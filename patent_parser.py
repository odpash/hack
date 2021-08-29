from multiprocessing.spawn import freeze_support

import requests
import json
import time
import multiprocessing


TOTAL = 10_000 # 261608
NUM = 500
url = 'https://yandex.ru/patents/api/search?text=&template=%25request%25+%3C%3C+%28s_19_country%3ARU+%7C+s_19_country' \
      '%3ASU%29+%3C%3C+s_22_date%3A%3E%3D20150101+%3C%3C+%28i_doc_type%3A1+%7C+i_doc_type%3A2%29&p={' \
      '}&how=rlv&numdoc=' + str(NUM)

referer = 'https://yandex.ru/patents?dco=RU&dco=SU&dfr=2015.01.01&dl=ru&dt=0&dty=1&dty=2&s=0&sp={}&st=0&spp=' + str(NUM)

compare = {
    'i_22_year': 'year',
    'z_ru_54_name': 'title',
    'z_ru_abstract': 'description',
    'z_ru_72_author': 'author',
    'z_ru_73_owner': 'owner'
}

file = open('patent_result2.csv', 'a', encoding='utf8')
header = 'link\ttitle\tdescription\tauthor\towner\tyear\n'
file.write(header)


def parse_info(n: int):
    try:
        headers = {
            'referer': referer.format(max(0, n - 1))
        }
        data = json.loads(requests.get(url.format(n), params=headers).text)['Grouping'][0]['Group']
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

            file.write(f"{patent['link']}\t{patent['title']}\t{patent['description']}"
                                 f"\t{patent['author']}\t{patent['owner']}\t{patent['year']}\n")
    except KeyError:
        print('KeyError', url.format(n))
    except Exception:
        print('ConnectionAbortedError', url.format(n))

if __name__ == '__main__':
    file.write(header)
    for n in range(TOTAL // NUM + 1):
        start = time.time()
        parse_info(n)
        print(f'PAGE {n}', time.time() - start)
    # with multiprocessing.Pool() as p:
    #     p.map(parse_info, range(TOTAL // NUM + 1))
    file.close()
