from flask import render_template, session, request, send_file, flash, redirect, url_for, jsonify
from app import app, db
from app.models import Target

@app.route('/')
def index():
    targets = db.session.query(Target).all()
    return render_template('index.html', targets=targets)

@app.route('/target/<int:id>')
def target(id):
    target = db.session.query(Target).filter(Target.id==id).first()
    
    return render_template('target.html', target=target)

@app.route('/addTarget', methods=['GET', 'POST'])
def addTarget():
    #db.session.delete(Target.query(id='d447cb62-2187-4dce-b8c7-896945d44d0e'))
    #db.session.commit()
    if request.method == 'POST':
        title = request.form['title']
        uri = request.form['uri']
        description = request.form['description']
        new_target = Target(title=title, uri=uri, description=description)
        db.session.add(new_target)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('addtarget.html')