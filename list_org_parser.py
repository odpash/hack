import requests
from bs4 import BeautifulSoup


url = 'https://www.list-org.com/search'
list_org_base = 'https://www.list-org.com{}'
hdr = {'User-Agent': 'Mozilla/5.0'}


def get_link(company_name):
    query_result = requests.get(url, params={
        'type': 'all',
        'val': company_name
    }, headers=hdr).text
    bs = BeautifulSoup(query_result, features='lxml')
    first_label = bs.find('label')
    if first_label:
        href = first_label.find('a')
        if href:
            href = href.get('href')
            return list_org_base.format(href)
    return None


def get_contacts(link):
    if not link:
        return 'Не удалось найти организацию'

    txt = requests.get(link, headers=hdr).text
    bs = BeautifulSoup(txt, features='lxml')
    div = bs.find_all('div', class_='c2m')
    if not div:
        return 'Не удалось получить данные'
    div = div[1]
    if not div:
        return 'Не удалось получить контакты'
    div = div.text
    return div



def get_links(companies):
    return [get_link(company) for company in companies]


# print(get_contacts(get_link('Деулин Константин Николаевич (RU)')))

# print(get_links(['Закрытое акционерное общество Научно-производственное внедренческое предприятие "Турбокон" (RU)'] * 200))
# print(get_info('Закрытое акционерное общество Научно-производственное внедренческое предприятие "Турбокон" (RU)'))