import sqlalchemy as sq
import enum
from sqlalchemy import Enum
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, as_declarative, mapped_column, Mapped

Base = declarative_base()


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


class MyEnum(enum.Enum):
    male = 1
    female = 2

@as_declarative()
class AbstractModel:
    id: Mapped[int] = mapped_column(primary_key=True)


class Requester(AbstractModel):
    __tablename__ = "requester"

    requester_id: Mapped[int] = mapped_column(nullable=False, unique=True)

    users: Mapped[list['User']] = relationship(back_populates="requesters")

    def __str__(self):
        return f"{self.id},{self.requester_id}"


class User(AbstractModel):
    __tablename__ = "user"

    vk_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    f_name: Mapped[str] = mapped_column(nullable=False)
    l_name: Mapped[str] = mapped_column(nullable=False)
    hometown: Mapped[str] = mapped_column(nullable=False)
    profile_link: Mapped[str] = mapped_column(nullable=False, unique=True)
    photo1: Mapped[str] = mapped_column(nullable=False)
    photo2: Mapped[str] = mapped_column(nullable=False)
    photo3: Mapped[str] = mapped_column(nullable=False)
    requester_fk: Mapped[int] = mapped_column(sq.ForeignKey("requester.id"))

    requesters: Mapped['Requester'] = relationship(back_populates="users")



    def __str__(self):
        return f'User {self.id}: (f_name: {self.f_name}, l_name: {self.l_name}, vk_id: {self.vk_id}, age: {self.age}, \
        hometown: {self.hometown}, sex: {self.sex}, photos: {self.photo1}, {self.photo2}, {self.photo3} ,requester_id' \
               f'{self.requester_fk})'



# class Favorite(AbstractModel):
#     __tablename__ = 'favorite'
#
#     id = sq.Column(sq.Integer, primary_key=True)
#     vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
#     f_name = sq.Column(sq.String(length=20), nullable=False)
#     l_name = sq.Column(sq.String(length=20))
#     age = sq.Column(sq.Integer)
#     hometown = sq.Column(sq.String(length=20))
#     sex = sq.Column(Enum(MyEnum))
#     profile_link = sq.Column(sq.String(length=60), nullable=False, unique=True)
#     photo1 = sq.Column(sq.String(length=100), nullable=False)
#     photo2 = sq.Column(sq.String(length=60))
#     photo3 = sq.Column(sq.String(length=60))
#     requester = sq.Column(sq.Integer, nullable=False)
#
#
#     def __str__(self):
#         return f'User {self.id}: (f_name: {self.f_name}, l_name: {self.l_name}, vk_id: {self.vk_id}, age: {self.age}, \
#         hometown: {self.hometown}, sex: {self.sex}, profile_link: { self.profile_link},photo: {self.photo1} ' \
#                f'{self.photo2}, {self.photo3}, requsester: {self.requester})'


# class User_Favorite(AbstractModel):
#     __tablename__ = 'user_favorite'
#
#     id = sq.Column(sq.Integer, primary_key=True)
#     user_id = sq.Column(sq.Integer, sq.ForeignKey("user.id"),  nullable=False)
#     favorite_id = sq.Column(sq.Integer, sq.ForeignKey("favorite.id"), nullable=False)
#
#     user = relationship(User, cascade="all,delete", backref="user", passive_deletes=True)
#     favorite = relationship(Favorite, cascade="all,delete", backref="user_favorite", passive_deletes=True)
#
#
#     def __str__(self):
#         return f'User_Favorite id: {self.id} (user_id: {self.user_id}, favorite_id: {self.favorite_id})'
