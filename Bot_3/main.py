# createdb -U postgres VKinder
# dropdb -U postgres VKinder
from pprint import pprint
import json
from modules import bot
import db.database

if __name__ == '__main__':
    while True:
        # Удаляем json файлы, если есть.
        bot.remove_json()

        # Выполняем запрос - хочет человек познакомиться с кем-нибудь, или нет.
        # В выводе - данные пользователя
        result_query = bot.query()
        # print(result_query)
        user_id = result_query[0]['id']

        # Запрос данных у пользователя для поиска по параметрам
        # В выводе - список с запрошенными параметрами
        result_search_data = bot.requesting_search_data(user_id, result_query)
        # print(result_search_data)

        # Выборка пользователей по параметрам из result_search_data, или ошибка поиска
        # Создается json для дальнейшей работы с БД
        result_create_found = bot.create_found(result_search_data)
        # print(result_create_found)
        if result_create_found == 'not_search':
            bot.write_msg(user_id, 'По Вашему запросу ничего не найдено,\n\
                                            попробуйте еще раз\n\n\
                                    Введите что-нибудь в чат')
            continue

        # Создание пользователя
        new_user = db.database.main_users_info_for_bot()

        # Возвращаемая информация из БД, выводит всех пользователей
        answer = db.database.users_info_for_bot()

        # answer_tmp_white = answer
        # answer_tmp_black = answer
        # pprint(answer)

        # Демонстрация пользователю отобранных предложений
        # В выводе - словарь с черным и белым списками
        selection_list = bot.view(user_id, answer)
        # pprint(selection_list)

        # Если вывод просмотра пользователя содержит черный и/или белый листы,
        # ему предлагается просмотреть их. Или запускается новый поиск.
        if selection_list['black'] or selection_list['favorites']:
            params = {}
            if selection_list['favorites']:
                with open('favorites.json', 'r', encoding='UTF-8') as favorites_file:
                    answer_favorite = db.database.favorite_info_for_bot()
                    print(f'answer_favorite = {answer_favorite}')
                    # favorites = json.load(favorites_file)
                    favorites = answer_favorite
                    params['favorites'] = favorites
            if selection_list['black']:
                with open('black.json', 'r', encoding='UTF-8') as black_file:
                    answer_black = db.database.black_info_for_bot()
                    # black = json.load(black_file)
                    black = answer_black
                    params['black'] = black

            print(f'params = {params}')
            result_go_to_favorites = bot.go_to_favorites(user_id, params)
            if result_go_to_favorites == 'break':
                break
        else:
            bot.write_msg(user_id, 'Вы ничего не выбрали,\n\
                                        черный и белый списки пусты,\n\
                                        попробуйте поиск еще раз\n\n\
                                        Введите что-нибудь в чат')
            continue
