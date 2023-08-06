# createdb -U postgres VKinder
# dropdb -U postgres VKinder
from pprint import pprint
import json
from modules import bot

if __name__ == '__main__':
    while True:
        # Выполняем запрос - хочет человек познакомиться с кем-нибудь, или нет.
        # В выводе - id пользователя
        result_query = bot.query()
        # print(result_query)

        # Запрос данных у пользователя для поиска по параметрам
        # В выводе - список с запрошенными параметрами
        result_search_data = bot.requesting_search_data(result_query)
        # print(result_search_data)

        # Выборка пользователей по параметрам из result_search_data, или ошибка поиска
        # Создается json для дальнейшей работы с БД
        result_create_found = bot.create_found(result_search_data)
        # print(result_create_found)
        if result_create_found == 'not_search':
            bot.write_msg(result_query, 'По Вашему запросу ничего не найдено,\n\
                                            попробуйте еще раз')
            continue

        # Открываем json
        # with open('found.json', 'r', encoding='utf-8') as file:
        #     data = json.load(file)
        # pprint(data)

        # Импортируем модуль по работе с БД
        from db.database import users_info_for_bot

        # Возвращаемая информация из БД, выводит всех пользователей
        answer = users_info_for_bot
        # answer_tmp_white = answer
        # answer_tmp_black = answer
        # pprint(answer)

        # Демонстрация пользователю отобранных предложений
        # В выводе - словарь с черным и белым списками
        selection_list = bot.view(result_query, answer)
        pprint(selection_list)

        # Если вывод просмотра пользователя содержит черный или белый листы,
        # ему предлагается просмотреть их. Или запускается новый поиск.
        if selection_list['black'] or selection_list['white']:
            # Пока нет данных для проверки и вывода
            # bot.go_to_favorites(result_query, answer_tmp_white, answer_tmp_black)
            
            # Тестю набор кнопок при наличии разных списков
            bot.go_to_favorites(result_query, selection_list['black'], selection_list['white'])
        else:
            bot.write_msg(result_query, 'Вы ничего не выбрали,\n\
                                        черный и белый списки пусты,\n\
                                        попробуйте поиск еще раз')
            continue
