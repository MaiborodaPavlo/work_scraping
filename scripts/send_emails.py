from collections import defaultdict
from datetime import date

from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model

from scripts import setup_django
setup_django()  # NOTE: Django setup for using app models

from scraping.models import Vacancy
from work_scraping.settings import EMAIL_HOST_USER

today = date.today()
empty = f'No vacancies found on { today }'
subject = text_content = f'Vacancy mailing on { today }'

User = get_user_model()
query = User.objects.filter(is_subscribed=True).values('city', 'language', 'email')
users = defaultdict(list)
params = {'city_id__in': set(), 'language_id__in': set()}
for user in query:
    if user['city']:
        params['city_id__in'].add(user['city'])
    if user['language']:
        params['language_id__in'].add(user['language'])
    users[(user['city'], user['language'])].append(user['email'])

if users:
    query = Vacancy.objects.filter(**params, created=today).values()
    vacancies = defaultdict(list)
    for vacancy in query:
        vacancies[(vacancy['city_id'], vacancy['language_id'])].append(vacancy)
    
    for key, emails in users.items():
        rows = vacancies.get(key, [])
        html = ''
        for row in rows:
            html += f"<h4><a href='{ row['url'] }'>{ row['title'] }</a></h4>"
            html += f"<p>{ row['description'] }</p>"
            html += f"<b>{ row['company'] }</b><br><hr>"
        for email in emails:
            msg = EmailMultiAlternatives(subject, text_content, EMAIL_HOST_USER, [email])
            msg.attach_alternative(html or empty, "text/html")
            msg.send()
