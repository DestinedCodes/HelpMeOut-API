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

    return jsonify({'id': id}), 201

# An endpoint to add video in chunks to a recording
@app.route('/api/recording/<id>', methods=['POST'])
def add_video_chunk(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    video = request.files.get('video').read()
    if not video:
        return jsonify({'error': 'video is required'}), 400
    if recording.video:
        recording.video = recording.video + video
    else:
        recording.video = video
    db.session.commit()
    return jsonify({'message': 'video added'}), 201

# An endpoint to get the video of a recording
@app.route('/api/recording/<id>', methods=['GET'])
def get_video(id):
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    return send_file(BytesIO(recording.video), download_name=f'{recording.title}.webm', as_attachment=True)


