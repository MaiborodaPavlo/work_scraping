web: gunicorn work_scraping.wsgi
worker: celery -A work_scraping worker --loglevel=info --concurrency=4
