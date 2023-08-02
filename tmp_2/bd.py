
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
import json
# from pprint import pprint
import configparser
from modules.models import create_tables, Founds

# with open('found.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)

# Получение DSN из файла ini:
config = configparser.ConfigParser()
config.read('configs/DSN.ini')
dsn = config['DSN']['BD']

engine = sq.create_engine(dsn)  # создание движка
print(dsn)

# создание класса подключения к БД (сессии) через engin
Session = sessionmaker(bind=engine)
session = Session()  # создание экземпляра класса для работы

# if __name__ == '__main__':
#     create_tables(engine)  # создание таблиц движком (импортированная функция из модуля models.py)
#     session.close()  # закрытие сессии
