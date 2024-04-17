# Celery tasks goes here

# CreateSIP
    # Including METS, PREMIS and CITS for Webarchives and package to a ZIP

# PUT to S3
# PUSH to Wayback
# RunCrawl
# Upload seeds config file (csv)

from app import celery
from app.models import Target
import time
@celery.task(bind=True)
def example_task(self):
    for i in range(10):
        print(i)
        time.sleep(1)