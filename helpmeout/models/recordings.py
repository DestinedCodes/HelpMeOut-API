from helpmeout import db
import nanoid

class Recordings(db.Model):
    __tablename__ = "recordings"

    id = db.Column(db.String(60), primary_key=True, unique=True, nullable=False, default = nanoid.generate())
    title = db.Column(db.String(120), nullable=False)
    video = db.Column(db.String, nullable=True)
    time = db.Column(db.Date(), nullable=False)
    user_id  = db.Column(db.String(60), db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return "Id: {}, Title: {}, Time: {}, User_id: {}".format(
            self.id, self.title, self.time, self.user_id
        )

    def format(self):
        return {
            "id": self.id,
            "title": self.title,
            "date": self.time,
            "user_id": self.user_id
        }

