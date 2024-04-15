from flask import render_template, session, request, send_file, flash, redirect, url_for, jsonify
from app import app, db
from app.models import Target, User, Seed
from app.forms import LoginForm, AddTargetForm, AddSeedForm
from flask_login import current_user, login_user, logout_user, login_required


@app.route('/')
def index():
    loginform = LoginForm()
    target_count = Target.query.count()
    targets = db.session.query(Target).all()
    return render_template('index.html', targets=targets, LoginForm=loginform, target_count=target_count)


@app.route('/targets', methods=['GET', 'POST'])
def targets():
    addtargetform = AddTargetForm()
    if addtargetform.validate_on_submit():
        target = Target(title=addtargetform.title.data, description=addtargetform.description.data, user_id=current_user.id)
        db.session.add(target)
        db.session.commit()
        return redirect(url_for('targets'))
    targets = db.session.query(Target).all()
    return render_template('targets.html', targets=targets, AddTargetForm=addtargetform, User=User)


@app.route('/targets/<id>',methods=['GET', 'POST'])
def targetDetail(id):
    addseedform = AddSeedForm()
    if request.method == 'POST':
        if request.form['type'] == 'addSeed':
            if addseedform.validate_on_submit():
                seed = Seed(url=addseedform.url.data, depth=addseedform.depth.data,
                            exclude_patterns=addseedform.exclude_patterns.data,
                            include_patterns=addseedform.include_patterns.data, domains=addseedform.domains.data,
                            target_id=id)
                db.session.add(seed)
                db.session.commit()
                return redirect(url_for('targetDetail',id=id))

    target = db.get_or_404(Target, id)
    seeds = Seed.query.filter_by(target_id=id).all()
    return render_template('target_detail.html', target=target, AddSeedForm=addseedform, seeds=seeds)


@app.route('/deletetarget/<id>',methods=['GET'])
def deleteTarget(id):
    target = db.get_or_404(Target, id)
    db.session.delete(target)
    db.session.commit()
    return redirect(url_for('targets'))


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