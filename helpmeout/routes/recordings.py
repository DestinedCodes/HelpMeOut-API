from flask import jsonify, request, Response, send_file
import nanoid
import subprocess
import base64
from io import BytesIO
from datetime import datetime
from helpmeout import app, db
from helpmeout.models.recordings import Recordings

# Initialize a new screen recording
@app.route('/api/recording', methods=['POST'])
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

    return jsonify({'recording_url': f"{request.url_root}api/recording/{id}"}), 201

# An endpoint to add video in chunks to a recording
@app.route('/api/recording/<id>', methods=['POST'])
def add_video_chunk(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    try:
        video = request.json.get('video')
        if not video:
            return jsonify({'error': 'video is required'}), 400
    except:
        return jsonify({'error': 'invalid video'}), 400
    if recording.video:
        recording.video = recording.video + video
    else:
        recording.video = video
    db.session.commit()
    return jsonify({'message': 'video added successfully'}), 201

# An endpoint to get the video of a recording
@app.route('/api/recording/<id>', methods=['GET'])
def get_video(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    if not recording.video:
        return jsonify({'error': 'recording is empty'}), 404
    # Decode the base64 video data
    try:
        video_data = base64.b64decode(recording.video)
    except Exception as e:
        return jsonify({'error': 'error decoding video'}), 500
    
    # Return the video as a response
    return Response(video_data, mimetype='video/mp4')

# An endpoint to get all recordings of a user
@app.route('/api/recording/user/<user_id>', methods=['GET'])
def get_user_recordings(user_id):
    recordings = Recordings.query.filter_by(user_id=user_id).all()
    if not recordings:
        return jsonify({'error': 'no recordings found'}), 404
    return jsonifty([{ 'title': recording.title, 'id': recording.id, 'user_id': recording.user_id, 'time': recording.time } for recording in recordings]), 200

# An endpoint to get all recordings
@app.route('/api/recording', methods=['GET'])
def get_all_recordings():
    recordings = Recordings.query.all()
    if not recordings:
        return jsonify({'error': 'no recordings found'}), 404
    return jsonify([{ 'title': recording.title, 'id': recording.id, 'user_id': recording.user_id, 'time': recording.time } for recording in recordings]), 200

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
    return jsonify({'message': 'title updated successfully'}), 200

# An endpoint to delete a recording
@app.route('/api/recording/<id>', methods=['DELETE'])
def delete_recording(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    db.session.delete(recording)
    db.session.commit()
    return jsonify({'message': 'recording deleted successfully'}), 200
