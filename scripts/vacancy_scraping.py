import asyncio
import logging
from datetime import date

from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db import DatabaseError

from scripts import setup_django
setup_django()  # NOTE: Django setup for using app models

from scraping.models import Vacancy, Url
from scraping.parsers import (
    WorkUaParser,
    RabotaUaParser,
    DouUaParser,
    DjinniParser,
    ParserError,
)
from work_scraping.settings import EMAIL_HOST_USER

log = logging.getLogger('django')
parsers_mapping = {
    'work': WorkUaParser,
    'rabota': RabotaUaParser,
    'dou': DouUaParser,
    'djinni': DjinniParser,
}
vacancies = []
parsing_errors = []


def get_settings():
    User = get_user_model()
    qs = User.objects\
        .filter(is_subscribed=True)\
        .only('city', 'language')\
        .values()
    return set((q['city_id'], q['language_id']) for q in qs)


def get_urls():
    qs = Url.objects.all().values()
    prepared_data = {(q['city_id'], q['language_id']): q['data'] for q in qs}
    return [
        {
            'city': setting[0],
            'language': setting[1],
            'url_data': prepared_data[setting]
        } for setting in get_settings()
        if setting in prepared_data
    ]


async def main(values):
    parser, url, city, language = values
    try:
        await loop.run_in_executor(None, parser(url, city, language).scrap)
        vacancies.extend(parser.vacancies)
    except ParserError as e:
        parsing_errors.append(e)
        log.error(e)

prepared_tasks = [
    (parser, data['url_data'][key], data['city'], data['language'])
    for data in get_urls() if data['url_data']
    for key, parser in parsers_mapping.items()
]
loop = asyncio.get_event_loop()
tasks = asyncio.wait([loop.create_task(main(f)) for f in prepared_tasks])
loop.run_until_complete(tasks)
loop.close()

if vacancies:
    for vacancy in vacancies:
        v = Vacancy(**vacancy)
        try:
            v.save()
        except DatabaseError as e:
            log.error(e)

if parsing_errors:
    msg = EmailMultiAlternatives(
        f'Parsing Errors on { date.today() }',
        'Parsing Errors',
        EMAIL_HOST_USER,
        [EMAIL_HOST_USER]
    )
    html = ''
    for error in parsing_errors:
        html += f'<p>{ error }</p>'
    msg.attach_alternative(html, "text/html")
    msg.send()
