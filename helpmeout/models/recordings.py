from helpmeout import db
import nanoid

class Recordings(db.Model):
    __tablename__ = "recordings"

    id = db.Column(db.String(60), primary_key=True, unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    video = db.Column(db.BLOB, nullable=True)
    transcript = db.Column(db.String, nullable=True)
    time = db.Column(db.Date(), nullable=False)
    user_id  = db.Column(db.String(60), db.ForeignKey("users.id"), nullable=False)
