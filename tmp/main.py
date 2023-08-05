# createdb -U postgres Coursework_2
# dropdb -U postgres Coursework_2
from pprint import pprint
# from db.database import users_info_for_bot
import json
from modules import bot

if __name__ == '__main__':
    result_query = bot.query()  # Выполняем запрос - хочет человек познакомиться с кем-нибудь, или нет:
    # print(result_query)
    result_search_data = bot.requesting_search_data(result_query)  # Запрос данных для поиска по параметрам:
            # Конечный вывод:
            # found = bot.create_found(result_search_data)
            # pprint(found)
    bot.create_found(result_search_data)  # Создается json для дальнейшей работы
    with open('found.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    # pprint(data)
    # print(dsn)
    from db.database import users_info_for_bot
    answer = users_info_for_bot
    # pprint(answer) # Возвращаемая информация из бд, выводит всех пользователей
    selection_list = bot.view(result_query, answer)
    pprint(selection_list)
