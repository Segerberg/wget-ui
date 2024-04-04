from app import db
from flask import current_app
import uuid

class Target(db.Model):
    id = db.Column(db.String,primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(128), index=True)
    uri = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128), index=True)
    jobs = db.relationship('Job', backref='target', lazy='dynamic')

    def __repr__(self):
        return self.title


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))
    # software
    # settings
    result = db.Column(db.String(128), index=True)

    def __repr__(self):
        return self.id

