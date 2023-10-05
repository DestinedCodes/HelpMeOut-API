from flask import jsonify, request, Response, redirect
import nanoid
import string
import json
import io
import os
import asyncio
from deepgram import Deepgram
from moviepy.editor import VideoFileClip, concatenate_videoclips
from datetime import datetime
from helpmeout import app, db
from helpmeout.models.recordings import Recordings
from helpmeout.utils import merge_video


@app.route('/api/start-recording', methods=['POST'])
def start_screen_record():
    # Get user_id from the JSON request
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    # Generate recording details
    recording_id = nanoid.generate(size=10, alphabet=string.ascii_letters)
    title = f"Recording {recording_id}"
    time = datetime.now()

    # Create a directory for the recording
    os.makedirs(f"helpmeout/static/{recording_id}")

    # Create a new recording entry in the database
    new_recording = Recordings(id=recording_id, user_id=user_id, time=time, title=title)
    db.session.add(new_recording)
    db.session.commit()

    response = {
        'message': 'Recording started successfully',
        'recording_id': recording_id,
        'recording_url': f"{request.url_root}api/recording/{recording_id}"
    }

    return jsonify(response), 201


# An endpoint to add video in chunks to a recording
@app.route('/api/recording/<id>', methods=['POST'])
def add_video_chunk(id):
    # Check if the recording with the given ID exists
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'Recording not found'}), 404

    # Check if 'video' file is present in the request
    video_file = request.files.get('video')
    if not video_file:
        return jsonify({'error': 'Video (file) is required'}), 400

    # Check if {id}.mp4 already exists, indicating the video is compiled
    if os.path.exists(f"helpmeout/static/{id}.mp4"):
        return jsonify({'error': 'Video compiled already'}), 400

    # Save the video chunk in the directory with an index as the filename
    video_chunk_path = os.path.join(f"helpmeout/static/{id}", f"{len(os.listdir(f'helpmeout/static/{id}'))}.mp4")
    with open(video_chunk_path, 'wb') as f:
        f.write(video_file.read())

    response = {
        'message': 'Video chunk added successfully',
        'recording_id': id,
        'recording_url': f"{request.url_root}api/recording/{id}"
    }

    return jsonify(response), 201


# An endpoint to stop a recording
@app.route('/api/stop-recording/<id>', methods=['POST'])
def stop_screen_record(id):
    # Add the last video chunk to the recording
    response = add_video_chunk(id)

    # Check if error is in response
    if 'error' in response.json:
        return response

    # Get the Video Ready
    response = get_video(id)

    # Check if error is in response
    if 'error' in response.json:
        return response

    # Get the Transcript Ready
    get_transcript(id)

    # Check if error is in response
    if 'error' in response.json:
        return response

    return redirect("https://helpmeout-vid.netlify.app/videodetails", code=302)


# An endpoint to get the video of a recording
@app.route('/api/recording/<id>', methods=['GET'])
def get_video(id):
    # Check if the recording with the given ID exists
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404

    # Check if the videos are still in chunks
    if os.path.exists(f"helpmeout/static/{id}"):
        # Check if no chunk has been added yet
        if len(os.listdir(f"helpmeout/static/{id}")) == 0:
            return jsonify({'error': 'recording is empty'}), 404

        # Check the recording_status
        if recording.recording_status == 'not_started':
            recording.recording_status = 'processing'
            db.session.commit()
            job = executor.submit(merge_video, id)

        # Check if the video is still being compiled
        if recording.recording_status == 'processing':
            return Recording.response('Video is still being compiled'), 200

    # Check if the video file exists
    video_path = f"helpmeout/static/{id}.mp4"
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video file not found'}), 500

    # Stream the video file
    return send_file(video_path, mimetype='video/mp4', as_attachment=True), 200

# An endpoint to get the transcript of a recording
@app.route('/api/recording/transcript/<id>', methods=['GET'])
async def get_transcript(id):
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    if not recording.transcript:
        # if {id}.mp4 does not exist then return recording is empty
        if not os.path.exists(f"helpmeout/static/{id}.mp4"):
            return jsonify({'error': 'recording not ready'}), 404

        # Convert video to audio
        audio = VideoFileClip(f"helpmeout/static/{id}.mp4").audio
        audio_file_path = f"helpmeout/static/{id}.mp3"
        audio.write_audiofile(audio_file_path)

        # Transcribe audio using Deepgram
        PARAMS = {'punctuate': True, 'tier': 'enhanced'}
        with open(audio_file_path, 'rb') as audio_file:
            source = {'buffer': audio_file, 'mimetype': 'audio/mp3'}
            data = await deepgram.transcription.prerecorded(source, PARAMS)
            recording.transcript = json.dumps(data['results']['channels'][0]['alternatives'][0], indent=2)
            db.session.commit()

    # Return the transcript as JSON
    return Response(recording.transcript, mimetype='application/json'), 200

# An endpoint to get details of a recording
@app.route('/api/recording/details/<id>', methods=['GET'])
def get_recording_details(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    response = {
            'title': recording.title,
            'recording_id': id,
            'recording_url': f"{request.url_root}api/recording/{id}",
            "creator_id": recording.user_id,
            "time": recording.time.isoformat(),
            'transcript_url': f"{request.url_root}api/recording/transcript/{id}"
            }
    json_response = json.dumps(response, indent=2)
    return Response(json_response, mimetype='application/json'), 200


# An endpoint to update the title of a recording
@app.route('/api/recording/<id>', methods=['PUT'])
def update_recording_title(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    title = request.json.get('title')
    if not title:
        return jsonify({'error': 'title is required'}), 400
    recording.title = title
    db.session.commit()
    response = {
            'message': 'title updated successfully',
            'recording_id': id,
            'recording_url': f"{request.url_root}api/recording/{id}"
            }
    json_response = json.dumps(response, indent=2)
    return Response(json_response, mimetype='application/json'), 200

# An endpoint to get all recordings of a user
@app.route('/api/recording/user/<user_id>', methods=['GET'])
def get_user_recordings(user_id):
    recordings = Recordings.query.filter_by(user_id=user_id).all()
    if not recordings:
        return jsonify({'error': 'no recordings found'}), 404
    response = [{
        'title': recording.title,
        'recording_id': recording.id,
        'recording_url': f"{request.url_root}api/recording/{recording.id}",
        "creator_id": recording.user_id,
        "time": recording.time.isoformat(),
        'transcript_url': f"{request.url_root}api/recording/transcript/{recording.id}"
        } for recording in recordings]
    json_response = json.dumps(response, indent=2)
    return Response(json_response, mimetype='application/json'), 200


# An endpoint to get all recordings
@app.route('/api/recording', methods=['GET'])
def get_all_recordings():
    recordings = Recordings.query.all()
    if not recordings:
        return jsonify({'error': 'no recordings found'}), 404
    response = [{
        'title': recording.title,
        'recording_id': recording.id,
        'recording_url': f"{request.url_root}api/recording/{recording.id}",
        "creator_id": recording.user_id,
        "time": recording.time.isoformat(),
        'transcript_url': f"{request.url_root}api/recording/transcript/{recording.id}"
        } for recording in recordings]
    json_response = json.dumps(response, indent=2)
    return Response(json_response, mimetype='application/json'), 200


# An endpoint to delete a recording
@app.route('/api/recording/<id>', methods=['DELETE'])
def delete_recording(id):
    recording = Recordings.query.filter_by(id=id).first()
    # delete the directory forcefully
    os.system(f"rm -rf helpmeout/static/{id}")
    # delete the video file
    os.system(f"rm -rf helpmeout/static/{id}.mp4")
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    db.session.delete(recording)
    db.session.commit()
    response = {
            'message': 'recording deleted successfully',
            'recording_id': id
            }
    json_response = json.dumps(response, indent=2)
    return Response(json_response, mimetype='application/json'), 200

