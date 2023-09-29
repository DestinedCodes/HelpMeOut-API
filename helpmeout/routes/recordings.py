from flask import jsonify, request
from helpmeout import app, db
from helpmeout.models.recordings import Recordings

# Add a new screen record
@app.route('/api/recording', methods=['POST'])
def add_screen_record():
    data = request.get_json()
    new_recording = Recordings(**data)
    db.session.add(new_recording)
    db.session.commit()
    return jsonify(data)

