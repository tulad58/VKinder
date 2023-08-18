# createdb -U postgres VKinder
# dropdb -U postgres VKinder
# from pprint import pprint
# import json
from modules import bot
import db.database

if __name__ == '__main__':
    viewed = set()  # Просмотренные

    # Выполняем запрос - хочет человек познакомиться с кем-нибудь, или нет.
    # В выводе - данные пользователя
    result_query = bot.query()
    # print(result_query)
    user_id = result_query[0]['id']

    while True:
        # Удаляем json файлы, если есть.
        bot.remove_json()

        # Запрос данных у пользователя для поиска по параметрам
        # В выводе - список с запрошенными параметрами
        result_search_data = bot.requesting_search_data(user_id, result_query)
        # print(result_search_data)

        # Выборка пользователей по параметрам из result_search_data, или ошибка поиска
        # Создается json для дальнейшей работы с БД
        result_create_found = bot.create_found(result_search_data, viewed)
        # print(result_create_found)
        if result_create_found == 'not_search':
            bot.write_msg(user_id, 'По Вашему запросу ничего не найдено,\n\
                                            попробуйте еще раз\n\n\
                                    Введите что-нибудь в чат')
            continue

        try:
            db.database.main_users_info_for_bot()
        except Exception:
            pass

        # Возвращаемая информация из БД, выводит всех пользователей
        answer = db.database.users_info_for_bot()
        # print(f'answer = {answer}')

        # Демонстрация пользователю отобранных предложений
        # В выводе - словарь с черным и белым списками
        selection_list = bot.view(user_id, answer, viewed)
        # pprint(selection_list)

        viewed = selection_list['viewed']
        # print(viewed)

        # Если вывод просмотра пользователя содержит черный и/или белый листы,
        # ему предлагается просмотреть их. Или запускается новый поиск.
        if selection_list['black'] or selection_list['favorites']:
            params = {}
            if selection_list['favorites']:
                answer_favorite = db.database.favorite_info_for_bot(user_id)
                params['favorites'] = answer_favorite
            if selection_list['black']:
                answer_black = db.database.black_info_for_bot()
                params['black'] = answer_black

            # print(f'params = {params}')
            result_go_to_favorites = bot.go_to_favorites(user_id, params)
            if result_go_to_favorites == 'break':
                # Удаляем json файлы, если есть, заканчиваем работу.
                bot.remove_json()
                break
        else:
            bot.write_msg(user_id, 'Вы ничего не выбрали,\n\
                                        черный и белый списки пусты,\n\
                                        попробуйте поиск еще раз\n\n\
                                        Введите что-нибудь в чат')
            continue
