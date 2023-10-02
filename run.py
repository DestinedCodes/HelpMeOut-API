from helpmeout import app, db
from flask_cors import CORS

CORS(app)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()

