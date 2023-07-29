from random import randrange
import configparser
import re
from pprint import pprint

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
    print(ext)
    vk.method('messages.send', ext)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        # print(event.message)
        # print(event.to_me)
        if event.to_me:
            request = event.text
            print(request)
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
            # print(request)
            if re.search(r"^[\w\-а-яА-я\d]*,{1}\s{1}[\d]{2,3},{1}\s{1}[\d]{2,3},{1}\s{1}[мж]{1}$", request):
                data = (request.split(', '))
                if data[3] == 'ж':
                    data[3] = '1'
                else:
                    data[3] = '2'
                print(f'data = {data}')
                write_msg(event.user_id, f"Данные приняты, нажмите 'Поиск'", search_keyboard)
            elif request == "Поиск":
                write_msg(event.user_id, "Начинаем")
                # search = VK.matches_found('bdate, city, sex, home_town', sex=1, hometown='New-York', count=5, age_from=16, age_to=20)
                search = VK.matches_found('bdate, city, sex, home_town', hometown=data[0], age_from=int(data[1]), age_to=int(data[2]), sex=int(data[3]), count=5)
                pprint(f'\nsearch = {search}')
                for i in search:
                    print(i)
                    found.append({'id': i['id'], 'city': i['city']['title']})
                break

            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")

pprint(f'\nfound = {found}')

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            print(request)
            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}", search_keyboard)
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")

