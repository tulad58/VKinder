import requests
from pprint import pprint


class VKontakte:

    '''
    Модуль содержит методы для работы с ВКонтакте.

    photos()
        Принимает аргументы:
            owner_id = Идентификатор владельца альбома.
            album_id = Идентификатор альбома.
            extended = дополнительные поля likes, comments, tags, can_comment, reposts.
            photo_sizes = Возвращать доступные размеры фотографии в специальном формате.
            count = Количество записей, которое будет получено.

    resolve_screen_name():
        Принимает аргументы:
            screen_name = "ScreenName" владельца альбома.
        Возвращает:
            "ID" владельца альбома.

    user(self, owner_id, fields)
        Принимает аргументы:
            owner_id = Идентификатор владельца аккаунта.
            fields = Список дополнительных параметров для возврата, например - 'sex, city, bdate'.
        Возвращает:
            Словарь с запрошенными данными.

    matches_found(self, fields, sex, city, bdate)
        Принимает аргументы:

        Возвращает:

    '''

    def __init__(self, token):
        self.token = token

    def resolve_screen_name(self, screen_name):
        url = 'https://api.vk.com/method/utils.resolveScreenName'
        params = {
            'access_token': self.token,
            'screen_name': screen_name,
            'v': '5.131'
        }
        response = requests.get(url=url, params=params).json()
        return response['response']['object_id']

    def photos(self, owner_id, album_id, extended, photo_sizes, count):
        if not str(owner_id).isdigit():
            owner_id = self.resolve_screen_name(owner_id)

        url = 'https://api.vk.com/method/photos.get'
        params = {
            'access_token': self.token,
            'owner_id': owner_id,
            'album_id': album_id,
            'extended': extended,
            'photo_sizes': photo_sizes,
            'count': count,
            'v': '5.131'
        }
        response = requests.get(url=url, params=params)
        pprint(f'response from def photos = {response.json()}')
        return response

    def user(self, owner_id, fields):
        if not owner_id.isdigit():
            owner_id = self.resolve_screen_name(owner_id)

        url = 'https://api.vk.com/method/users.get'
        params = {
            'access_token': self.token,
            'user_ids': owner_id,
            'fields': fields,
            'v': '5.131'
        }
        response = requests.get(url=url, params=params).json()['response'][0]
        ret = {
        'id': response['id'],
        'first_name': response['first_name'],
        'last_name': response['last_name'],
        'sex': response['sex'],
        'city': response['city']['id'],
        'bdate': response['bdate'],
        'link': f"https://vk.com/id{response['id']}"
        }
        return ret

    def matches_found(self, fields, sex, hometown, count, age_from, age_to, has_photo, online):
        url = 'https://api.vk.com/method/users.search'
        params = {
            'access_token': self.token,
            'sex': sex,
            'count': count,
            'hometown': hometown,
            'age_from': age_from,
            'age_to': age_to,
            'fields': fields,
            'has_photo': has_photo,
            'online': online,
            'v': '5.131'
        }
        response = requests.get(url=url, params=params).json()['response']['items']
        return response
