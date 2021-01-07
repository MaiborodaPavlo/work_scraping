web: gunicorn work_scraping.wsgi
worker: celery -A work-scraping worker --loglevel=info --concurrency=4
