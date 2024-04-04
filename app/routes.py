from flask import render_template, session, request, send_file, flash, redirect, url_for, jsonify
from app import app, db
from app.models import Target

@app.route('/')
def index():
    targets = db.session.query(Target).all()
    return render_template('index.html', targets=targets)

@app.route('/target/<id>')
def target(id):
    target = db.session.query(Target).filter(id==id).first()
    return render_template('target.html', target=target)
