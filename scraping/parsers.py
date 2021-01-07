import logging
import random
import requests
from bs4 import BeautifulSoup

log = logging.getLogger('django')

HEADERS = [
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*'
    },

]


class ParserError(Exception):
    pass


class BaseParser:
    vacancies = []
    domain = ''

    def __init__(self, url, city_id, language_id):
        self.url = url
        self.city_id = city_id
        self.language_id = language_id

    @property
    def headers(self):
        return random.choice(HEADERS)

    def scrap(self):
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            self.parse(soup)
        else:
            raise ParserError(f'{self.url} - Page do not response')

    def parse(self, soup):
        raise NotImplementedError


class WorkUaParser(BaseParser):
    domain = 'https://www.work.ua'

    def parse(self, soup):
        main_div = soup.find('div', id='pjax-job-list')
        if not main_div:
            raise ParserError(f"{self.url} - Div with id 'pjax-job-list' does not exists")
        list_div = main_div.find_all('div', attrs={'class': 'job-link'})
        for div in list_div:
            _h2 = div.find('h2')
            self.vacancies.append({
                'title': _h2.text,
                'url': self.domain + _h2.a['href'],
                'description': div.p.text,
                'company': div.find('div', attrs={'class': 'add-top-xs'}).find('span').b.text,
                'city_id': self.city_id,
                'language_id': self.language_id,
            })


class RabotaUaParser(BaseParser):
    domain = 'https://rabota.ua'

    def parse(self, soup):
        table = soup.find('table', id='ctl00_content_vacancyList_gridList')
        if not table:
            raise ParserError(f"{self.url} - Table with id 'ctl00_content_vacancyList_gridList' does not exists")
        trs = table.find_all('tr', attrs={'id': True})
        for tr in trs:
            _card = tr.find('div', attrs={'class': 'card-body'})
            _main_info = _card.find('div', attrs={'class': 'common-info'})
            _title = _main_info.find('h2', attrs={'class': 'card-title'})
            try:
                self.vacancies.append({
                    'title': _title.a['title'],
                    'url': self.domain + _title.a['href'],
                    'description': _card.find('div', 'card-description').text,
                    'company': _main_info.find('p', attrs={'class': 'company-name'}).a.text,
                    'city_id': self.city_id,
                    'language_id': self.language_id,
                })
            except AttributeError as e:
                log.error(e)
                continue


class DouUaParser(BaseParser):
    domain = ''

    def parse(self, soup):
        main_div = soup.find('div', id='vacancyListId')
        if not main_div:
            raise ParserError(f"{self.url} - Div with id 'vacancyListId' does not exists")
        list_div = main_div.find_all('li', attrs={'class': 'l-vacancy'})
        for div in list_div:
            _title_div = div.find('div', attrs={'class': 'title'})
            _title_info = _title_div.find('a', attrs={'class': 'vt'})
            self.vacancies.append({
                'title': _title_info.text,
                'url': self.domain + _title_info['href'],
                'description': div.find('div', attrs={'class': 'sh-info'}).text,
                'company': _title_div.find('a', attrs={'class': 'company'}).text,
                'city_id': self.city_id,
                'language_id': self.language_id,
            })


class DjinniParser(BaseParser):
    domain = 'https://djinni.co/jobs2'

    def parse(self, soup):
        main_section = soup.find('section', attrs={'class': 'jobs-list-wrapper'})
        if not main_section:
            raise ParserError(f"{self.url} - section with class 'jobs-list-wrapper' does not exists")
        list_div = main_section.find_all('div', attrs={'class': 'wrapper'})
        for div in list_div:
            _title = div.find('p', attrs={'class': 'title'})
            self.vacancies.append({
                'title': _title.a.text,
                'url': self.domain + _title.a['href'],
                'description': div.find_all('p')[2].text,
                'company': _title.find('span', attrs={'class': 'company'}).text.lstrip('at '),
                'city_id': self.city_id,
                'language_id': self.language_id,
            })
