import requests
from bs4 import BeautifulSoup
from settings import notificate_admin
import json


def parse_activity(site_code):
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
            try:
                if i.find('a', {'class': 'info-card__title'}).text == 'Виды деятельности':
                    okved = i
                    break
            except:
                pass
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
    return activity


def make_request(url: str):
    try:
        query_result = requests.get(url).text
    except:
        return 'Request sending error!'
    try:
        return BeautifulSoup(query_result, features='lxml')
    except:
        return 'Parse error, check features!'


def try_exc(site_code, tag1, tag2, value, param_name, url):
    try:
        if param_name == 'pdf_link':
            return 'https://companies.rbc.ru/company-pdf/' + str(site_code).split('href="/company-pdf/')[1].split('/')[
                0]
        elif param_name == 'update_info_time':
            return site_code.find('span', {'class': 'company-headline__status'}).text.replace('Обновлено ', '')
        return site_code.find(tag1, {tag2: value}).text
    except:
        notificate_admin(param_name + '\n' + url)
        return 'None'


def parse_container_type_one(code):
    try:
        code = code.find('div', {'class': 'info-cell__container'}).find_all('div', {'class': 'info-cell'})
        result = []
        for info_cell in code:
            param_name = info_cell.find('span', {'class': 'info-cell__small'}).text
            param_values = info_cell.find_all('span', {'class': 'info-cell__text'})
            copy_param_values = info_cell.find_all('a', {'class': 'info-cell__text'})
            is_null = True
            for i in range(len(param_values)):
                param_values[i] = param_values[i].text.strip()
                if param_values[i] != '':
                    is_null = False
            if is_null:
                for i in range(len(copy_param_values)):
                    if copy_param_values[i].has_attr('href'):
                        copy_param_values[i] = copy_param_values[i].get('href')
                result.append({param_name: copy_param_values})
            else:
                result.append({param_name: param_values})
    except:
        return ''
    return result


def parse_container_type_two(code):
    code = code.find('div', {'class': 'info-cell__container'}).find_all('div', {'class': 'info-cell'})
    result = []
    for info_cell in code:
        param_name = info_cell.find('a', {'class': 'info-cell__text company-social__link'}).text
        param_values = info_cell.find('a', {'class': 'info-cell__text company-social__link'}).get('href')
        result.append({param_name: param_values})
    return result


def parse_container(site_code, container_name, url):
    containers = site_code.find_all('div', {'class': 'info-card company-detail__block'})
    for container in containers:
        try:
            container_name_v = container.find('a', {'class': 'info-card__title'})

            if container_name_v.text == container_name:
                if container_name_v.text != 'Социальные сети':
                    return parse_container_type_one(container)
                else:
                    return parse_container_type_two(container)
        except:
            pass

    notificate_admin('Containers not found!\n' + url + 'Container name: ' + container_name)
    return []


def main(url: str):
    site_code = make_request(url)
    if site_code == 'Request sending error!' or site_code == 'Parse error, check features!':
        notificate_admin(site_code)
        return {'status': 'our_error', 'desc': site_code}
    pdf_link = try_exc(site_code, '', '', '', 'pdf_link', url)
    company_status = try_exc(site_code, 'span', 'class', 'company-status-badge', 'company_status', url)
    company_name = try_exc(site_code, 'h1', 'class', 'company-headline__title', 'company_name', url)
    company_type = try_exc(site_code, 'span', 'class', 'company-headline__opf', 'company_type', url)
    update_info_time = try_exc(site_code, '', '', '', 'update_info_time', url)
    profile = parse_container(site_code, 'Профиль', url)
    contacts = parse_container(site_code, 'Контакты', url)
    social_networks = parse_container(site_code, 'Социальные сети', url)
    requisites = parse_container(site_code, 'Реквизиты', url)
    leaders = parse_container(site_code, 'Руководители', url)
    founders = parse_container(site_code, 'Учредители', url)
    activity = parse_activity(site_code)
    desc = ''

    summary_information = {
        'company_name': company_name,
        'pdf_link': pdf_link,
        'company_status': company_status,
        'update_info_time': update_info_time,
        'company_type': company_type,
        'desc': desc,
        'profile': profile,
        'contacts': contacts,
        'social_networks': social_networks,
        'requisites': requisites,
        'leaders': leaders,
        'founders': founders,
        'activity': activity
    }
    return summary_information


