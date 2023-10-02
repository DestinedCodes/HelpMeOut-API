from flask import jsonify, request, Response, send_file, redirect
import nanoid
from datetime import datetime
from helpmeout import app, db
from helpmeout.models.recordings import Recordings
import json
import io
import os
import tempfile
from moviepy.editor import VideoFileClip, concatenate_videoclips


# An endpoint to start a new recording
@app.route('/api/start-recording', methods=['POST'])
def start_screen_record():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    id = nanoid.generate(size=10)
    title = id
    time = datetime.now()

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
    if recording.video:
        recording.video = video
        # recording.video = append_video(recording.video, video)
    else:
        recording.video = video
    db.session.commit()
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
    if recording.video:
        recording.video = video
        # recording.video = append_video(recording.video, video)
    else:
        recording.video = video
    db.session.commit()
    return redirect(f"https://helpmeout-vid.netlify.app/")


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
    if not recording.video:
        return jsonify({'error': 'recording is empty'}), 404
    if not recording.transcript:
        # use the video to generate a transcript using whispr.ai
        pass
    return Response(recording.video, mimetype='video/mp4')


# An endpoint to get the transcript of a recording
@app.route('/api/recording/transcript/<id>', methods=['GET'])
def get_transcript(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    if not recording.transcript:
        if not recording.video:
            return jsonify({'error': 'recording is empty'}), 404
        # use the video to generate a transcript using whispr.ai
        pass
    return Response(recording.transcript, mimetype='text/plain')


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
            "time": recording.time,
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
        "time": recording.time,
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
        "time": recording.time,
        'transcript_url': f"{request.url_root}api/recording/transcript/{recording.id}"
        } for recording in recordings]
    json_response = json.dumps(response, indent=2)
    return Response(json_response, mimetype='application/json'), 200


# An endpoint to delete a recording
@app.route('/api/recording/<id>', methods=['DELETE'])
def delete_recording(id):
    recording = Recordings.query.filter_by(id=id).first()
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


def append_video(existing_video_data, new_video_data):
    # Create temporary files for the video clips
    with tempfile.NamedTemporaryFile(delete=False) as existing_temp_file:
        existing_temp_file.write(existing_video_data)
        existing_temp_filepath = existing_temp_file.name

    with tempfile.NamedTemporaryFile(delete=False) as new_temp_file:
        new_temp_file.write(new_video_data)
        new_temp_filepath = new_temp_file.name

    # Create video clips from the temporary files
    existing_clip = VideoFileClip(existing_temp_filepath)
    new_clip = VideoFileClip(new_temp_filepath)

    # Concatenate the video clips
    final_clip = concatenate_videoclips([existing_clip, new_clip])

    # Save the concateted video clip to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as final_temp_file:
        final_clip.write_videofile(final_temp_file.name, codec='libx264')
        final_temp_filepath = final_temp_file.name

    # Read the temporary file and return the data
    final_video_data = open(final_temp_filepath, 'rb').read()

    # Delete the temporary files
    os.remove(existing_temp_filepath)
    os.remove(new_temp_filepath)
    os.remove(final_temp_filepath)

    return final_video_data
