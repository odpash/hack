import requests
from bs4 import BeautifulSoup
from settings import notificate_admin


def make_request(url: str):
    try:
        query_result = requests.get(url).text
    except:
        return 'Request sending error!'
    try:
        return BeautifulSoup(query_result, features='lxml')
    except:
        return 'Parse error, check features!'


def main(query: str):
    links = []
    site_code = make_request(query)
    if site_code == 'Request sending error!' or site_code == 'Parse error, check features!':
        notificate_admin(site_code)
        return {'status': 'our_error', 'desc': site_code}

    pages_container = site_code.find_all('a', {'class': 'pagination__item'})
    pages_count = int(pages_container[-2].text) if len(pages_container) > 1 and pages_container[-2].text.isdigit() else 1

    for page in range(1, pages_count + 1):
        site_code = make_request('https://companies.rbc.ru/search/?query=' + f'&page={page}')
        if site_code == 'Request sending error!' or site_code == 'Parse error, check features!':
            notificate_admin(site_code)
            continue

        cards_table = site_code.find('main', {'class': 'company-detail-layout__content'})
        for card in cards_table.find_all('div', {'class': 'company-card info-card'}):
            element = card.find('a', {'class': 'company-name-highlight'})
            if element.has_attr('href'):
                links.append(element.get('href'))
        if 'По вашему запросу ничего не найдено' in str(site_code):
            return {'status': 'external_error', 'desc': 'По вашему запросу ничего не найдено.'}
    return {'status': 'ok', 'desc': links}
