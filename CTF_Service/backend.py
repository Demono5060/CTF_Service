import mysql.connector.errors
from flask import Flask, render_template, url_for, request, redirect, session
from mysql.connector import connect, Error
from json import loads

app = Flask(__name__)
app.secret_key = '\x10Y\xde\xb6|R\xd4,\xb8j\xd76\x1cWD\x08\x19P\xcb;{\xb8\x1d\n'

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
            with connection.cursor() as cursor:
                cursor.execute('''
                CREATE DATABASE shop;
                ''')
                connection.commit()
                connection.database = 'shop'
                cursor = connection.cursor()
                cursor.execute('''
                CREATE TABLE shop(
                id INT AUTO_INCREMENT PRIMARY KEY,
                login VARCHAR(16) UNIQUE,
                pass VARCHAR(32),
                privilege INT,
                money INT
                );
                ''')
                connection.commit()
                cursor.execute('''
                INSERT INTO shop (login, pass, privilege, money)
                VALUES
                ("admin", 'admin', 1, 30000);
                ''')
                connection.commit()
                return connection


shop_db = shop_db_connect()


def db_create():
    try:
        create_db_query = "CREATE DATABASE shop"
        with shop_db.cursor() as cursor:
            cursor.execute(create_db_query)
    except Error as e:
        print(e)


def db_table_create():
    try:
        create_table_shop = """
            CREATE TABLE shop(
            id INT AUTO_INCREMENT PRIMARY KEY,
            login VARCHAR(16) UNIQUE,
            pass VARCHAR(32),
            privilege INT,
            money INT
            )
            """
        create_admin_account = """
            INSERT INTO shop (login, pass, privilege, money)
            VALUES
            ("admin", 'admin', 1, 30000)
            """
        with shop_db.cursor() as cursor:
            cursor.execute(create_table_shop)
            cursor.execute(create_admin_account)
            shop_db.commit()
    except Error as e:
        print(e)


def db_execute(command):
    try:
        with shop_db.cursor() as cursor:
            cursor.execute(command)
            res = cursor.fetchall()
            shop_db.commit()
            return res
    except Error as e:
        return (e)


def db_add_user(username, password):
    try:
        create_account = """
            INSERT INTO shop (login, pass, privilege, money)
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
             SELECT * FROM shop WHERE (login=%(username)s AND pass=%(password)s)
               """  # WARNING, MAY BE UNSAFETY, NEED TESTS!!!
        with shop_db.cursor() as cursor:
            cursor.execute(find, {'username': username, 'password': password})
            return cursor.fetchall()
    except Error as e:
        print(e)


def db_change_user_password(username, password):
    try:
        change = """
        UPDATE shop
        SET pass = %(password)s
        WHERE login = %(username)s
        """  # WARNING, MAY BE UNSAFETY, NEED TESTS!!!
        with shop_db.cursor() as cursor:
            cursor.execute(change, {'username': username, 'password': password})
            shop_db.commit()
    except Error as e:
        print(e)


def db_get_all_users():
    try:
        find = """
            SELECT * FROM shop
            """
        with shop_db.cursor() as cursor:
            cursor.execute(find)
            return cursor.fetchall()
    except Error as e:
        print(e)


def login(username, password):
    user = db_get_user(username, password)
    if not user:
        return render_template('auth.html', err="Err")
    else:
        user = list(user[0])
        session['username'] = user[1]
        session['privilege'] = user[3]
        session['money'] = user[4]
        return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        login(request.form.get('username'), request.form.get('password'))
        return redirect(url_for('index'))
    else:
        return render_template('auth.html', err=None)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form.get('password') == request.form.get('cpassword') and request.form.get('cpassword') != '':
            if db_add_user(request.form.get('username'), request.form.get('password')) != 'Duplicate':
                login(request.form.get('username'), request.form.get('password'))
                return redirect(url_for('index'))
            else:
                return render_template('register.html', err='This nickname already taken')
        else:
            return render_template('register.html', err='Passwords are not equal')
    else:
        return render_template('register.html', err=None)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('command') and session.get('privilege') == 1:
            result = db_execute(request.form.get('command'))
            if type(result) is list:
                return render_template('admin.html', result=result)
            if type(result) is mysql.connector.errors.ProgrammingError:
                return render_template('admin.html', users=db_get_all_users(), err=result)
            else:
                return render_template('admin.html', users=db_get_all_users(), other=result)
    return render_template('admin.html', users=db_get_all_users())


@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('privilege')
    session.pop('money')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        if request.form.get('new_password') == request.form.get('confirm_password') and request.form.get(
                'new_password'):
            if db_get_user(session.get('username'), request.form.get('old_password')):
                db_change_user_password(session.get('username'), request.form.get('new_password'))
                return render_template('settings.html', result='Ok')
            else:
                return render_template('settings.html', err='Old password is incorrect')
        else:
            return render_template('settings.html', err='Passwords are not equal')
    else:
        return render_template('settings.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port='777')
    shop_db.disconnect()
