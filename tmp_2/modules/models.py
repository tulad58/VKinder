# createdb -U postgres Coursework_2
# dropdb -U postgres Coursework_2
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Founds(Base):
    __tablename__ = "founds"

    id = sq.Column(sq.Integer, primary_key=True)
    id_vk = sq.Column(sq.Integer, unique=True)
    link = sq.Column(sq.String, unique=True)
    first_name = sq.Column(sq.String(length=40), nullable=False)
    last_name = sq.Column(sq.String(length=40), nullable=False)
    pfoto = sq.Column(sq.Text, nullable=False)

# ===========================================================

def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
# ===========================================================
