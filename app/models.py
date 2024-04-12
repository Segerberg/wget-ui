from app import db
from flask import current_app
import uuid

class Target(db.Model):
    #id = db.Column(db.String,primary_key=True, default=lambda: str(uuid.uuid4()))
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), index=True)
    uri = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128), index=True)
    jobs = db.relationship('Job', backref='target', lazy='dynamic')

    def __repr__(self):
        return self.title


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    storagepath = db.Column(db.String(100))
    resultOutcome = db.Column(db.String(100))
    stats = db.Column(db.String(100))
    QA = db.Column(db.String(100))
    schedule = db.Column(db.String(100))
    startDateTime = db.Column(db.DateTime)
    EndDateTime = db.Column(db.DateTime)

    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))
    target = db.relationship('Targets', backref=db.backref('jobs', lazy=True))
    crawler_id = db.Column(db.Integer, db.ForeignKey('crawler.id'))
    crawler = db.relationship('Crawler', backref=db.backref('jobs', lazy=True))
    # software
    # settings
    result = db.Column(db.String(128), index=True)

    def __repr__(self):
        return self.id
    
class ContentOwners():
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(128), index=True)
    reference_code = db.Column(db.String(128), index=True)

class Seeds():
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), index=True)
    depth = db.Column(db.Integer, index=True)
    exclude_patterns = db.Column(db.String(128), index=True)
    include_patterns = db.Column(db.String(128), index=True)
    domains = db.Column(db.String(128), index=True)

    target_id = db.Column(db.Integer, db.ForeignKey('targets.id'))
    target = db.relationship('Targets', backref=db.backref('seeds', lazy=True))
    
class Users():
    id = db.Column(db.String,primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(128), index=True)
    last_name = db.Column(db.String(128), index=True)
    email = db.Column(db.String(128), index=True)
    password = db.Column(db.String(128), index=True)

class Crawler():
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    type = db.Column(db.String(128))
    cmd = db.Column(db.String(128), index=True)
    settings = db.Column(db.Text, index=True)
