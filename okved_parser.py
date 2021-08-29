import requests
from bs4 import BeautifulSoup


url = 'https://companies.rbc.ru/okved/'

query_result = requests.get(url).text
bs = BeautifulSoup(query_result, features='lxml')

okved = []

for okved_group in bs.find_all('details', class_='okved__details'):
    okved_main = okved_group.find('a', class_='okved__item')
    okved_main_code = okved_main.find('span', class_='okved__item-code').text
    okved_main_title = okved_main.text[2:]
    okved.append((okved_main_code, okved_main_title))

    okved_links = okved_group.find_all('a', class_='okved__link')
    for okved_link in okved_links:
        okved_link_code = okved_link.find('span', class_='okved__item-code').text
        okved_link_title = okved_link.text.replace(okved_link_code, '')
        okved.append((okved_link_code, okved_link_title))

for a in okved:
    print(*a, sep='\t')
