from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
import yaml


swagger = Swagger()


db = SQLAlchemy()

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recordings.db'

db.init_app(app)

swagger_config = yaml.load(open('swagger.yaml'), Loader=yaml.FullLoader)
Swagger(app, template=swagger_config)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

from .models.users import Users
from .models.recordings import Recordings
from .routes import recordings
