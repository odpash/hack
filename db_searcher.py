import json
import csv
import re
import urllib.parse as urlparse

from search_op import get_companies_by_query, get_patents_by_query, categories, classes, subclasses


with open('rbc_results0.json', encoding='utf8') as file:
    company_base = json.loads(file.read())
    print(len(company_base))


url = 'https://www.list-org.com/search?'
vars = {
    'type': 'all',
    'val': ''
}


def get_link(name):
    vars['val'] = name
    return url + urlparse.urlencode(vars)


with open('patent_base.csv', encoding='utf8') as file:
    patent_base = []
    for row in csv.reader(file, delimiter=';'):
        # Название капсом
        row[1] = row[1].upper()
        # Замена картинок на [img]
        row[2] = re.sub(r'<img.*">', '[img]', row[2])
        # Замена компаний на ссылки в list-org
        row[4] = '<br>'.join([f'<a href="{get_link(face)}">{face}</a>' for face in row[4].split('<br>')])
        patent_base.append(row)
    patent_base.pop(0)


is_active = lambda x: x['company_status'].lower() == 'действует'
priority_sort = lambda x: len(x['contacts']) == 0


def search(query, only_active=True, category=None, class_=None, subclass=None, science=None, niokr=None,
           investment=None, fund=None, registration=(None, None), capital=(None, None)):
    companies = get_companies_by_query(query, company_base)
    if only_active:
        companies = list(filter(is_active, companies))
    return sorted(companies, key=priority_sort)


def search_patents(query):
    patents = get_patents_by_query(query, patent_base)
    return patents


# if __name__ == '__main__':
#     while True:
#         cmd = input()
#         result = get_companies_by_query(cmd, base)
#         print(list(map(lambda x: x['company_name'], result)))
