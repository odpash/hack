import requests
from bs4 import BeautifulSoup


def make_request(url: str):
    try:
        query_result = requests.get('https://companies.rbc.ru/search/?query=' + url).text
    except:
        pass
        return 'error'

    return BeautifulSoup(query_result, features='lxml')


def find_pages_by_query(query: str):
    links = []
    site_code = make_request(query)
    if site_code == 'error':
        return []
    try:
        pages_count = int(site_code.find_all('a', {'class': 'pagination__item'})[-2].text)
    except:
        pages_count = 1
    for page in range(1, pages_count + 1):
        site_code = make_request(query + f'&page={page}')
        if site_code == 'error':
            continue
        cards_table = site_code.find('main', {'class': 'company-detail-layout__content'})
        is_page_with_info = False
        for card in cards_table.find_all('div', {'class': 'company-card info-card'}):
            is_page_with_info = True
            links.append(card.find('a', {'class': 'company-name-highlight'}).get('href'))
        if 'По вашему запросу ничего не найдено' not in cards_table.text and is_page_with_info is False:
            pass
    return links


def try_exc(site_code, tag1, tag2, value):
    try:
        return site_code.find(tag1, {tag2: value}).text
    except:
        return 'None'


def get_info_from_container(site_code, container_name):
    if container_name != 'Социальные сети':
        res = {}
    else:
        res = []
    try:
        profile_table = site_code.find_all('div', {'class': 'info-card company-detail__block'})
        for c in profile_table:
            if c.find('a', {'class': 'info-card__title'}).text == container_name:
                profile_table = c
                break
        profile_table = profile_table.find('div', {'class': 'info-cell__container'})
    except:
        pass
        return res

    for param in profile_table.find_all('div', {'class': 'info-cell'}):
        try:

            if container_name == 'Социальные сети':
                res.append(param.find('a', {'class': 'info-cell__text company-social__link'}).get('href'))
                continue

            param_name = param.find('span', {'class': 'info-cell__small'}).text
            param_value = param.find_all('span', {'class': 'info-cell__text'})
            if param_name == 'Телефон':
                res[param_name] = param.find('a', {'class': 'info-cell__text'}).get('href').replace('tel:', '')
                continue
            if param_name == 'Сайт':
                res[param_name] = param.find('a', {'class': 'info-cell__text'}).text
                continue
            if param_name == 'E-mail':
                res[param_name] = param.find('a', {'class': 'info-cell__text'}).get('href').replace('mailto:', '')
                continue
            if len(param_value) > 1:
                for i in range(len(param_value)):
                    param_value[i] = param_value[i].text.strip().replace('\xa0', '')
            else:
                param_value = param_value[0].text.strip().replace('\xa0', '')
            res[param_name] = param_value
        except:
            pass
    return res


def parse_page(query: str):
    site_code = BeautifulSoup(requests.get(query).text, features='lxml')
    agency_info = try_exc(site_code, 'a', 'id', 'analytics-no-representative-js')
    try:
        pdf_link = 'https://companies.rbc.ru/company-pdf/' + str(site_code).split('href="/company-pdf/')[1].split('/')[
            0]
    except:
        pdf_link = 'None'
    company_status = try_exc(site_code, 'span', 'class', 'company-status-badge')
    try:
        update_info_time = site_code.find('span', {'class': 'company-headline__status'}).text.replace('Обновлено ', '')
    except:
        update_info_time = 'None'
    company_name = try_exc(site_code, 'h1', 'class', 'company-headline__title')
    company_type = try_exc(site_code, 'span', 'class', 'company-headline__opf')

    desc = []
    for info in site_code.find_all('p', {'class': 'info-card__text'}):
        try:
            desc.append(info.text.replace('\xa0', ''))
        except:
            pass
    profile = get_info_from_container(site_code, 'Профиль')
    contacts = get_info_from_container(site_code, 'Контакты')
    social_networks = get_info_from_container(site_code, 'Социальные сети')
    financianal_data = get_info_from_container(site_code, 'Реквизиты')
    leaders = get_info_from_container(site_code, 'Руководители')
    founders = get_info_from_container(site_code, 'Учредители')
    okved = site_code.find('div', {'id': 'okved'})
    activity = []
    try:
        for block in okved.find_all('div', {'class': 'company-okved__block'}):
            try:
                code = block.find('span', {'class': 'company-okved__code'}).text.strip()
                information = block.find('span', {'class': 'info-cell__text'}).text.strip()
                activity.append([code, information])
            except:
                pass
    except:
        for i in site_code.find_all('div', {'class': 'info-card company-detail__block'}):
            if i.find('a', {'class': 'info-card__title'}).text == 'Виды деятельности':
                okved = i
                break
        try:
            for block in okved.find_all('div', {'class': 'info-cell company-okved__cell'}):
                try:
                    code = block.find('span', {'class': 'company-okved__code'}).text.strip()
                    try:
                        information = block.find('span', {'class': 'company-okved__label'}).text.strip()
                    except:
                        information = block.find('span', {'class': 'info-cell__text'}).text.strip()
                    activity.append([code, information])
                except:
                    pass
        except:
            pass

    summary_information = {'agency_info': agency_info,
                           'pdf_link': pdf_link,
                           'company_status': company_status,
                           'update_info_time': update_info_time,
                           'company_name': company_name,
                           'company_type': company_type,
                           'desc': desc,
                           'profile': profile,
                           'contacts': contacts,
                           'social_networks': social_networks,
                           'financianal_data': financianal_data,
                           'leaders': leaders,
                           'founders': founders,
                           'activity': activity
                           }
    return summary_information


def main():
    query = 'Нефть'
    pages = find_pages_by_query(query)[:20]
    result = []
    for i in pages:
        print(i)
        result.append(parse_page(i))
    print(*result, sep='\n')


if __name__ == '__main__':
    main()