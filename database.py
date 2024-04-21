import os
import sqlite3 as sl
from functools import wraps
from datetime import date

# Take the token from the .env file
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Take path of database
DATAPATH = os.environ["DATAPATH"]


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect_db(func):
    """Декоратор подключения и отключения БД"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sl.connect(DATAPATH)
        result = func(conn=conn, *args, **kwargs)
        conn.close()
        return result
    return wrapper


@connect_db
def start_db(conn):
    # открываем базу
    with conn:
        # получаем количество таблиц с нужным нам именем
        data = conn.execute("select count(*) from sqlite_master where type='table' and name='users'")
        for row in data:
            # если таких таблиц нет
            if row[0] == 0:
                # создаём таблицу для пользователей
                with conn:
                    conn.execute("""
                        CREATE TABLE users (
                            chatid VARCHAR(20) NOT NULL UNIQUE,
                            username VARCHAR(50),
                            name VARCHAR(100),
                            lastname VARCHAR(100),
                            registrationdate VARCHAR(20),
                            
                            is_blocked BOOLEAN,
                            
                            exhibition BOOLEAN,
                            meeting BOOLEAN,
                            educational BOOLEAN,
                            science BOOLEAN,
                            career BOOLEAN,
                            networking BOOLEAN,
                            forum BOOLEAN
                        );
                    """)

    # выводим содержимое таблицы на экран
    with conn:
        data = conn.execute("SELECT * FROM users")
        for row in data:
            print(row)


@connect_db
def create(message, conn=None):
    chatid = str(message.from_user.id)
    username = str(message.from_user.username)
    name = str(message.from_user.first_name)
    lastname = str(message.from_user.last_name)
    registrationdate = str(date.today())

    request = 'INSERT INTO users (chatid, username, name, lastname, registrationdate, is_blocked, ' \
              'exhibition, meeting, educational, science, career, networking, forum) ' \
              'values(?, ?, ?, ?, ?, ?,' \
              ' ?, ?, ?, ?, ?, ?, ?)'
    data = [
        (chatid, username, name, lastname, registrationdate, False, True, True, True, True, True, True, True)
    ]

    # добавляем с помощью запроса данные
    with conn:
        conn.executemany(request, data)
    return get_user(message)


@connect_db
def is_existed(message, conn=None):
    cur = conn.cursor()

    chatid = str(message.from_user.id)
    sql = f'SELECT COUNT(*) FROM users WHERE users.chatid = {chatid}'

    with conn:
        cur.execute(sql)
        records = cur.fetchall()
        print(records, len(records), records[0][0] == 0)
        if records[0][0] == 0:
            print('NOT EXIST')
            return 0
        else:
            return 1


@connect_db
def list_users(term=None, conn=None):
    conn.row_factory = dict_factory
    cur = conn.cursor()

    if term is None:
        sql = 'SELECT * FROM users '

        with conn:
            cur.execute(sql)
            records = cur.fetchall()
            return records
    else:

        if not term in ['exhibition', 'meeting', 'educational', 'science', 'career', 'networking', 'forum']:
            print('NOT available TERM')

        sql = f'SELECT * FROM users WHERE {term} = TRUE'
        cur.execute(sql)
        records = cur.fetchall()
        return records


@connect_db
def get_user(message, conn=None):
    conn.row_factory = dict_factory
    cur = conn.cursor()

    chatid = str(message.from_user.id)
    sql = f'SELECT * FROM users WHERE users.chatid = {chatid}'

    with conn:
        cur.execute(sql)
        records = cur.fetchall()
        print(records)
        return records[0]


@connect_db
def get_user_from_chatid(chatid, conn=None):
    conn.row_factory = dict_factory
    cur = conn.cursor()

    sql = f'SELECT * FROM users WHERE users.chatid = {chatid}'

    with conn:
        cur.execute(sql)
        records = cur.fetchall()
        print(records)
        return records[0]


@connect_db
def update_term(message, term, conn=None):
    conn.row_factory = dict_factory
    cur = conn.cursor()

    user = get_user(message)
    if term in user:
        chatid = str(message.from_user.id)

        b = user[term]
        if b == 1:
            b = False
        else:
            b = True
        sql = f'UPDATE users SET {term} = {b} WHERE chatid = {chatid}'

        with conn:
            cur.execute(sql)
            print("Successfully updated")
            return True
    else:
        raise ValueError(f'TERM {term} NOT EXIST')


@connect_db
def update_term(user, term, conn=None):
    conn.row_factory = dict_factory
    cur = conn.cursor()
    if term in user:
        chatid = str(user['chatid'])

        b = user[term]
        if b == 1:
            b = False
        else:
            b = True
        sql = f'UPDATE users SET {term} = {b} WHERE chatid = {chatid}'

        with conn:
            cur.execute(sql)
            print("Successfully updated")
            return True
    else:
        raise ValueError(f'TERM {term} NOT EXIST')


# @connect_db
# def local_create(conn=None):
#     chatid = ''
#     username = ''
#     name = ''
#     lastname = ''
#     registrationdate = str(date.today())
#
#     request = 'INSERT INTO users (chatid, username, name, lastname, registrationdate, is_blocked, ' \
#               'exhibition, meeting, educational, science, career, networking, forum) ' \
#               'values(?, ?, ?, ?, ?, ?,' \
#               ' ?, ?, ?, ?, ?, ?, ?)'
#     data = [
#         (chatid, username, name, lastname, registrationdate, False, True, True, True, True, True, True, True)
#     ]
#
#     # добавляем с помощью запроса данные
#     with conn:
#         conn.executemany(request, data)


if __name__ == '__main__':
    start_db()
    # local_create()
