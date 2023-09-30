from flask import jsonify, request, send_file
import nanoid
import subprocess
from io import BytesIO
from datetime import datetime
from helpmeout import app, db
from helpmeout.models.recordings import Recordings
from moviepy.editor import VideoFileClip, concatenate_videoclips, clips_array

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

    return jsonify({'recording_id': id}), 201

# An endpoint to add video in chunks to a recording
@app.route('/api/recording/<id>', methods=['POST'])
def add_video_chunk(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    try:
        video = request.files.get('video').read()
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
    return send_file(BytesIO(recording.video), download_name=f'{recording.title}.webm', as_attachment=True)


# An endpoint to get all recordings of a user
@app.route('/api/recording/user/<user_id>', methods=['GET'])
def get_user_recordings(user_id):
    recordings = Recordings.query.filter_by(user_id=user_id).all()
    if not recordings:
        return jsonify({'error': 'no recordings found'}), 404
    return jsonify([recording.serialize() for recording in recordings]), 200

# An endpoint to get all recordings
@app.route('/api/recording', methods=['GET'])
def get_all_recordings():
    recordings = Recordings.query.all()
    if not recordings:
        return jsonify({'error': 'no recordings found'}), 404
    # return title, id, user_id, time of each recording in JSON format
    return jsonify([{ 'title': recording.title, 'id': recording.id, 'user_id': recording.user_id, 'time': recording.time } for recording in recordings]), 200
