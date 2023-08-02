import sqlalchemy as sq
import json
from pathlib import Path
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from models import User, Favorite, User_Favorite, create_tables

def create_connection(user_name, password, host_name, port, db_name):
    DSN = f'postgresql://{user_name}:{password}@{host_name}:{port}/{db_name}'
    return DSN


def add_dict_to_db(data):
    for record in data:
        session.add(User(vk_id=record.get('id'),
                    f_name=record.get('first_name'),
                    l_name=record.get('last_name'),
                    profile_link=record.get('link'),
                    photo1=record.get('photos')[0]['url']
        )
    )


def get_data_json(route):
    p = Path(route)
    with open(p, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data


Base = declarative_base()
DSN = create_connection('postgres', 'Admin', 'localhost', 5432, 'VKinder')
engine = sq.create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()
data = get_data_json('..\\data.json')
add_dict_to_db(data)
session.commit()
session.close()