from collections import defaultdict
from datetime import date

from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model

from scripts import setup_django
setup_django()  # NOTE: Django setup for using app models

from scraping.models import Vacancy, Url
from work_scraping.settings import EMAIL_HOST_USER

today = date.today()
empty = f'No vacancies found on { today }'
subject = text_content = f'Vacancy mailing on { today }'

User = get_user_model()
query = User.objects.filter(is_subscribed=True).values('city', 'language', 'email')
users = defaultdict(list)
params = {'city_id__in': set(), 'language_id__in': set()}
for user in query:
    if user['city'] and user['language']:
        users[(user['city'], user['language'])].append(user['email'])
        params['city_id__in'].add(user['city'])
        params['language_id__in'].add(user['language'])

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

    url_html = ''
    _urls = Url.objects.all().values('city', 'language')
    existing_urls = [(url['city'], url['language']) for url in _urls]
    for pair in users.keys():
        if pair not in existing_urls:
            url_html += f"<p>For city: {pair[0]} and language: {pair[1]} is not exists urls</p>"
    if url_html:
        msg = EmailMultiAlternatives('Urls is not exists', 'Urls is not exists', EMAIL_HOST_USER, [EMAIL_HOST_USER])
        msg.attach_alternative(url_html, "text/html")
        msg.send()
