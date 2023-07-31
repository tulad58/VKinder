from random import randrange
import configparser
import re
from pprint import pprint
import json
import time

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from Modules.VK.ModuleVK import VKontakte


# Получение токенов из файла ini:
config = configparser.ConfigParser()
config.read('tokens/tokens.ini')
token_g = config['TOKENS']['VK_token_GROUP']
token_u = config['TOKENS']['VK_token']

vk = vk_api.VkApi(token=token_g)
longpoll = VkLongPoll(vk)

VK = VKontakte(token_u)

print('\n' * 20)

start_keyboard = VkKeyboard(one_time=True)
start_keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
start_keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)

search_keyboard = VkKeyboard(one_time=True)
search_keyboard.add_button('Поиск', color=VkKeyboardColor.PRIMARY)

keyboard = VkKeyboard(one_time=True)
keyboard.add_button('Привет', color=VkKeyboardColor.NEGATIVE)
keyboard.add_button('Клавиатура', color=VkKeyboardColor.POSITIVE)
keyboard.add_line()
keyboard.add_location_button()
keyboard.add_line()
keyboard.add_button('Далее', color=VkKeyboardColor.PRIMARY)

def write_msg(user_id, message, keyboards=None):
    ext = {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),}
    if keyboards is not None:
        ext['keyboard'] = keyboards.get_keyboard()
    vk.method('messages.send', ext)

def get_photo(owner_id, album_id, extended, photo_sizes, count):
    s = []
    photos = VK.photos(owner_id, album_id, extended, photo_sizes, count).json()
    if not 'error' in photos:
        for i in photos['response']['items']:
            for j in i['sizes']:
                if j['type'] == photo_sizes:
                    d = {
                        'likes': i['likes']['count'],
                        'url': j['url']
                    }
                    s.append(d)
    return sorted(s, key=lambda x: int(x['likes']), reverse=True)[:3]

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            if request.lower() == "да":
                message = f'Вы согласились, {event.user_id}, отлично!\n\n\
                    Давайте введем параметры поиска.\n\
                    город, возраст от, возраст до, пол (м/ж) - через запятую с пробелом\n\
                    примеры: Москва, 25, 30, м; New-York, 19, 25, ж; Нальчик-20, 35, 40, м'
                write_msg(event.user_id, message)
                break
            if request.lower() == "нет":
                message = f'Вы отказались, {event.user_id}, возвращайтесь, если надумаете'
                write_msg(event.user_id, message)
            message = 'Привет! Тут можно познакомиться, желаете?\nнажмите Да/Нет'
            write_msg(event.user_id, message, start_keyboard)

for event in longpoll.listen():
    found = []
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            if re.search(r"^[\w\-а-яА-я\d]*,{1}\s{1}[\d]{2,3},{1}\s{1}[\d]{2,3},{1}\s{1}[мжМЖ]{1}$", request):
                data = (request.split(', '))
                if data[3].lower() == 'ж':
                    data[3] = '1'
                else:
                    data[3] = '2'
                write_msg(event.user_id, f"Данные приняты, нажмите 'Поиск'", search_keyboard)
            elif request == "Поиск":
                write_msg(event.user_id, "Начинаем")
                search = VK.matches_found('bdate, city, sex, home_town', hometown=data[0], age_from=int(data[1]), age_to=int(data[2]), sex=int(data[3]), count=30)
                for i in search:
                    if len(found) == 5:
                        break
                    if 'home_town' in i:  # Не всегда в выводе есть поле
                        photos = get_photo(owner_id=str(i['id']), album_id='profile', extended=1, photo_sizes='m', count=10)
                        # pprint(f'photos = {photos}')
                        if len(photos) == 3:  # Если фото присутствуют в количестве 3х
                            found.append({'id': i['id'], 'link': f'https://vk.com/id{i["id"]}', 'first_name': i['first_name'], 'last_name': i['last_name'], 'photos': photos, 'home_town': i['home_town']})
                # break
                if not found:  # Если ничего не нашлось
                    write_msg(event.user_id, "Данные по Вашему запросу не найдены,\n\
                              попоробуйте изменить его")
                else:  # Если нашлось
                    break

            else:
                write_msg(event.user_id, "Введенные данные не годятся, введите еще раз:\n\
                          город, возраст от, возраст до, пол (м/ж) - через запятую с пробелом\n\
                    примеры: Москва, 25, 30, м; New-York, 19, 25, ж; Нальчик-20, 35, 40, м")

print('\n\n\n')
print(f'found = len = {len(found)}')
print(f'found:')
pprint(found)

write_msg(event.user_id, "Данные собраны")

for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            # print(request)
            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}", search_keyboard)
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")

# for event in longpoll.listen():
#     if event.type == VkEventType.MESSAGE_NEW:
#         if 'да' in event.message['text'].lower():
#             if event.from_chat:
#                 message = 'Вы согласились, отлично!\n\
#                     Давайте введем параметры поиска...\n\
#                     город, возраст, пол (м/ж) - через запятую'
#                 vk_messages_send(message, event.chat_id)
#             break
#         if 'нет' in event.message['text'].lower():
#             if event.from_chat:
#                 message = 'Вы отказались, возвращайтесь, если надумаете'
#                 vk_messages_send(message, event.chat_id, start_keyboard)
#         message = 'Тут можно познакомиться, желаете?\nнажмите Да/Нет'
#         vk_messages_send(message, event.chat_id, start_keyboard)

# for event in longpoll.listen():
#     if event.type == VkEventType.MESSAGE_NEW:

#         if event.to_me:
#             request = event.text

#             if request == "привет":
#                 write_msg(event.user_id, f"Хай, {event.user_id}")
#             elif request == "пока":
#                 write_msg(event.user_id, "Пока((")
#             else:
#                 write_msg(event.user_id, "Не поняла вашего ответа...")








# for event in longpoll.listen():
#     if event.type == VkEventType.MESSAGE_NEW:

#         if event.to_me:
#             request = event.text

#             if request == "привет":
#                 write_msg(event.user_id, f"Хай, {event.user_id}")
#             elif request == "пока":
#                 write_msg(event.user_id, "Пока((")
#             else:
#                 write_msg(event.user_id, "Не поняла вашего ответа...")
