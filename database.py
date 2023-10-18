import sqlite3 as sl
import random


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def start_db():
    con = sl.connect('test.db')
    # открываем базу
    with con:
        # получаем количество таблиц с нужным нам именем
        data = con.execute("select count(*) from sqlite_master where type='table' and name='users'")
        for row in data:
            # если таких таблиц нет
            if row[0] == 0:
                # создаём таблицу для товаров
                with con:
                    con.execute("""
                        CREATE TABLE users (
                            chatid VARCHAR(20) NOT NULL UNIQUE,
                            name VARCHAR(100),
                            term1 BOOLEAN,
                            term2 BOOLEAN,
                            term3 BOOLEAN
                        );
                    """)

    # выводим содержимое таблицы на экран
    with con:
        data = con.execute("SELECT * FROM users")
        for row in data:
            print(row)


def create(message):
    con = sl.connect('test.db')
    sql = 'INSERT INTO users (chatid, name, term1, term2, term3) values(?, ?, ?, ?, ?)'

    # chatid = str(message.from_user.id)
    chatid = random.randint(1, 1000)

    name = str(message.from_user.username)

    data = [
        (chatid, name, False, False, False)
    ]

    # добавляем с помощью запроса данные
    with con:
        con.executemany(sql, data)


def is_existed(message):
    con = sl.connect('test.db')
    cur = con.cursor()

    chatid = str(message.from_user.id)
    sql = f'SELECT COUNT(*) FROM users WHERE users.chatid = {chatid}'

    with con:
        cur.execute(sql)
        records = cur.fetchall()
        print(records, records[0][0])
        if records[0][0] == 0:
            print('NOT EXIST')
            return 0
        else:
            return 1


def list_users(term=None):
    con = sl.connect('test.db')
    con.row_factory = dict_factory
    cur = con.cursor()

    if term is None:
        sql = 'SELECT * FROM users '

        with con:
            cur.execute(sql)
            records = cur.fetchall()
            print(records)
            return records
    else:

        if not term in ['term1', 'term2', 'term3']:
            print('NOT available TERM')

        sql = f'SELECT * FROM users WHERE {term} = TRUE'
        cur.execute(sql)
        records = cur.fetchall()
        print(records)
        return records


def get_user(message):
    con = sl.connect('test.db')
    con.row_factory = dict_factory
    cur = con.cursor()

    chatid = str(message.from_user.id)
    sql = f'SELECT * FROM users WHERE users.chatid = {chatid}'

    with con:
        cur.execute(sql)
        records = cur.fetchall()
        print(records)
        return records[0]


def update_term(message, term):
    con = sl.connect('test.db')
    con.row_factory = dict_factory
    cur = con.cursor()

    user = get_user(message)
    if term in user:
        chatid = str(message.from_user.id)

        b = user[term]
        if b == 1:
            b = False
        else:
            b = True
        sql = f'UPDATE users SET {term} = {b} WHERE chatid = {chatid}'

        with con:
            cur.execute(sql)
            print("Successfully updated")
            return True
    else:
        raise ValueError(f'TERM {term} NOT EXIST')



if __name__ == '__main__':
    start_db()