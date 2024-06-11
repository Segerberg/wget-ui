from app import celery
from app import db, __version__

from app.models import Target, User, Seed, Crawler, Job
import ast
import subprocess
from urllib.parse import urlparse
import os
import json
from datetime import datetime, timezone
from app.utils import get_file_stats, calculate_md5, create_xml, create_tar, create_uuid
import shutil
# CreateSIP
# Including METS, PREMIS and CITS for Webarchives and package to a ZIP

# PUT to S3
# PUSH to Wayback
# RunCrawl
# Upload seeds config file (csv)

@celery.task(bind=True)
def wget(self, id):
    WARC_DIR = os.environ.get('WARC_DIR') or 'warcs'
    job = db.get_or_404(Job, id)
    crawler = db.get_or_404(Crawler, job.crawler_id)
    settings = ast.literal_eval(crawler.settings)
    command = ['wget'] # todo
    command.extend(settings)
    job_dir = os.path.join(WARC_DIR, job.task_id)
    if not os.path.exists(job_dir):
        os.makedirs(job_dir)


    seeds = Seed.query.filter_by(target_id=job.target_id).all()
    job.startDateTime = datetime.utcnow()
    db.session.commit()
    for seed in seeds:
        hostname = urlparse(seed.url).hostname.replace('.','-')



        seed_setting = ['--level', str(seed.depth)]
        seed_setting.append(f'--domains={seed.domains}')
        seed_setting.append (f'"--reject-regex {seed.exclude_patterns}"')
        warc_file = [f"--warc-file={job_dir}/{job.task_id}", "--warc-max-size=1G"]
        command.extend(warc_file)
        command.extend(seed_setting)
        command.append(seed.url)

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.update_state(state='Crawling', meta={'message': 'Crawl started'})

        try:
            for line in iter(process.stdout.readline, ''):
                print(line)
        except: # todo catch error
            pass
    job.EndDateTime = datetime.utcnow()
    db.session.commit()


@celery.task(bind=True)
def create_sip(self, id, username):
    SIP_DIR = os.environ.get('SIP_DIR') or 'sips'
    if not os.path.exists(SIP_DIR):
        os.makedirs(SIP_DIR)
    profile = open("app/profiles/GU-websites-1.0/profile.json")
    profile_data = json.loads(profile.read())
    creation_datetime = datetime.now(tz=timezone.utc)
    creation_datetime = creation_datetime.astimezone()  # Convert to local timezone
    creation_date_str = creation_datetime.isoformat()
    job = db.get_or_404(Job, id)
    obj_id = job.task_id
    target = db.get_or_404(Target,job.target_id)
    content_files = []
    schema_files = []
    WARC_DIR = os.environ.get('WARC_DIR') or 'warcs'
    job_dir = os.path.join(WARC_DIR, job.task_id)
    # CREATE STRUCTURE
    for k,v  in profile_data['structure'].items():
        if v['type'] == 'folder':
            folder_path = os.path.join(job_dir,k)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

    warc_files = os.listdir(job_dir)

    for file_name in warc_files:
        file_path = os.path.join(job_dir, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.warc.gz'):
            file_size = os.path.getsize(file_path)
            file_creation = get_file_stats(os.path.join(job_dir,file_name))
            content_files.append({"name":file_name,"size":file_size,"creation":file_creation, "uuid":create_uuid(),"checksum":calculate_md5(os.path.join(job_dir,file_name))})
            shutil.move(file_path, os.path.join(job_dir,'content',file_name))

    for schema in profile_data['schemas']:
        file_path = os.path.join('app/profiles/GU-websites-1.0/',schema['location'])
        if os.path.isfile(file_path) and os.path.basename(file_path).endswith('.xsd'):
            file_size = os.path.getsize(file_path)
            file_creation = get_file_stats(file_path)
            schema_files.append(
                {"name": os.path.basename(file_path), "size": file_size, "creation": file_creation, "uuid": create_uuid(),
                 "checksum": calculate_md5(file_path)})

            shutil.copy(file_path, os.path.join(job_dir,'metadata', os.path.basename(file_path)))


    data = {"content":content_files, "schemas":schema_files, "ip_creation":creation_date_str, "obj_id":str(obj_id), "title":target.title,
            "software_version":__version__, "current_user":username, "job_start":job.startDateTime, "job_end":job.EndDateTime}

    ipenvents_filepath = os.path.join(job_dir, 'ipevents.xml')
    with open(ipenvents_filepath, 'w', encoding='utf-8') as f:
        ipevents = create_xml(target, data, 'profiles/GU-websites-1.0/templates/ipevents.xml')
        f.write(ipevents)

    premis_filepath = os.path.join(job_dir, 'metadata', 'premis.xml')
    with open(premis_filepath, 'w', encoding='utf-8') as f:
        premis = create_xml(target, data, 'profiles/GU-websites-1.0/templates/premis.xml')
        f.write(premis)

    with open(os.path.join(job_dir, 'mets.xml'), 'w', encoding='utf-8') as f:
        ipevents_file_size = os.path.getsize(ipenvents_filepath)
        ipevents_file_creation = get_file_stats(ipenvents_filepath)
        ipevents_checksum = calculate_md5(ipenvents_filepath)
        premis_file_size = os.path.getsize(ipenvents_filepath)
        premis_file_creation = get_file_stats(ipenvents_filepath)
        premis_checksum = calculate_md5(ipenvents_filepath)

        data["premis_file"] = {"size": premis_file_size, "creation": premis_file_creation,
                               "checksum": premis_checksum, "uuid": create_uuid()}

        data["ipevents_file"] = {"size": ipevents_file_size, "creation": ipevents_file_creation,
                                 "checksum": ipevents_checksum, "uuid": create_uuid()}
        mets = create_xml(target, data, 'profiles/GU-websites-1.0/templates/sip-mets.xml')
        f.write(mets)

    if not os.path.isfile(os.path.join(SIP_DIR,f"{obj_id}.tar")):
        create_tar(job_dir, os.path.join(SIP_DIR,f"{obj_id}.tar"))
        #shutil.rmtree(job_dir)