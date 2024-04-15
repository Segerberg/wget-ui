from app import db
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import uuid
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    targets = db.relationship('Target', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Target(db.Model):
    #id = db.Column(db.String,primary_key=True, default=lambda: str(uuid.uuid4()))
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
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



