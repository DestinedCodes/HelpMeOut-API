from flask import jsonify, request
from . import app, db
from .models import User, ScreenRecord

# Add a new user
@app.route('/user', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(**data)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(data)

# Get a user by email
@app.route('/user/<email>', methods=['GET'])
def get_user(email):
    user = User.query.get(email)
    return jsonify(user)

# Add a new screen record
@app.route('/screen_record', methods=['POST'])
def add_screen_record():
    data = request.get_json()
    new_screen_record = ScreenRecord(**data)
    db.session.add(new_screen_record)
    db.session.commit()
    return jsonify(data)

# Get all screen records
@app.route('/screen_record', methods=['GET'])
def get_screen_records():
    screen_records = ScreenRecord.query.all()
    return jsonify(screen_records)

# Get a screen record by id
@app.route('/screen_record/<id>', methods=['GET'])
def get_screen_record(id):
    screen_record = ScreenRecord.query.get(id)
    return jsonify(screen_record)

# Update a screen record by id
@app.route('/screen_record/<id>', methods=['PUT'])
def update_screen_record(id):
    data = request.get_json()
    screen_record = ScreenRecord.query.get(id)
    screen_record.__dict__.update(**data)
    db.session.commit()
    return jsonify(screen_record)

# Delete a screen record by id
@app.route('/screen_record/<id>', methods=['DELETE'])
def delete_screen_record(id):
    screen_record = ScreenRecord.query.get(id)
    db.session.delete(screen_record)
    db.session.commit()
    return jsonify(screen_record)
