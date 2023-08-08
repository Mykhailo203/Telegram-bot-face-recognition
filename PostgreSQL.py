import psycopg2
from config import host, user, db_name, password

conn = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name)

cursor = conn.cursor()


def execute(query: str, data: tuple):
    cursor.execute(query, data)
    conn.commit()


def select(query: str, data: tuple):
    cursor.execute(query, data)
    res = cursor.fetchall()
    print(res)
    return res


def select2(query: str, data: tuple):
    cursor.execute(query, data)
    res = cursor.fetchall()
    print(res)
    return res