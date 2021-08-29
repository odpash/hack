from find_pages_by_query import main as PAGES_LIST
from parse_page import main as PAGE_INFO
import settings
import multiprocessing
import okved_links
import time
import pymongo


def write_new_record(records):
    db_client = pymongo.MongoClient("mongodb://localhost:27017/")
    current_db = db_client["hackathon"]
    collection = current_db["rbc_results"]
    collection.insert_many(records)


def main():  # returns string (if errors) and list (if all is ok)
    queries = okved_links.main()
    idx = 0
    fl = False
    for query in queries:
        start = time.time()
        idx += 1
        if fl:
            pages_list = PAGES_LIST(query)
            if pages_list['status'] == 'ok':
                with multiprocessing.Pool(60) as p:
                    res = p.map(PAGE_INFO, pages_list['desc'])
                write_new_record(res)
                print(f'Обработано: {idx} / {len(queries)}. Время: {time.time() - start}')
        if idx == 128:
            fl = True


if __name__ == '__main__':
    multiprocessing.freeze_support()
    print(main())
