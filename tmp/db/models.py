import sqlalchemy as sq
import enum
from sqlalchemy import ForeignKey
from sqlalchemy import Enum
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, as_declarative, mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr
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

    @classmethod
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class User(AbstractModel, Base):
    __tablename__ = "user"

    # id: Mapped[int] = mapped_column(primary_key=True)
    vk_id: Mapped[int] = mapped_column(nullable=False, unique=True)

    def __str__(self):
        return f"{self.id},{self.vk_id}"


class Match(AbstractModel, Base):
    __tablename__ = "match"

    # id: Mapped[int] = mapped_column(primary_key=True)
    vk_id: Mapped[int] = mapped_column(nullable=False)
    vk_link: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    photo1: Mapped[str] = mapped_column(nullable=False)
    photo2: Mapped[str] = mapped_column(nullable=False)
    photo3: Mapped[str] = mapped_column(nullable=False)
    home_town: Mapped[str] = mapped_column(nullable=False)

    def __str__(self):
        return f"{self.id}, {self.vk_id}, {self.photo1}, {self.photo2}, {self.photo3}, {self.first_name}," \
               f"{self.last_name}, {self.home_town}"


def drop_everything():
    """(On a live db) drops all foreign key constraints before dropping all tables.
    Workaround for SQLAlchemy not doing DROP ## CASCADE for drop_all()
    (https://github.com/pallets/flask-sqlalchemy/issues/722)
    """
    from sqlalchemy.engine.reflection import Inspector
    from sqlalchemy.schema import DropConstraint, DropTable, MetaData, Table

    con = sq.engine.connect()
    trans = con.begin()
    inspector = Inspector.from_engine(sq.engine)

    # We need to re-create a minimal metadata with only the required things to
    # successfully emit drop constraints and tables commands for postgres (based
    # on the actual schema of the running instance)
    meta = MetaData()
    tables = []
    all_fkeys = []

    for table_name in inspector.get_table_names():
        fkeys = []

        for fkey in inspector.get_foreign_keys(table_name):
            if not fkey["name"]:
                continue

            fkeys.append(sq.ForeignKeyConstraint((), (), name=fkey["name"]))

        tables.append(Table(table_name, meta, *fkeys))
        all_fkeys.extend(fkeys)

    for fkey in all_fkeys:
        con.execute(DropConstraint(fkey))

    for table in tables:
        con.execute(DropTable(table))

    trans.commit()

# drop_everything()
