import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_scraping.settings')

app = Celery('work_scraping')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
