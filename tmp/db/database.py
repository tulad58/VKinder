from sys import path
from os.path import dirname as dir
import sqlalchemy as sq
import json
from pathlib import Path
from sqlalchemy.orm import relationship, sessionmaker
from db.models import create_tables,  AbstractModel, Requester, User
from sqlalchemy import exc


path.append(dir(path[0])) # Для импорта из main нужно добавить путь

def create_connection(user_name, password, host_name, port, db_name):
    DSN = f'postgresql://{user_name}:{password}@{host_name}:{port}/{db_name}'
    return DSN

class Create:
    def __init__(self):
        pass
    def add_data_to_db(self, data):
        try:
            print("try")
            for record in data:
                session.add(User(vk_id=record.get('id'),
                            f_name=record.get('first_name'),
                            l_name=record.get('last_name'),
                            profile_link=record.get('link'),
                            hometown=record.get('home_town'),
                            photo1=record.get('photos')[0]['url'],
                            photo2=record.get('photos')[1]['url'],
                            photo3=record.get('photos')[2]['url'],
                            requester_fk=record.get('requester')
                ))
                print("try2")
                session.commit()
        except exc.IntegrityError:
            print("ecxept")
            session.rollback()

    # def add_to_favorite(self, data):
    #     session.add(Favorite(
    #         vk_id=data.get('id'),
    #         f_name=data.get('first_name'),
    #         l_name=data.get('last_name'),
    #         profile_link=data.get('link'),
    #         hometown=data.get('home_town'),
    #         photo1=data.get('photos')[0]['url'],
    #         photo2=data.get('photos')[1]['url'],
    #         photo3=data.get('photos')[2]['url'],
    #         requester_fk=data.get('requester')
    #     ))


    def add_requester(self, data):
        q = session.query(Requester).filter(Requester.requester_id == data[0].get('requester'))
        new_q = data[0].get('requester')
        try:
            if new_q != q.one():
                session.add(Requester(
                    requester_id=data[0].get('requester')
                ))
                session.commit()
        except exc.IntegrityError:
            session.rollback()

def get_data_json(route):
    p = Path(route)
    with open(p, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data

class Read:
    def __init__(self):
        pass
    def read_from_db(self):
        q = session.query(User.f_name, User.l_name, User.profile_link, User.photo1, User.photo2, User.photo3)
        return q.all()


DSN = create_connection('postgres', 'Admin', 'localhost', 5432, 'VKinder')
engine = sq.create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()
data = get_data_json('found.json')
create_instance = Create()
create_instance.add_requester(data)
print("1")
create_instance.add_data_to_db(data)
print("2")
# user.requesters.append(users)
session.commit()
print("3")
read_db_instance = Read()
users_info_for_bot = read_db_instance.read_from_db()

session.close()
