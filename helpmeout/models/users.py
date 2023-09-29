from helpmeout import db
from uuid import uuid4

class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(60), primary_key=True, unique=True, nullable=False, default = uuid4().hex)
    name = db.Column(db.String(60), nullable=False)
    screen_records = db.relationship('Recordings', backref='author', lazy=True)

    def __repr__(self):
        return "Id: {}, Name: {}".format(
            self.id, self.name
        )
    
    def insert(self):
        """Insert the current object into the database"""
        db.session.add(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "name": self.name
        }
