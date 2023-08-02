from pprint import pprint
import json
import bd
from modules import bot

if __name__ == '__main__':
    # result_query = bot.query()  # Выполняем запрос - хочет человек познакомиться с кем-нибудь, или нет:
    # result_search_data = bot.requesting_search_data(result_query)  # Запрос данных для поиска по параметрам:
            # Конечный вывод:
            # found = bot.create_found(result_search_data)
            # pprint(found)
    # bot.create_found(result_search_data)  # Создается json для дальнейшей работы
    with open('found.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    # pprint(data)
    # print(dsn)

    bd.create_tables(bd.engine)
    bd.session.close()

