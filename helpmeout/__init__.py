from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
import yaml
import os

# Create the Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

# Initialize CORS
CORS(app)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Swagger
swagger = Swagger(app, template=yaml.load(open('swagger.yaml'), Loader=yaml.FullLoader))

# Import models and routes
from .models.recordings import Recordings
from .routes import recordings

