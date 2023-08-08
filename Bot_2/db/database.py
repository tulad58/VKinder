from sys import path
from os.path import dirname as dir
path.append(dir(path[0]))
import sqlalchemy as sq
import json
from pathlib import Path
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from db.models import User, Favorite, User_Favorite, create_tables
def create_connection(user_name, password, host_name, port, db_name):
    DSN = f'postgresql://{user_name}:{password}@{host_name}:{port}/{db_name}'
    return DSN

class Create:
    def __init__(self):
        pass
    def add_data_to_db(self, data):
        for record in data:
            session.add(User(vk_id=record.get('id'),
                        f_name=record.get('first_name'),
                        l_name=record.get('last_name'),
                        profile_link=record.get('link'),
                        hometown=record.get('home_town'),
                        photo1=record.get('photos')[0]['url'],
                        photo2=record.get('photos')[1]['url'],
                        photo3=record.get('photos')[2]['url'],
            )
        )

    def add_to_favorite(self, data):
        session.add(Favorite(
            vk_id=data.get('id'),
            f_name=data.get('first_name'),
            l_name=data.get('last_name'),
            profile_link=data.get('link'),
            hometown=data.get('home_town'),
            photo1=data.get('photos')[0]['url'],
            photo2=data.get('photos')[1]['url'],
            photo3=data.get('photos')[2]['url'],
        ))



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



Base = declarative_base()
# DSN = create_connection('postgres', 'Admin', 'localhost', 5432, 'VKinder')
DSN = create_connection('postgres', '1', 'localhost', 5432, 'VKinder')
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
# print(users_info_for_bot)
session.close()
