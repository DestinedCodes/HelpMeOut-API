from flask_login import UserMixin
from . import db

# Model for the table ti atore the scren record data
class ScreenRecord(db.Model):
    __tablename__ = 'screen_record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    screen_record = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"ScreenRecord('{self.screen_record}', '{self.date}')"

# Model for the table to store the user data
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    screen_records = db.relationship('ScreenRecord', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

