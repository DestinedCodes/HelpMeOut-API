import nanoid
from helpmeout import db

class Recordings(db.Model):
    __tablename__ = "recordings"

    id = db.Column(db.String(60), primary_key=True, unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    transcript = db.Column(db.String, nullable=True)
    time = db.Column(db.Date(), nullable=False)
    user_id  = db.Column(db.String(60), nullable=False)
