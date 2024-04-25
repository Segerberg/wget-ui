from app import celery
from app import db
from app.models import Target, User, Seed, Crawler, Job
import ast
import subprocess
from datetime import datetime
from urllib.parse import urlparse
# CreateSIP
# Including METS, PREMIS and CITS for Webarchives and package to a ZIP

# PUT to S3
# PUSH to Wayback
# RunCrawl
# Upload seeds config file (csv)

@celery.task(bind=True)
def wget(self, id):
    job = db.get_or_404(Job, id)
    crawler = db.get_or_404(Crawler, job.crawler_id)
    settings = ast.literal_eval(crawler.settings)
    command = ['wget'] # todo
    command.extend(settings)


    seeds = Seed.query.filter_by(target_id=job.target_id).all()
    job.startDateTime = datetime.utcnow()
    db.session.commit()
    for seed in seeds:

        seed_setting = ['--level', str(seed.depth)]
        seed_setting.append(f'--domains={seed.domains}')
        warc_file = [f"--warc-file={job.target_id}_{job.id}"]
        command.extend(warc_file)
        command.extend(seed_setting)
        command.append(seed.url)
        print(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        for line in iter(process.stdout.readline, ''):
            print(line)