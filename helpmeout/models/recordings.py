from helpmeout import db
from uuid import uuid4

class Recordings(db.Model):
    __tablename__ = "recordings"

    id = db.Column(db.String(60), primary_key=True, unique=True, nullable=False, default = uuid4().hex)
    title = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date(), nullable=False)
    user_id  = db.Column(db.String(60), db.ForeignKey("users.id"), nullable=False)


    def __repr__(self):
        return "Id: {}, Title: {}, Date: {}, User_id: {}".format(
            self.id, self.title, self.date, self.user_id
        )
    
    def insert(self):
        """Insert the current object into the database"""
        db.session.add(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "user_id": self.user_id
        }
