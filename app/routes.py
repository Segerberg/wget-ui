from flask import render_template, session, request, send_file, flash, redirect, url_for, jsonify
from app import app, db
from app.models import Target, User
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required


@app.route('/')
def index():
    loginform = LoginForm()
    targets = db.session.query(Target).all()
    return render_template('index.html', targets=targets, LoginForm=loginform)


@app.route('/targets')
def target(id):
    targets = db.session.query(Target).all()
    return render_template('targets.html', targets=targets)


@app.route('/target/<id>')
def targetDetail(id):
    target = db.session.query(Target).filter(id==id).first()
    return render_template('target_detail.html', target=target)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get("next")
            return redirect(next or url_for('index'))
        flash("Login failed",  "alert-danger")
    return render_template('index.html', LoginForm=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("logged out!", "alert-success")
    return redirect(url_for('index'))