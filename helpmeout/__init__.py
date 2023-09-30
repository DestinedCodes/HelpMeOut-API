from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recordings.db'

db.init_app(app)

from .models.users import Users
from .models.recordings import Recordings
from .routes import users, recordings
