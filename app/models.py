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

class Crawler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    type = db.Column(db.String(128))
    cmd = db.Column(db.String(128), index=True)
    settings = db.Column(db.Text, index=True)

    def __repr__(self):
        return self.id

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    storage_path = db.Column(db.String(100))
    result_outcome = db.Column(db.String(100))
    stats = db.Column(db.String(100))
    QA = db.Column(db.String(100))
    schedule = db.Column(db.String(100))
    start_date_time = db.Column(db.DateTime)
    end_date_time = db.Column(db.DateTime)

    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))
    target = db.relationship('Targets', backref=db.backref('jobs', lazy=True))
    crawler_id = db.Column(db.Integer, db.ForeignKey('crawler.id'))
    crawler = db.relationship('Crawlers', backref=db.backref('jobs', lazy=True))
    # software
    # settings
    result = db.Column(db.String(128), index=True)

    def __repr__(self):
        return self.id
    
class ContentOwners(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(128), index=True)
    reference_code = db.Column(db.String(128), index=True)

    def __repr__(self):
        return self.id

class Seeds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), index=True)
    depth = db.Column(db.Integer, index=True)
    exclude_patterns = db.Column(db.String(128), index=True)
    include_patterns = db.Column(db.String(128), index=True)
    domains = db.Column(db.String(128), index=True)

    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))
    target = db.relationship('Target', backref=db.backref('seeds', lazy=True))

    def __repr__(self):
        return self.id

class Users(db.Model):
    id = db.Column(db.String,primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(128), index=True)
    last_name = db.Column(db.String(128), index=True)
    email = db.Column(db.String(128), index=True)
    password = db.Column(db.String(128), index=True)

    def __repr__(self):
        return self.id


