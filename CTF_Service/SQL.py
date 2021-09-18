import mysql.connector.errors
from mysql.connector import connect, Error
from json import loads
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
                    '''
                    )
                cursor.execute(command, multi=True).send(None)
                connection.autocommit = False
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


def db_get_all_users():
    try:
        find = """
            SELECT * FROM users
            """
        with shop_db.cursor() as cursor:
            cursor.execute(find)
            return cursor.fetchall()
    except Error as e:
        print(e)
