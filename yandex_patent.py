import requests
import multiprocessing
import datetime

compare = {
    'i_22_year': 'year',
    'z_ru_54_name': 'title',
    'z_ru_abstract': 'description',
    'z_ru_72_author': 'author',
    'z_ru_73_owner': 'owner'
}


def search(url):
    try:
        data = requests.get(url).json()['Grouping'][0]['Group']
        patents = []
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
            patents.append(f"{patent['link']}\t{patent['title']}\t{patent['description']}"
                           f"\t{patent['author']}\t{patent['owner']}\t{patent['year']}\n")

        return patents
    except:
        print(f'ERROR: {url}')
        return 'no info'


def main():
    fl = False
    for year in range(2019, 2022):
        for month in range(1, 13):
            if len(str(month)) == 1:
                date_start = f'{year}0{month}01'
            else:
                date_start = f'{year}{month}01'

            if month + 1 == 13:
                date_finish = f'{year + 1}0101'
            else:
                if len(str(month + 1)) == 1:
                    date_finish = f'{year}0{month + 1}01'
                else:
                    date_finish = f'{year}{month + 1}01'
            if date_finish == 10 and year == 2021:
                fl = True
                break
            print('Текущая дата:', date_start)
            url = f'https://yandex.ru/patents/api/search?text=&template=%25request%25+%3C%3C+%28s_19_country%3ARU+%7C+s_19_country%3ASU%29+%3C%3C+s_22_date%3A%3E%3D{date_start}+%3C%3C+s_22_date%3A%3C%3D{date_finish}+%3C%3C+%28i_doc_type%3A1+%7C+i_doc_type%3A2%29&p=0&how=rlv&numdoc=3000'
            s = search(url)
            for i in s:
                if 'no info' == i:
                    continue
                file.write(i)
        if fl:
            break


if __name__ == '__main__':
    file = open('patent_result2.csv', 'a', encoding='utf8')
    header = 'link\ttitle\tdescription\tauthor\towner\tyear\n'
    file.write(header)
    main()
