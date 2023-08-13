from sys import path
from os.path import dirname as dir
import sqlalchemy as sq
import json
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from db.models import create_tables, User, Match
from sqlalchemy import exc, select

path.append(dir(path[0])) # Для импорта из main нужно добавить путь


def create_connection(user_name, password, host_name, port, db_name):
    DSN = f'postgresql://{user_name}:{password}@{host_name}:{port}/{db_name}'
    return DSN

class Create:
    def __init__(self):
        pass
    def add_data_to_db(self, data):
        for record in data:
            session.add(Match(vk_id=record.get('id'),
                        first_name=record.get('first_name'),
                        last_name=record.get('last_name'),
                        vk_link=record.get('link'),
                        home_town=record.get('home_town'),
                        photo1=record.get('photos')[0]['url'],
                        photo2=record.get('photos')[1]['url'],
                        photo3=record.get('photos')[2]['url']
                             ))


    def create_user(self, data):
        new_user = data[0].get('requester')
        stmt = select(User)
        result = session.execute(stmt)
        print(result)
        session.add(User(vk_id=new_user))

def get_data_json(route):
    p = Path(route)
    with open(p, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data

class Read:
    def __init__(self):
        pass
    def read_from_db(self):
        q = session.query(Match.first_name, Match.last_name, Match.vk_link, Match.photo1, Match.photo2, Match.photo3)
        return q.all()


DSN = create_connection('postgres', 'Admin', 'localhost', 5432, 'VKinder')
engine = sq.create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()
data = get_data_json('found.json')
create_instance = Create()
create_instance.add_data_to_db(data)
session.commit()
read_db_instance = Read()
users_info_for_bot = read_db_instance.read_from_db()

session.close()
