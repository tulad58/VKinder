from sqlalchemy import ForeignKey
from sqlalchemy.orm import declarative_base, relationship, as_declarative, mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr

Base = declarative_base()


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@as_declarative()
class AbstractModel:

    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class MainUser(Base, AbstractModel):
    __tablename__ = "main_user"

    vk_id: Mapped[int] = mapped_column(nullable=False, unique=True)

    children: Mapped[list["User"]] = relationship(back_populates="parents", secondary="favorite")
    child_associations: Mapped[list["Favorite"]] = relationship(back_populates="parent", overlaps="children")

    def __str__(self):
        return f"{self.id},{self.vk_id}"


class User(Base, AbstractModel):
    __tablename__ = "user"

    vk_id: Mapped[int] = mapped_column(nullable=False)
    profile_link: Mapped[str] = mapped_column(nullable=False)
    f_name: Mapped[str] = mapped_column(nullable=False)
    l_name: Mapped[str] = mapped_column(nullable=False)
    photo1: Mapped[str] = mapped_column(nullable=False)
    photo2: Mapped[str] = mapped_column(nullable=False)
    photo3: Mapped[str] = mapped_column(nullable=False)
    hometown: Mapped[str] = mapped_column(nullable=False)
    main_user_id: Mapped[int] = mapped_column(ForeignKey("main_user.id"), nullable=True)

    parents: Mapped[list["MainUser"]] = relationship(back_populates="children",
                                                     secondary="favorite",
                                                     overlaps="child_associations")
    parent_associations: Mapped[list["Favorite"]] = relationship(back_populates="child",
                                                                 overlaps="children,parents")

    def __str__(self):
        return f'User {self.id}: (f_name: {self.f_name}, l_name: {self.l_name}, vk_id: {self.vk_id}, profile_link:' \
               f' {self.profile_link}, hometown: {self.hometown}, photos: {self.photo1}, {self.photo2}, {self.photo3})'


class Favorite(Base, AbstractModel):
    __tablename__ = "favorite"

    main_user_id: Mapped[int] = mapped_column(ForeignKey("main_user.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    child: Mapped["User"] = relationship(back_populates="parent_associations", overlaps="children,parents")
    parent: Mapped["MainUser"] = relationship(back_populates="child_associations", overlaps="children,parents")

    def __str__(self):
        return f'vk_id: {self.vk_id}, profile_link: {self.profile_link}, photo: {self.photo}'


class BlackList(Base, AbstractModel):
    __tablename__ = "black_list"

    vk_id: Mapped[int] = mapped_column(nullable=False, unique=False)
    profile_link: Mapped[str] = mapped_column(nullable=False)
    photo: Mapped[str] = mapped_column(nullable=False)

    def __str__(self):
        return f'vk_id: {self.vk_id}, profile_link: {self.profile_link}, photo: {self.photo}'
