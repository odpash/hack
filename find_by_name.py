import requests
import list_org


def main(fio):
    l_o = list_org.search_by_fio(fio)
    print(l_o)


print(main('Логинов Виктор Федорович'))
