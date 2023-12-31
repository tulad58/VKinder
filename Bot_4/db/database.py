import sqlalchemy as sq
import json
from sqlalchemy import select
from sqlalchemy.orm import declarative_base, sessionmaker
from db.models import User, Favorite, BlackList, create_tables, MainUser


def create_connection(user_name, password, host_name, port, db_name):
    return f'postgresql://{user_name}:{password}@{host_name}:{port}/{db_name}'


def get_current_user_vk_id(data):
    vk_id = data[0].get('requester')
    return vk_id


class Create:
    def __init__(self):
        pass

    @staticmethod
    def add_data_to_db(data):
        new_vk_id = get_current_user_vk_id(data)
        main_user_id = session.execute(select(MainUser.id).where(MainUser.vk_id == new_vk_id)).first()
        for record in data:
            session.add(User(vk_id=record.get('id'),
                        f_name=record.get('first_name'),
                        l_name=record.get('last_name'),
                        profile_link=record.get('link'),
                        hometown=record.get('home_town'),
                        photo1=record.get('photos')[0]['url'],
                        photo2=record.get('photos')[1]['url'],
                        photo3=record.get('photos')[2]['url'],
                        main_user_id=main_user_id[0]))

    @staticmethod
    def add_new_main_user(data):
        check_id = get_current_user_vk_id(data)
        try:
            session.add(MainUser(vk_id=check_id))
        except Exception:
            print("Ошибка!")
            pass

    @staticmethod
    def add_data_to_favorite(data, user_id):
        new_main_user_id = session.execute(select(MainUser.id).where(MainUser.vk_id == user_id)).one()[0]
        for record in data:
            new_user_id = session.execute(select(User.id).where(User.vk_id == record.get('id'))).first()[0]
            session.add(Favorite(
                        user_id=new_user_id,
                        main_user_id=new_main_user_id))

    @staticmethod
    def add_data_to_black(data):
        for record in data:
            session.add(BlackList(
                vk_id=record.get('id'),
                profile_link=record.get('link'),
                photo=record.get('photo')))


def get_data_json(route):
    with open(route, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data


class Read:
    def __init__(self):
        pass

    @staticmethod
    def read_from_db_users(data):
        current_user_vk_id = get_current_user_vk_id(data)
        current_user_id = session.execute(select(MainUser.id).where(MainUser.vk_id == current_user_vk_id)).one()[0]
        q = session.execute(select(User.f_name, User.l_name, User.profile_link, User.photo1, User.photo2, User.photo3).
                            where(User.main_user_id == current_user_id))
        return q.all()

    @staticmethod
    def read_from_db_favorite():
        q = session.execute(select(User.vk_id, User.profile_link, User.photo1).join_from(User, Favorite).
                            join_from(User, MainUser))
        return q.all()

    @staticmethod
    def read_from_db_black():
        q = session.query(BlackList.vk_id, BlackList.profile_link, BlackList.photo)
        return q.all()

    @staticmethod
    def read_from_main_users():
        q = session.query(MainUser.id, MainUser.vk_id)
        return q.all()


Base = declarative_base()
DSN = create_connection('postgres', 'Admin', 'localhost', 5432, 'VKinder')
engine = sq.create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()


def main_users_info_for_bot():
    with session as s:
        data_found = get_data_json('found.json')
        create_instance = Create()
        create_instance.add_new_main_user(data_found)
        s.commit()
        read_db_instance = Read()
        res = read_db_instance.read_from_main_users()
        return res


def users_info_for_bot():
    with session as s:
        data_found = get_data_json('found.json')
        create_instance = Create()
        create_instance.add_data_to_db(data_found)
        s.commit()
        read_db_instance = Read()
        return read_db_instance.read_from_db_users(data_found)


def favorite_info_for_bot(user_id):
    with session as s:
        data_favorite = get_data_json('favorites.json')
        create_instance = Create()
        create_instance.add_data_to_favorite(data_favorite, user_id)
        s.commit()
        read_db_instance = Read()
        return read_db_instance.read_from_db_favorite()


def black_info_for_bot():
    with session as s:
        data_black = get_data_json('black.json')
        create_instance = Create()
        create_instance.add_data_to_black(data_black)
        s.commit()
        read_db_instance = Read()
        return read_db_instance.read_from_db_black()
