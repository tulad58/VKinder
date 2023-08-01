from random import randrange
import configparser
import re
from pprint import pprint
# import json
# import time

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

# Получение токенов из файла ini:
config = configparser.ConfigParser()
config.read('tokens/tokens.ini')
token_g = config['TOKENS']['VK_token_GROUP']
token_u = config['TOKENS']['VK_token']

vk_g = vk_api.VkApi(token=token_g)
longpoll = VkLongPoll(vk_g)
vk_u = vk_api.VkApi(token=token_u)

# https://dev.vk.com/ru/api/bots/development/keyboard
start_keyboard = VkKeyboard(one_time=True)
start_keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
start_keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)

sex_keyboard = VkKeyboard(one_time=True)
sex_keyboard.add_button('Мужской', color=VkKeyboardColor.PRIMARY)
sex_keyboard.add_button('Женский', color=VkKeyboardColor.PRIMARY)

next_keyboard = VkKeyboard(one_time=True)
next_keyboard.add_button('Далее', color=VkKeyboardColor.PRIMARY)

def write_msg(user_id, message, keyboards=None):
    ext = {'user_id': user_id,
            'message': message,
            'random_id': randrange(10 ** 7),}
    if keyboards is not None:
        ext['keyboard'] = keyboards.get_keyboard()
    vk_g.method('messages.send', ext)

def get_photo(owner_id, album_id, extended, photo_sizes, count):
    s = []
    photos = vk_u.method('photos.get', {
                            'owner_id': owner_id,
                            'album_id': album_id,
                            'extended': extended,
                            'photo_sizes': photo_sizes,
                            'count': count,
                        })
    if not 'error' in photos:
        for i in photos['items']:
            for j in i['sizes']:
                if j['type'] == photo_sizes:
                    d = {
                        'likes': i['likes']['count'],
                        'url': j['url']
                    }
                    s.append(d)
    return sorted(s, key=lambda x: int(x['likes']), reverse=True)[:3]

def query():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                event_user_id = event.user_id
                name = vk_u.method('users.get', {'user_ids': event_user_id})[0]['first_name']
                request = event.text
                if request.lower() == "да":
                    message = f'Вы согласились, {name}, отлично!'
                    write_msg(event_user_id, message)
                    break
                if request.lower() == "нет":
                    message = f'{name}, Вы отказались, возвращайтесь, если надумаете'
                    write_msg(event_user_id, message)
                message = f'Привет!\n\n\
                            Здесь можно поискать аккаунты\n\
                            пользователей по параметрам.\n\
                            Желаете?\n\n\
                            Нажмите кнопки [Да] или [Нет]'
                write_msg(event_user_id, message, start_keyboard)
    return event_user_id

def create_found(result_search_data):
    event_user_id = result_search_data[0]
    search = vk_u.method(
                        'users.search',
                        {
                        'fields': 'bdate, city, sex, home_town',
                        'hometown': result_search_data[1],
                        'age_from': result_search_data[2],
                        'age_to': result_search_data[3],
                        'sex': result_search_data[4],
                        'count': 300,
                        'has_photo': 1,
                        'online': 1
                        }
                        )['items']
    found = []
    for i in search:
        if len(found) == 5:
            break
        if 'home_town' in i:  # Не всегда в выводе есть ключ
            # print('str 121:')
            photos = get_photo(
                owner_id=str(i['id']),
                album_id='profile',
                extended=1,
                photo_sizes='m',
                count=10)
            if len(photos) == 3:  # Если фото присутствуют в количестве 3х
                found.append({
                    'id': i['id'],
                    'link': f'https://vk.com/id{i["id"]}',
                    'first_name': i['first_name'],
                    'last_name': i['last_name'],
                    'photos': photos,
                    'home_town': i['home_town']
                    })
    return found

def requesting_search_data(result_query):
    result = []
    event_user_id = result_query
    result.append(event_user_id)
    message = f'Давайте введем параметры поиска.\n\
    Нужно будет ввести по очереди следующие данные:\n\n\
     - Название города, в котором хотите найти друзей\n\
     - Возраст с которого начнем поиск\n\
     - Возраст на котором закончим поиск\n\
     - Пол'
    write_msg(event_user_id, message)
    message = 'Введите желаемый город, и нажмите [ENTER]'
    write_msg(event_user_id, message)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request_town = event.text
                if re.search(r"^\d*[a-zA-Z\-а-яА-Я]+\d*$", request_town):
                    write_msg(event_user_id, 'Данные приняты')
                    result.append(request_town)
                    break
                else:
                    message = 'Введенные данные не годятся, введите еще раз:\n\
                        примеры: Москва; New-York; Нальчик-20'
                    write_msg(event_user_id, message)

    message = 'Введите желаемый возраст начала поиска\n\
                цифрами, (16 и более лет), и нажмите [ENTER]'
    write_msg(event_user_id, message)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request_from = event.text
                if re.search(r"^\d+$", request_from) and int(request_from) >= 16:
                    write_msg(event_user_id, 'Данные приняты')
                    result.append(request_from)
                    break
                else:
                    message = 'Введенные данные не годятся, введите еще раз:\n\
                                цифрами, (16 и более лет), и нажмите [ENTER]'
                    write_msg(event_user_id, message)

    message = 'Введите желаемый возраст окончания поиска\n\
                (16 и более лет), и нажмите [ENTER]'
    write_msg(event_user_id, message)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request_to = event.text
                if re.search(r"^\d+$", request_to) and int(request_to) >= 16:
                    write_msg(event_user_id, 'Данные приняты')
                    result.append(request_to)
                    break
                else:
                    message = 'Введенные данные не годятся, введите еще раз:\n\
                                цифрами, (16 и более лет), и нажмите [ENTER]'
                    write_msg(event_user_id, message)

    message = 'Выберите желаемый пол,\n\
                и нажмите соответствующую кнопку'
    write_msg(event_user_id, message, sex_keyboard)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request_sex = event.text
                if re.search(r"^(Мужской|Женский){1}$", request_sex):
                    write_msg(event_user_id, 'Данные приняты')
                    result.append(request_sex)
                    break
                else:
                    message = 'Введенные данные не годятся, выберите пол,\n\
                                и нажмите соответствующую кнопку'
                    write_msg(event_user_id, message, sex_keyboard)
    if result[4].lower() == 'ж':
        result[4] = '1'
    else:
        result[4] = '2'
    return result

if __name__ == '__main__':

    # Выполняем запрос - хочет человек познакомиться с кем-нибудь, или нет:
    result_query = query()

    # Запрос данных для поиска по параметрам:
    result_search_data = requesting_search_data(result_query)

    # Конечный вывод:
    found = create_found(result_search_data)
    pprint(found)
