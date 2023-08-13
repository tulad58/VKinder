from random import randrange
import configparser
import re
from pprint import pprint
import json
from datetime import datetime
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

choice_keyboard = VkKeyboard(one_time=True)
choice_keyboard.add_button('В избранные', color=VkKeyboardColor.POSITIVE)
choice_keyboard.add_button('В черный список', color=VkKeyboardColor.NEGATIVE)
choice_keyboard.add_button('Далее', color=VkKeyboardColor.PRIMARY)

user_keyboard = VkKeyboard(one_time=True)
user_keyboard.add_button('По моим данным', color=VkKeyboardColor.PRIMARY)
user_keyboard.add_button('По вводимым данным', color=VkKeyboardColor.PRIMARY)

favorites_keyboard_1 = VkKeyboard(one_time=True)
favorites_keyboard_1.add_button('В избранное', color=VkKeyboardColor.POSITIVE)
favorites_keyboard_1.add_button('В черный список', color=VkKeyboardColor.NEGATIVE)
favorites_keyboard_1.add_button('Новый поиск', color=VkKeyboardColor.PRIMARY)
favorites_keyboard_1.add_button('Выход', color=VkKeyboardColor.PRIMARY)

favorites_keyboard_2 = VkKeyboard(one_time=True)
favorites_keyboard_2.add_button('В избранное', color=VkKeyboardColor.POSITIVE)
favorites_keyboard_2.add_button('Новый поиск', color=VkKeyboardColor.PRIMARY)
favorites_keyboard_2.add_button('Выход', color=VkKeyboardColor.PRIMARY)

favorites_keyboard_3 = VkKeyboard(one_time=True)
favorites_keyboard_3.add_button('В черный список', color=VkKeyboardColor.NEGATIVE)
favorites_keyboard_3.add_button('Новый поиск', color=VkKeyboardColor.PRIMARY)
favorites_keyboard_3.add_button('Выход', color=VkKeyboardColor.PRIMARY)


# ----------------------------------------------------------------------

def write_msg(user_id, message, keyboards=None, photo=None):
    ext = {'user_id': user_id,
            'message': message,
            'random_id': randrange(10 ** 7),}
    if keyboards is not None:
        ext['keyboard'] = keyboards.get_keyboard()
    if photo is not None:
        ext['attachment'] = photo
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

def resolve_city(request_town):
    city = vk_u.method('database.getCities', {
                            'q': request_town,
                            'count': 1
                        })
    # print(city)
    return city

def search_by_user(data):
    user_id, bdate, city, sex, town = data
    print(user_id, bdate, city, sex)
    d_now = datetime.now().date()
    d_user = datetime.strptime(bdate, '%d.%m.%Y').date()
    a = d_now - d_user
    age = int(int(str(a.days)) / 365)
    age_from = age - 5
    if age < 21:
        age_from = 16
    age_to = age + 5
    if sex == 2:
        sex = 1
    result = [user_id, city, town, str(age_from), str(age_to), str(sex)]
    return result

def search_by_input(user_id):
    result = []
    event_user_id = user_id
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
                if resolve_city(request_town)['items']:
                    city_id = resolve_city(request_town)['items'][0]['id']
                    city_name = resolve_city(request_town)['items'][0]['title']
                    write_msg(event_user_id, 'Данные приняты')
                    result.append(city_id)
                    result.append(city_name)
                    break
                else:
                    message = 'Введенные данные не годятся, введите еще раз:\n\
                        примеры: Москва; New-York; Нальчик'
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

    message = f'Введите желаемый возраст окончания поиска\n\
                ({request_from} и более лет), и нажмите [ENTER]'
    write_msg(event_user_id, message)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request_to = event.text
                if re.search(r"^\d+$", request_to) and int(request_to) >= int(request_from):
                    write_msg(event_user_id, 'Данные приняты')
                    result.append(request_to)
                    break
                else:
                    message = f'Введенные данные не годятся, введите еще раз:\n\
                                цифрами, ({request_from} и более лет), и нажмите [ENTER]'
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
                    if request_sex == 'Женский':
                        result.append('1')
                    else:
                        result.append('2')
                    break
                else:
                    message = 'Введенные данные не годятся, выберите пол,\n\
                                и нажмите соответствующую кнопку'
                    write_msg(event_user_id, message, sex_keyboard)
    return result

# ----------------------------------------------------------------------

def query():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                event_user_id = event.user_id  # метод быстрого получения user_id
                users_get = vk_u.method('users.get', {
                                        'user_ids': event_user_id,
                                        'fields': 'bdate, city, sex, home_town, country'
                                        })
                name = users_get[0]['first_name']
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
    return users_get

def requesting_search_data(user_id, result_query):
    rq = result_query[0]
    # print(rq)
    if (rq.get('bdate') is not None and
        rq.get('city') is not None and
        rq.get('sex') is not None and
        rq['bdate'] and
        rq['city'] and
        rq['sex']):
        data = (
            rq['id'],
            rq['bdate'],
            rq['city']['id'],
            rq['sex'],
            rq['city']['title'])
        # print(data)
        message = f"Для поиска по параметрам Вашего профиля\n\
                достаточно данных, таких как город, дата рождения, пол.\n\
                Вам доступен поиск по вводимым параметрам, или по Вашим\n\
                При поиске по Вашим данным будут использованы параметры:\n\
                1) Ваш город {rq['city']['title']},\n\
                2) Противоположный пол\n\
                3) Возраст +/- пять лет (не менее 16 лет)\n\n\
                Нажмите соответствующую кнопку"
        write_msg(user_id, message, user_keyboard)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request_input_user = event.text
                    if re.search(r"^По моим данным$", request_input_user):
                        write_msg(user_id, 'ОК')
                        return search_by_user(data)
                    if re.search(r"^По вводимым данным$", request_input_user):
                        write_msg(user_id, 'ОК')
                        return search_by_input(user_id)
                    message = 'Введенные данные не годятся,\n\
                                нажмите соответствующую кнопку'
                    write_msg(user_id, message, input_user_keyboard)
                    input_user_keyboard = VkKeyboard(one_time=True)
    else:
        message = 'Для поиска по параметрам Вашего профиля\n\
                    нехватает данных, проверьте в профиле:\n\
                    ГОРОД, ДАТУ РОЖДЕНИЯ, ПОЛ.\n\
                    Вам доступен поиск по вводимым параметрам'
        write_msg(user_id, message)
        return search_by_input(user_id)

def create_found(result_search_data):
    event_user_id = result_search_data[0]
    search = vk_u.method(
                        'users.search',
                        {
                        'fields': 'bdate, city, sex, home_town',
                        'city': result_search_data[1],
                        'city_mame': result_search_data[2],
                        'age_from': result_search_data[3],
                        'age_to': result_search_data[4],
                        'sex': result_search_data[5],
                        'count': 300,
                        'has_photo': 1,
                        'online': 1
                        }
                        )['items']
    if not search:
        return 'not_search'
    found = []
    for i in search:
        print(i)
        if len(found) == 5:  # количество предложений по поиску
            break
        if (i.get('city') is not None and i.get('home_town') is not None and
            i['city'] and i['home_town']):  # Не всегда в выводе есть сами ключи или их значения
            photos = get_photo(
                owner_id=str(i['id']),
                # album_id='profile',  # альбом для поиска
                album_id='wall',  # альбом для поиска
                extended=1,  # возвращать дополнительные поля
                photo_sizes='x',  # размер фотографий
                count=10)
            if len(photos) == 3:  # Если фото присутствуют в количестве 3х
                found.append({
                    'id': i['id'],
                    'link': f'https://vk.com/id{i["id"]}',
                    'first_name': i['first_name'],
                    'last_name': i['last_name'],
                    'photos': photos,
                    'home_town': i['home_town'],
                    'requester': event_user_id,
                    'city': i['city']
                })
    with open('found.json', 'w', encoding='UTF-8') as found_file:
        json.dump(found, found_file, indent=4, ensure_ascii=False)
    return found

def view(user_id, answer):
    favorites = []
    black = []
    for i in answer:
        pars = re.search(r'(https:\/\/vk\.com\/id)(\d+)', i[2])
        id = pars.group(2)
        message = f'\
        {i[0]} {i[1]}\n\
        Ссылка на профиль - {i[2]}\n\
        Фото пользователя:'
        photo = f'{i[3]},{i[4]},{i[5]}'
        write_msg(user_id, message, photo=photo)
        message = 'Выберите дальнейшее действие,\n\
                    и нажмите соответствующую кнопку'
        write_msg(user_id, message, choice_keyboard)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request_choice = event.text
                    if re.search(r"^В избранные$", request_choice):
                        write_msg(user_id, 'ОК, в избранные')
                        favorites.append({'id': id, 'link': i[2], 'photo': i[3]})
                        break
                    if re.search(r"^В черный список$", request_choice):
                        write_msg(user_id, 'ОК, в черный список')
                        black.append({'id': id, 'link': i[2], 'photo': i[3]})
                        break
                    if re.search(r"^Далее$", request_choice):
                        write_msg(user_id, 'ОК, пропускаем')
                        break
                    message = 'Введенные данные не годятся,\n\
                                нажмите соответствующую кнопку'
                    write_msg(user_id, message, choice_keyboard)
    if favorites:
        with open('favorites.json', 'w', encoding='UTF-8') as favorites_file:
            json.dump(favorites, favorites_file, indent=4, ensure_ascii=False)
    if black:
        with open('black.json', 'w', encoding='UTF-8') as black_file:
            json.dump(black, black_file, indent=4, ensure_ascii=False)
    return {'favorites': favorites, 'black': black}

def go_to_favorites(user_id, params):
    if 'favorites' in params and 'black' in params:
        favorites_keyboard = favorites_keyboard_1
    if 'favorites' in params and 'black' not in params:
        favorites_keyboard = favorites_keyboard_2
    if 'favorites' not in params and 'black' in params:
        favorites_keyboard = favorites_keyboard_3
    message = 'Список предложений закончился,\n\
                как желаете продолжить?\n\
                Нажмите соответствующую кнопку'
    write_msg(user_id, message, favorites_keyboard)
    for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        request_favorites = event.text
                        if re.search(r"^В избранное$", request_favorites):
                            write_msg(user_id, 'ОК, в избранное\n\
                                                Содержимое списка\n\n')
                            for i in params['favorites']:
                                message = f"\
                                Ссылка на профиль - {i['link']}\n\
                                Фото пользователя:"
                                photo = f"{i['photo']}"
                                write_msg(user_id, message, photo=photo)
                            write_msg(user_id, 'Новый поиск\n\n\
                                                Введите что-нибудь в чат')
                            break
                        if re.search(r"^В черный список$", request_favorites):
                            write_msg(user_id, 'ОК, в черный список\n\
                                                Содержимое списка\n\n')
                            for i in params['black']:
                                message = f"\
                                Ссылка на профиль - {i['link']}\n\
                                Фото пользователя:"
                                photo = f"{i['photo']}"
                                write_msg(user_id, message, photo=photo)
                            write_msg(user_id, 'Новый поиск\n\n\
                                                Введите что-нибудь в чат')
                            break
                        if re.search(r"^Новый поиск$", request_favorites):
                            write_msg(user_id, 'ОК, поищем снова.\nВведите что-нибудь.')
                            break
                        if re.search(r"^Выход$", request_favorites):
                            write_msg(user_id, 'ОК, пока!')
                            return 'break'
                        message = 'Введенные данные не годятся,\n\
                                    как желаете продолжить?\n\
                                    Нажмите соответствующую кнопку'
                        write_msg(user_id, message, favorites_keyboard)
