import mysql.connector.errors
from mysql.connector import connect, Error
from flask import url_for
from json import loads
from os import urandom
from hashlib import md5

sql_conf = loads(open('SQLConf.json', 'r').read())


def shop_db_connect():
    try:
        connection = connect(
            host=sql_conf.get('host'),
            user=sql_conf.get('user'),
            password=sql_conf.get('password'),
            database='shop')
        return connection
    except Error as e:
        if e.errno == 1049:
            connection = connect(
                host=sql_conf.get('host'),
                user=sql_conf.get('user'),
                password=sql_conf.get('password'))
            connection.autocommit = True
            with connection.cursor() as cursor:
                command = (
                    '''
                    CREATE DATABASE shop;
                    USE shop;
                    CREATE TABLE users(id INT AUTO_INCREMENT PRIMARY KEY,login VARCHAR(16) UNIQUE,pass VARCHAR(32),
                    privilege INT,money INT);
                    INSERT INTO users (login, pass, privilege, money) VALUES ('admin', 'admin', 1, 30000);
                    USE shop;
                    CREATE TABLE codes (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(32), value INT);
                    CREATE TABLE products (id INT AUTO_INCREMENT PRIMARY KEY, description VARCHAR(32), img VARCHAR(64),
                     value INT);
                    INSERT INTO products (description, img, value) VALUES ('Neo', 'static/neo.jpg', 310);
                    INSERT INTO products (description, img, value) VALUES ('Triniti', 'static/triniti.jpg', 270);
                    INSERT INTO products (description, img, value) VALUES ('Morpheus', 'static/morpheus.jpg', 300);
                    '''
                )
                cursor.execute(command, multi=True).send(None)
                insert_codes = 'INSERT INTO codes(code, value) VALUES '
                values = [10, 100, 150, 300, 500, 1000]
                for value in values:
                    for i in range(0, 10):
                        insert_codes += str((md5(urandom(32)).hexdigest(), value)) + ','
                cursor.execute(insert_codes[:-1], multi=True).send(None)
                return connection


shop_db = shop_db_connect()


def db_execute(command):
    try:
        with shop_db.cursor() as cursor:
            cursor.execute(command)
            res = cursor.fetchall()
            shop_db.commit()
            return res
    except Error as e:
        return e


def db_add_user(username, password):
    try:
        create_account = """
            INSERT INTO users (login, pass, privilege, money)
            VALUES
            (%(username)s, %(password)s, 0, 0)
            """  # WARNING, MAY BE UNSAFETY, NEED TESTS!!!
        with shop_db.cursor() as cursor:
            cursor.execute(create_account, {'username': username, 'password': password})
            shop_db.commit()
    except Error as e:
        if e.errno == 1062:
            return 'Duplicate'
        else:
            print(e)


def db_get_user(username, password):
    try:
        find = """
             SELECT * FROM users WHERE (login=%(username)s AND pass=%(password)s)
               """  # WARNING, MAY BE UNSAFETY, NEED TESTS!!!
        with shop_db.cursor() as cursor:
            cursor.execute(find, {'username': username, 'password': password})
            return cursor.fetchall()
    except Error as e:
        print(e)


def db_get_product(identification_digit):
    try:
        find = """
        SELECT * FROM products WHERE (id=%(id)s)
        """
        with shop_db.cursor() as cursor:
            cursor.execute(find, {'id': identification_digit})
            return cursor.fetchone()
    except Error as e:
        print(e)


def db_get_money(username):
    try:
        find = """
             SELECT * FROM users WHERE login=%(username)s
               """  # WARNING, MAY BE UNSAFETY, NEED TESTS!!!
        with shop_db.cursor() as cursor:
            cursor.execute(find, {'username': username})
            return list(cursor.fetchall()[0])[4]
    except Error as e:
        print(e)


def db_change_user_password(username, password):
    try:
        change = """
        UPDATE users
        SET pass = %(password)s
        WHERE login = %(username)s
        """  # WARNING, MAY BE UNSAFETY, NEED TESTS!!!
        with shop_db.cursor() as cursor:
            cursor.execute(change, {'username': username, 'password': password})
            shop_db.commit()
    except Error as e:
        print(e)


def db_change_user_money(username, money):
    try:
        change = """
        UPDATE users
        SET money = %(money)s
        WHERE login = %(username)s
        """  # WARNING, MAY BE UNSAFETY, NEED TESTS!!!
        with shop_db.cursor() as cursor:
            cursor.execute(change, {'username': username, 'money': money})
            shop_db.commit()
    except Error as e:
        print(e)


def db_get_all_elements(table_name):
    try:
        find = """
            SELECT * FROM {}
            """.format(table_name)
        with shop_db.cursor() as cursor:
            cursor.execute(find)
            return cursor.fetchall()
    except Error as e:
        print(e)


def db_add_key(value):
    try:
        add_key = """
        INSERT INTO codes (code, value) VALUES (%(key)s, %(value)s);
        """
        with shop_db.cursor() as cursor:
            cursor.execute(add_key, {'key': md5(urandom(32)).hexdigest(), 'value': value})
            shop_db.commit()
    except Error as e:
        print(e)


def db_find_key(key):
    try:
        find_key = """
        SELECT * FROM codes WHERE code=%(key)s
        """
        with shop_db.cursor() as cursor:
            cursor.execute(find_key, {'key': key})
            res = cursor.fetchall()
            return res
    except Error as e:
        print(e)


def db_remove_key(key):
    try:
        remove = """
        DELETE FROM codes WHERE code=%(key)s
        """
        with shop_db.cursor() as cursor:
            cursor.execute(remove, {'key': key})
            shop_db.commit()
    except Error as e:
        print(e)


def db_get_table_columns(table_name):
    try:
        get_columns = """
        SHOW COLUMNS FROM {}
        """.format(table_name)
        with shop_db.cursor() as cursor:
            cursor.execute(get_columns)
            res = cursor.fetchall()
            return res
    except Error as e:
        print(e)
