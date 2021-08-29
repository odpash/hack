import requests
import bs4
import json


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'referer': 'https://www.list-org.com/search?type=all&val=9103018662',
    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
}


def search_by_fio(fio):
    try:
        r = requests.get('https://www.list-org.com/search?type=fio&val=' + fio, headers=headers)
        r = 'https://www.list-org.com' + bs4.BeautifulSoup(r.text, features='lxml').find('div', {'class': 'org_list'}).find(
            'a').get('href')
        return r
    except:
        return ''


def parse_standart_table(r, idx):
    try:
        main_info_table = r.find_all('table', {'class': 'tt'})[idx].find_all('td')
        sp = []
        for i in range(0, len(main_info_table) - 1, 2):
            try:
                sp.append({'param_name': main_info_table[i].text, 'param_value': main_info_table[i + 1].text})
            except:
                pass
    except:
        sp = []
    return sp


def parse_vertical_table(r, idx):
    try:
        main_info_table = r.find_all('table', {'class': 'tt'})[idx].find_all('tr')
        keys = []
        res = []
        for i in range(len(main_info_table)):
            try:

                v = main_info_table[i].find_all('td')
                for z in range(len(v)):
                    v[z] = v[z].text
                if (i == 0 and idx != 5) or (i == 1 and idx == 5):
                    keys = list(v)
                else:
                    if i == 0 and idx == 5:
                        continue
                    m_r = []
                    if '...показать исторические данные...' in v:
                        continue
                    for k in range(len(keys)):
                        try:
                            if 'Посмотреть отчетность за ' in v[k]:
                                continue
                            m_r.append({'param_name': keys[k], 'param_value': v[k]})
                        except:
                            pass
                    if len(m_r) > 0:
                        res.append(m_r)
            except:
                pass
    except:
        res = []
    return res


def parse_company(link):
    r = requests.get(link, headers=headers)
    r = bs4.BeautifulSoup(r.text, features='lxml')
    d = {}
    d['main_info'] = parse_standart_table(r, 0)
    d['deyatelnost'] = parse_standart_table(r, 1)
    d['ychred'] = parse_vertical_table(r, 2)
    d['+-'] = parse_vertical_table(r, 3)
    d['nalog'] = parse_vertical_table(r, 4)
    d['all_finance'] = parse_vertical_table(r, 5)
    d['lics'] = parse_vertical_table(r, 6)
    i = r.find_all('p')
    other_params = []
    for x in i:
        try:
            x = x.text.split(': ')
            other_params.append({'param_name': x[0], 'param_value': x[1]})
        except:
            pass
    d['other_params'] = other_params
    return d

print(parse_company('https://www.list-org.com/man/6845608'))