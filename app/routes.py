import os
import shutil
from flask import render_template, request, flash, redirect, url_for, send_from_directory
from app import app, db
from app.models import Target, User, Seed, Crawler, ContentOwner, Job
from app.forms import LoginForm, AddTargetForm, AddSeedForm, AddCrawlerForm, AddUserForm, AddJobForm, AddContentOwnerForm, EditContentOwnerForm, CreateSIPForm, AddContentOwnerTargetForm
from flask_login import current_user, login_user, logout_user, login_required
from app.tasks import wget, create_sip, put_s3_task
from app.utils import bytes_to_human_readable, get_file_stats, convert_db_date_format
import requests
import json
from minio import Minio
import io


@app.route('/crawl/<id>')
def crawl(id):
    job = db.get_or_404(Job, id)
    task = wget.delay(id)
    job.task_id = task.id
    job.state = "crawling"
    db.session.commit()
    flash(f"Started crawl", "alert-success")
    return redirect(url_for('targetDetail',id=job.target_id))

@app.route('/create-ip/<id>', methods=['POST'])
def create_ip(id):
    job = db.get_or_404(Job, id)
    job.state = "creating sip"
    db.session.commit()
    create_sip_form = CreateSIPForm()
    SA = create_sip_form.SA.data
    username = current_user.username
    task = create_sip.delay(id, username, SA)
    return redirect(url_for('jobDetail', id=id))

@app.route('/put_s3/<job_id>/<obj_id>')
def put_s3(job_id, obj_id):
    task = put_s3_task.delay(obj_id)
    job = db.get_or_404(Job, job_id)
    job.state = "preserving"
    db.session.commit()

    return redirect(url_for('jobDetail', id=job_id))

@app.route('/check_task/<task_id>')
def check_task(task_id):
    task = wget.AsyncResult(task_id)
    if task.state == 'Crawling':
        return 'Crawling'
    elif task.state == 'SUCCESS':
        return 'Done'
    else:
        return task.state

@app.route('/check_job_state/<id>')
def check_job_state(id):
    job = db.get_or_404(Job,id)
    print(job.state)
    return str(job.state)


@app.route('/')
def index():
    loginform = LoginForm()
    target_count = Target.query.count()
    targets = db.session.query(Target).all()
    SIP_DIR = os.environ.get('SIP_DIR') or 'sips'
    sip_files = [file for file in os.listdir(SIP_DIR) if file.endswith('.tar')]
    return render_template('index.html', targets=targets, LoginForm=loginform, target_count=target_count, sip_files=sip_files)


@app.route('/targets', methods=['GET', 'POST'])
def targets():
    addtargetform = AddTargetForm()
    if request.method == 'POST':
        if request.form['type'] == 'addTarget':
            if addtargetform.validate_on_submit():
                target = Target(title=addtargetform.title.data, description=addtargetform.description.data, user_id=current_user.id)
                db.session.add(target)
                db.session.commit()
                return redirect(url_for('targets'))
        elif request.form['type'] == 'editTarget':
            if addtargetform.validate_on_submit():
                id = request.form.get('id')
                db.session.commit()
                return redirect(url_for('targets'))
    targets = db.session.query(Target).all()
    return render_template('targets.html', targets=targets, AddTargetForm=addtargetform, User=User)


@app.route('/targets/<id>',methods=['GET', 'POST'])
def targetDetail(id):
    addseedform = AddSeedForm()
    addjobform = AddJobForm()
    addcontentownertargetform = AddContentOwnerTargetForm()
    crawlers = db.session.query(Crawler).all()
    content_owners = db.session.query(ContentOwner).all()
    addjobform.crawler.choices = [(c.id, c.name) for c in crawlers]
    addcontentownertargetform.content_owner.choices = [(c.id, c.owner) for c in content_owners]
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

        elif request.form['type'] == 'addJob':
            job = Job(target_id=id, crawler_id=addjobform.crawler.data, state="prepared")
            db.session.add(job)
            db.session.commit()
            flash(f"Added job", "alert-success")
            return redirect(url_for('targetDetail', id=id))

        elif request.form['type'] == 'addContentOwnerTarget':
            print("hej")
            content_owner = db.get_or_404(ContentOwner, addcontentownertargetform.content_owner.data)
            print(content_owner)
            target = db.get_or_404(Target, id)
            target.content_owners.append(content_owner)
            db.session.commit()
            return redirect(url_for('targetDetail', id=id))

    target = db.get_or_404(Target, id)
    content_owners = target.content_owners
    seeds = Seed.query.filter_by(target_id=id).all()
    jobs = Job.query.filter_by(target_id=id).all()
    return render_template('target_detail.html', target=target, AddSeedForm=addseedform, AddJobForm=addjobform, seeds=seeds, jobs=jobs,
                           AddContentOwnerTargetForm=addcontentownertargetform, content_owners=content_owners)


@app.route('/deletetarget/<id>', methods=['GET'])
def deleteTarget(id):
    target = db.get_or_404(Target, id)
    db.session.delete(target)
    db.session.commit()
    return redirect(url_for('targets'))

@app.route('/job/<id>',methods=['GET', 'POST'])
def jobDetail(id):
    create_sip_form = CreateSIPForm()
    warcs = {}
    job = db.get_or_404(Job, id)
    WARC_DIR = os.environ.get('WARC_DIR') or 'warcs'
    SIP_DIR = os.environ.get('SIP_DIR') or 'sips'
    BASE_URL = os.environ.get('BASE_URL') or '127.0.0.1:5000'
    REPLAY_URL = os.environ.get('REPLAY_URL') or '127.0.0.1:5000'
    job_dir = os.path.join(WARC_DIR, job.task_id)
    warc_files = os.listdir(job_dir)
    sip_files = os.listdir(SIP_DIR)
    sip = None
    sip_size = None
    sip_created = None
    for file_name in sip_files:
        if os.path.splitext(os.path.basename(file_name))[0] == job.task_id and file_name.endswith(".tar"):
            sip = file_name
            sip_size = bytes_to_human_readable(os.path.getsize(os.path.join(SIP_DIR,sip)))
            sip_created = get_file_stats(os.path.join(SIP_DIR,sip))
    if not sip:
        essarch_api = os.environ.get('ESSARCH_API')
        essarch_token = os.environ.get('ESSARCH_TOKEN')
        headers = {
            "Accept": "application/json",
            "Authorization": essarch_token
        }

        r = requests.get(essarch_api+'/'+'submission-agreements', headers=headers)
        sas = json.loads(r.content)

        create_sip_form.SA.choices = [(c['id'], c['name']) for c in sas]

    for file_name in warc_files:
        file_path = os.path.join(job_dir, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.warc.gz') and not "meta.warc.gz" in file_name:
            file_size = os.path.getsize(file_path)
            print(f"{file_name}: {bytes_to_human_readable(file_size)}")
            warcs[file_name] = bytes_to_human_readable(file_size)

    return render_template('job_detail.html', job=job, warcs=warcs, job_dir=job_dir, base_url=BASE_URL,
                           replay_url=REPLAY_URL, sip=sip, sip_size=sip_size, sip_created=sip_created,CreateSIPForm=create_sip_form)

@app.route('/downloadWarc/<id>/<file>',methods=['GET', 'POST'])
def downloadWarc(id, file):
    job = db.get_or_404(Job, id)
    WARC_DIR = os.environ.get('WARC_DIRd') or 'C:/earkiv/wget-ui/warcs' #todo
    job_dir = os.path.join(WARC_DIR, job.task_id)
    return send_from_directory(job_dir, file, as_attachment=True)


@app.route('/deletejob/<id>', methods=['GET'])
def deleteJob(id):
    job = db.get_or_404(Job, id)
    WARC_DIR = os.environ.get('WARC_DIR') or 'warcs'
    if job.task_id:
        if os.path.exists(os.path.join(WARC_DIR,job.task_id)):
            shutil.rmtree(os.path.join(WARC_DIR,job.task_id))
    target_id = job.target_id
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('targetDetail', id=target_id))

@app.route('/deleteseed/<id>', methods=['GET'])
def deleteSeed(id):
    seed = db.get_or_404(Seed, id)
    target_id = seed.target_id
    db.session.delete(seed)
    db.session.commit()
    return redirect(url_for('targetDetail', id=target_id))


@app.route('/administration', methods=['GET', 'POST'])
def administration():
    addcrawlerform = AddCrawlerForm()
    adduserform = AddUserForm()
    addjobform = AddJobForm()
    addcontentownerform = AddContentOwnerForm()

    if request.method == 'POST':
        if request.form['type'] == 'addCrawler':
            if addcrawlerform.validate_on_submit():
                crawler = Crawler(name=addcrawlerform.name.data,crawler_type=addcrawlerform.crawler_type.data,
                                  cmd=addcrawlerform.cmd.data, settings=addcrawlerform.settings.data)
                db.session.add(crawler)
                db.session.commit()

                flash(f"Added Crawler '{addcrawlerform.name.data}'", "alert-success")
                return redirect(url_for('administration'))

        elif request.form['type'] == 'addUser':
            if adduserform.validate_on_submit():
                
                user = User(username=adduserform.username.data)
                user.set_password(adduserform.password1.data)
                user.check_password(adduserform.password2.data)
                db.session.add(user)
                db.session.commit()
                flash(f"Added User '{adduserform.username.data}'", "alert-success")
                return redirect(url_for('administration'))
            
        elif request.form['type'] == 'addJob':
            if addjobform.validate_on_submit():
                job = Job(crawler=addjobform.crawler.data)
                db.session.add(job)
                db.session.commit()
                flash(f"Added Job '{addjobform.crawler.data}'", "alert-success")
                return redirect(url_for('administration'))
            
        elif request.form['type'] == 'addContentOwner':
            if addcontentownerform.validate_on_submit():
                content_owner = ContentOwner(owner=addcontentownerform.owner.data, 
                                             reference_code=addcontentownerform.reference_code.data)
                db.session.add(content_owner)
                db.session.commit()
                flash(f"Added Owner '{addcontentownerform.owner.data}'", "alert-success")
                return redirect(url_for('administration'))
        
        elif request.form['type'] == 'editOwner': 
            if addcontentownerform.validate_on_submit():
                id = request.form.get('id')
                db.session.commit()
                return redirect(url_for('administration'))
                    
        elif request.form['type'] == 'editUser': 
            if adduserform.validate_on_submit():
                id = request.form.get('id') 
                db.session.commit()
                return redirect(url_for('administration'))
        
        elif request.form['type'] == 'editCrawler': 
            if addcrawlerform.validate_on_submit():
                id = request.form.get('id')
                db.session.commit()
                return redirect(url_for('administration'))
            
    crawlers = db.session.query(Crawler).all()
    users = db.session.query(User).all()
    jobs = db.session.query(Job).all()
    owners = db.session.query(ContentOwner).all()
    return render_template('administration.html',AddCrawlerForm=addcrawlerform,  AddUserForm=adduserform, AddJobForm=addjobform, AddContentOwnerForm=addcontentownerform, crawlers=crawlers, users=users, jobs=jobs, owners=owners)

@app.route('/deleteuser/<id>', methods=['GET'])
def deleteUser(id):
    user = db.get_or_404(User, id)
    db.session.delete(user)
    db.session.commit()
    flash("Deleted User", "alert-success")
    return redirect(url_for('administration'))

@app.route('/deletecrawler/<id>', methods=['GET'])
def deleteCrawler(id):
    crawler = db.get_or_404(Crawler, id)
    db.session.delete(crawler)
    db.session.commit()
    flash("Deleted Crawler {{crawler}}", "alert-success")
    return redirect(url_for('administration'))

@app.route('/deleteowner/<id>', methods=['GET'])
def deleteOwner(id):
    owner = db.get_or_404(ContentOwner, id)
    target_id = owner.target_id
    db.session.delete(owner)
    db.session.commit()
    return redirect(url_for('administration', id=target_id))

@app.route('/editseed/<id>', methods=['GET', 'POST'])
def editSeed(id):
    seed = Seed.query.get_or_404(id)
    form = AddSeedForm(request.form, obj=seed)
    if request.method == 'POST':
        if form.validate():
            form.populate_obj(seed)
            db.session.commit()
            return redirect(url_for('targets', id=id))
    return render_template('edit_seed_modal.html', form=form, seed=seed, id=id)

@app.route('/editowner/<id>', methods=['GET', 'POST'])
def editOwner(id):
    owner = ContentOwner.query.get_or_404(id)
    form = AddContentOwnerForm(request.form, obj=owner)
    if request.method == 'POST':
        if form.validate():
            form.populate_obj(owner)
            db.session.commit()
            flash(f"{owner.owner} updated!")
            return redirect(url_for('administration'))
    return render_template('edit_owner_modal.html', form=form, owner=owner, id=id)

@app.route('/edituser/<id>', methods=['GET', 'POST'])
def editUser(id):
    user = User.query.get_or_404(id)
    form = AddUserForm(request.form, obj=user)
    if request.method == 'POST':
        if form.validate():
            form.populate_obj(user)
            db.session.commit()
            flash(f"{user.username} updated!")
            return redirect(url_for('administration'))
    return render_template('edit_user_modal.html', form=form, user=user, id=id)

@app.route('/editcrawler/<id>', methods=['GET', 'POST'])
def editCrawler(id):
    crawler = Crawler.query.get_or_404(id)
    form = AddCrawlerForm(request.form, obj=crawler)
    if request.method == 'POST':
        if form.validate():
            form.populate_obj(crawler)
            db.session.commit()
            flash(f"{crawler.name} updated!")
            return redirect(url_for('administration'))
    return render_template('edit_crawler_modal.html', form=form, crawler=crawler, id=id)

@app.route('/edittarget/<id>', methods=['GET', 'POST'])
def editTarget(id):
    target = Target.query.get_or_404(id)
    form = AddTargetForm(request.form, obj=target)
    if request.method == 'POST':
        if form.validate():
            form.populate_obj(target)
            db.session.commit()
            flash(f"{target.title} updated!")
            return redirect(url_for('targets'))
    return render_template('edit_target_modal.html', form=form, target=target, id=id)

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