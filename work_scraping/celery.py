import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_scraping.settings')

# Get the base REDIS URL, default to redis' default
BASE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

app = Celery('work_scraping')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.broker_url = BASE_REDIS_URL
