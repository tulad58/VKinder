import sqlalchemy as sq
import enum
from sqlalchemy import Enum
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

def create_connection(user_name, password, host_name, port, db_name):
    DSN = f'postgresql://{user_name}:{password}@{host_name}:{port}/{db_name}'
    return DSN

def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

class MyEnum(enum.Enum):
    male = 1
    female = 2

class User(Base):
    __tablename__ = "user"

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, unique=True, nullable=False)
    f_name = sq.Column(sq.String(length=20), nullable=False)
    l_name = sq.Column(sq.String(length=20))
    age = sq.Column(sq.Integer)
    hometown = sq.Column(sq.String(length=1000))
    sex = sq.Column(Enum(MyEnum))
    profile_link = sq.Column(sq.String(length=60), nullable=False, unique=True)
    photo1 = sq.Column(sq.String(length=300), nullable=False)
    photo2 = sq.Column(sq.String(length=300), nullable=False)
    photo3 = sq.Column(sq.String(length=300), nullable=False)


    def __str__(self):
        return f'User {self.id}: (f_name: {self.f_name}, l_name: {self.l_name}, vk_id: {self.vk_id}, age: {self.age}, \
        hometown: {self.hometown}, sex: {self.sex}, photos: {self.photo1}, {self.photo2}, {self.photo3})'

    def __init__(self, vk_id, f_name, l_name, hometown, profile_link, photo1, photo2, photo3):
        self.vk_id = vk_id,
        self.f_name = f_name,
        self.l_name = l_name,
        self.hometown = hometown
        self.profile_link = profile_link
        self.photo1 = photo1
        self.photo2 = photo2
        self.photo3 = photo3

class Favorite(Base):
    __tablename__ = 'favorite'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    profile_link = sq.Column(sq.String(length=60), nullable=False, unique=True)
    photo = sq.Column(sq.String(length=300), nullable=False)

    def __init__(self, vk_id, profile_link, photo):
        self.vk_id = vk_id,
        self.profile_link = profile_link
        self.photo = photo

    def __str__(self):
        return f'vk_id: {self.vk_id}, profile_link: {self.profile_link}, photo: {self.photo}'

class BlackList(Base):
    __tablename__ = 'black_list'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    profile_link = sq.Column(sq.String(length=60), nullable=False, unique=True)
    photo = sq.Column(sq.String(length=300), nullable=False)

    def __init__(self, vk_id, profile_link, photo):
        self.vk_id = vk_id,
        self.profile_link = profile_link
        self.photo = photo

    def __str__(self):
        return f'vk_id: {self.vk_id}, profile_link: {self.profile_link}, photo: {self.photo}'
