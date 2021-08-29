import json
import re
import urllib.parse as urlparse
import random

import requests

NUM = 10

patent_url = 'https://yandex.ru/patents/api/search?'
patent_vars = {
    'text': '',
    'template': '%request%+<<+(s_19_country:RU+|+s_19_country:SU)+<<+s_22_date:>=20100101+<<+('
                'i_doc_type:1+|+i_doc_type:2)',
    'p': 0,
    'how': 'rlv',
    'numdoc': NUM
}

patent_api_url = 'https://yandex.ru/patents/api/search?text={}&template=%25request%25+%3C' \
                 '%3C+%28s_19_country%3ARU+%7C+s_19_country%3ASU%29+%3C%3C+s_22_date%3A%3E%3D20100101+%3C%3C' \
                 '+%28i_doc_type%3A1+%7C+i_doc_type%3A2%29&p=0&how=rlv&numdoc={}'

listorg_url = 'https://www.list-org.com/search?'
listorg_vars = {
    'type': 'all',
    'val': ''
}


def get_patent_api_link(name):
    return patent_api_url.format(name, random.randint(170, 550))


def get_listorg_link(name):
    listorg_vars['val'] = name
    return listorg_url + urlparse.urlencode(listorg_vars)

compare = {
    'i_22_year': 'year',
    'z_ru_54_name': 'title',
    'z_ru_abstract': 'description',
    'z_ru_72_author': 'author',
    'z_ru_73_owner': 'owner'
}


def get_patents(name):
    try:
        results = []
        data = json.loads(requests.get(get_patent_api_link(name)).text)['Grouping'][0]['Group']
        for info in data:
            patent = {
                'link': '',
                'title': '',
                'description': '',
                'author': '',
                'owner': '',
                'year': ''
            }
            archive_info = info['Document'][0]['ArchiveInfo']
            patent['link'] = archive_info['Url']
            for attr in archive_info['GtaRelatedAttribute']:
                for key in compare:
                    if attr['Key'] == key:
                        patent[compare[key]] = attr['Value']


            # Заголовок капсом
            patent['title'] = patent['title'].upper()
            # Замена картинок на [img]
            patent['description'] = re.sub(r'<img.*">', '[img]', patent['description'])
            # Замена компаний на ссылки в list-org
            # patent['owner'] = '<br>'.join([f'<a href="{get_listorg_link(face)}">{face}</a>' for face in patent['owner'].split('<br>')])

            results.append([patent['link'], patent['title'], patent['description'], patent['author'], patent['owner'], patent['year']])

        return results
    except KeyError:
        print('KeyError')
        return []
    except Exception as e:
        print(e)
        return []
