from flask import jsonify, request, Response, send_file, redirect
import nanoid
from datetime import datetime
from helpmeout import app, db
from helpmeout.models.recordings import Recordings
import json
import io
import os
import tempfile
from deepgram import Deepgram
from moviepy.editor import VideoFileClip, concatenate_videoclips
import asyncio

DEEPGRAM_API_KEY = '32192faf34b41b9c0a289c4aa81b403171b0cdb1'

# Initialize Deepgram


# An endpoint to start a new recording
@app.route('/api/start-recording', methods=['POST'])
def start_screen_record():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    id = nanoid.generate(size=10)
    title = id
    time = datetime.now()
    os.makedirs(f"helpmeout/static/{id}")

    new_recording = Recordings(id=id, user_id=user_id, time=time, title=title)
    db.session.add(new_recording)
    db.session.commit()

    response = {
            'message': 'recording started successfully',
            'recording_id': id,
            'recording_url': f"{request.url_root}api/recording/{id}"
            }

    json_response = json.dumps(response, indent=2)

    return Response(json_response, mimetype='application/json'), 201


# An endpoint to add video in chunks to a recording
@app.route('/api/recording/<id>', methods=['POST'])
def add_video_chunk(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    video = request.files.get('video').read()
    if not video:
        return jsonify({'error': 'video(file) is required'}), 400
    # if {id}.mp4 exists then return video compiled already
    if os.path.exists(f"helpmeout/static/{id}.mp4"):
        return jsonify({'error': 'video compiled already'}), 400
    # save the video chunk in the directory with name as an index if video chunk as they are being added
    with open(f"helpmeout/static/{id}/{len(os.listdir(f'helpmeout/static/{id}'))}.mp4", 'wb') as f:
        f.write(video)

    response = {
            'message': 'video added successfully',
            'recording_id': id,
            'recording_url': f"{request.url_root}api/recording/{id}"
            }
    json_response = json.dumps(response, indent=2)

    return Response(json_response, mimetype='application/json'), 201


# An endpoint to stop a recording
@app.route('/api/stop-recording/<id>', methods=['POST'])
def stop_screen_record(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    video = request.files.get('video').read()
    if not video:
        return jsonify({'error': 'video(file) is required'}), 400
    # if {id}.mp4 exists then return video compiled already
    if os.path.exists(f"helpmeout/static/{id}.mp4"):
        return jsonify({'error': 'video compiled already'}), 400
    # save the video chunk in the directory with name as an index if video chunk as they are being added
    with open(f"helpmeout/static/{id}/{len(os.listdir(f'helpmeout/static/{id}'))}.mp4", 'wb') as f:
        f.write(video)

    response = {
            'message': 'video added successfully',
            'recording_id': id,
            'recording_url': f"{request.url_root}api/recording/{id}"
            }
    json_response = json.dumps(response, indent=2)

    return RedirectResponse(url=f"{request.url_root}api/recording/{id}")


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


# An endpoint to get the video of a recording
@app.route('/api/recording/<id>', methods=['GET'])
def get_video(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    if os.path.exists(f"helpmeout/static/{id}"):
        if len(os.listdir(f"helpmeout/static/{id}")) == 0:
            return jsonify({'error': 'recording is empty'}), 404
        # append all the video chunks in the directory
        recording.video = append_video(id)

    # open the video file
    video_file = open(f"helpmeout/static/{id}.mp4", 'rb').read()

    # return the video file
    return Response(video_file, mimetype='video/mp4'), 200

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
            recording.transcript = await deepgram.transcription.prerecorded(source, PARAMS)

    # Return the transcript as JSON
    return jsonify(recording.transcript)

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


def append_video(recording_id):
    # get the directory name
    dir_name = f"helpmeout/static/{recording_id}"

    clips = []
    # Create video clips for all files in the directory
    for filename in os.listdir(dir_name):
        clips.append(VideoFileClip(f"{dir_name}/{filename}"))

    # Concatenate the video clips
    if len(clips) == 1:
        final_clip = clips[0]
    else:
        final_clip = concatenate_videoclips(clips)

    # save the concatenated video to a file
    final_clip.write_videofile(f"helpmeout/static/{recording_id}.mp4", codec="libx264")

    # delete the directory forcefully
    os.system(f"rm -rf {dir_name}")

    return final_clip

