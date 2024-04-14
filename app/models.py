from app import db
from flask import current_app
import uuid


class Target(db.Model):
    id = db.Column(db.String,primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(128), index=True)
    uri = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128), index=True)
    jobs = db.relationship('Job', backref='targets', lazy='dynamic')
    seeds = db.relationship('Seed', backref='targets', lazy='dynamic')
    content_owners = db.relationship('ContentOwner', backref='targets', lazy='dynamic')
    def __repr__(self):
        return self.title


class Crawler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    type = db.Column(db.String(128))
    cmd = db.Column(db.String(128), index=True)
    settings = db.Column(db.Text, index=True)
    jobs = db.relationship('Job', backref='crawlers', lazy='dynamic')
    def __repr__(self):
        return self.name


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
    crawler_id = db.Column(db.Integer, db.ForeignKey('crawler.id'))
    result = db.Column(db.String(128))

    def __repr__(self):
        return self.id


class ContentOwner(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(128), index=True)
    reference_code = db.Column(db.String(128), index=True)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))
    def __repr__(self):
        return self.name


class Seed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), index=True)
    depth = db.Column(db.Integer, index=True)
    exclude_patterns = db.Column(db.String(128), index=True)
    include_patterns = db.Column(db.String(128), index=True)
    domains = db.Column(db.String(128), index=True)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))
    def __repr__(self):
        return self.url


# class Users():
#     id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
#     first_name = db.Column(db.String(128), index=True)
#     last_name = db.Column(db.String(128), index=True)
#     email = db.Column(db.String(128), index=True)
#     password = db.Column(db.String(128), index=True)


