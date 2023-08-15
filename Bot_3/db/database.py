import sqlalchemy as sq
import json
from sqlalchemy import select
from sqlalchemy.orm import declarative_base, sessionmaker
from db.models import User, Favorite, BlackList, create_tables, MainUser
def create_connection(user_name, password, host_name, port, db_name):
    DSN = f'postgresql://{user_name}:{password}@{host_name}:{port}/{db_name}'
    return DSN


def get_current_user_vk_id(data):
    vk_id = data[0].get('requester')
    return vk_id


class Create:
    def __init__(self):
        pass


    def add_data_to_db(self, data):
        new_vk_id = get_current_user_vk_id(data)
        main_user_id = session.execute(select(MainUser.id).where(MainUser.vk_id == new_vk_id)).first()
        print(f"main_user_id:{main_user_id} {type(main_user_id)}")
        for record in data:
            session.add(User(vk_id=record.get('id'),
                        f_name=record.get('first_name'),
                        l_name=record.get('last_name'),
                        profile_link=record.get('link'),
                        hometown=record.get('home_town'),
                        photo1=record.get('photos')[0]['url'],
                        photo2=record.get('photos')[1]['url'],
                        photo3=record.get('photos')[2]['url'],
                        main_user_id=main_user_id[0]
            )
        )

    def add_new_main_user(self, data):
        check_id = get_current_user_vk_id(data)
        try:
            session.add(MainUser(vk_id=check_id))
        except Exception:
            pass

    def add_data_to_favorite(self, data):
        print(data)
        for record in data:
            print(record)
            session.add(Favorite(vk_id=record.get('id'),
                        profile_link=record.get('link'),
                        photo=record.get('photo')
            )
        )

    def add_data_to_black(self, data):
        print(data)
        for record in data:
            print(record)
            session.add(BlackList(vk_id=record.get('id'),
                        profile_link=record.get('link'),
                        photo=record.get('photo')
            )
        )

def get_data_json(route):
    with open(route, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data

class Read:
    def __init__(self):
        pass
    def read_from_db_users(self, data):
        current_user_vk_id = get_current_user_vk_id(data)
        current_user_id = session.query(MainUser.id).where(MainUser.vk_id==current_user_vk_id)
        q = session.query(User.f_name, User.l_name, User.profile_link, User.photo1, User.photo2, User.photo3)\
            .where(User.main_user_id==current_user_id)
        return q.all()

    def read_from_db_favorite(self):
        q = session.query(Favorite.vk_id, Favorite.profile_link, Favorite.photo)
        return q.all()

    def read_from_db_black(self):
        q = session.query(BlackList.vk_id, BlackList.profile_link, BlackList.photo)
        return q.all()

    def read_from_main_users(self):
        q = session.query(MainUser.id, MainUser.vk_id)
        return q.all()

Base = declarative_base()
DSN = create_connection('postgres', 'Admin', 'localhost', 5432, 'VKinder')
engine = sq.create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()

def main_users_info_for_bot():
    data_found = get_data_json('found.json')
    create_instance = Create()
    create_instance.add_new_main_user(data_found)
    session.commit()
    read_db_instance = Read()
    res = read_db_instance.read_from_main_users()
    print(f"main_users_info_for_bot {res}")
    return res
def users_info_for_bot():
    data_found = get_data_json('found.json')
    create_instance = Create()
    create_instance.add_data_to_db(data_found)
    session.commit()
    read_db_instance = Read()
    return read_db_instance.read_from_db_users(data_found)

def favorite_info_for_bot():
    data_favorite = get_data_json('favorites.json')
    create_instance = Create()
    create_instance.add_data_to_favorite(data_favorite)
    session.commit()
    read_db_instance = Read()
    return read_db_instance.read_from_db_favorite()

def black_info_for_bot():
    data_black = get_data_json('black.json')
    print(data_black)
    create_instance = Create()
    create_instance.add_data_to_black(data_black)
    session.commit()
    read_db_instance = Read()
    return read_db_instance.read_from_db_black()
session.close()
