import os
import sys

import django


def setup_django():
    project_path = os.path.dirname(os.path.abspath('manage.py'))
    sys.path.append(project_path)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'work_scraping.settings'
    django.setup()
