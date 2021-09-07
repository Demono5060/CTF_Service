from flask import Flask, render_template, url_for, request, redirect, session
from mysql.connector import connect, Error
from json import loads
app = Flask(__name__)
app.secret_key = '\x10Y\xde\xb6|R\xd4,\xb8j\xd76\x1cWD\x08\x19P\xcb;{\xb8\x1d\n'
sql_conf = loads(open('SQLConf.json', 'r').read())


def db_create():
    try:
        with connect(
                host=sql_conf.get('host'),
                user=sql_conf.get('user'),
                password=sql_conf.get('password')
        ) as connection:
            create_db_query = "CREATE DATABASE shop"
            with connection.cursor() as cursor:
                cursor.execute(create_db_query)
    except Error as e:
        print(e)


def db_table_create():
    try:
        with connect(
                host=sql_conf.get('host'),
                user=sql_conf.get('user'),
                password=sql_conf.get('password'),
                database=sql_conf.get('database')
        ) as connection:
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
            with connection.cursor() as cursor:
                cursor.execute(create_table_shop)
                cursor.execute(create_admin_account)
                connection.commit()
    except Error as e:
        print(e)


def db_add_user(username, password):
    try:
        with connect(
                host=sql_conf.get('host'),
                user=sql_conf.get('user'),
                password=sql_conf.get('password'),
                database=sql_conf.get('database')
        )as connection:
            create_account = """
                INSERT INTO shop (login, pass, privilege, money)
                VALUES
                ("{}", '{}', 0, 0)
                """.format(username, password)
            with connection.cursor() as cursor:
                cursor.execute(create_account)
                connection.commit()
    except Error as e:
        if e.errno == 1062:
            return 'Duplicate'
        else:
            print(e)


def db_get_user(username, password):
    try:
        with connect(
                host=sql_conf.get('host'),
                user=sql_conf.get('user'),
                password=sql_conf.get('password'),
                database=sql_conf.get('database')
        )as connection:
            find = """
                SELECT * FROM shop WHERE (login='{}' AND pass='{}')
                """.format(username, password)
            with connection.cursor() as cursor:
                cursor.execute(find)
                return cursor.fetchall()
    except Error as e:
        print(e)


def db_get_all_users():
    try:
        with connect(
                host=sql_conf.get('host'),
                user=sql_conf.get('user'),
                password=sql_conf.get('password'),
                database=sql_conf.get('database')
        )as connection:
            find = """
                SELECT * FROM shop
                """
            with connection.cursor() as cursor:
                cursor.execute(find)
                return cursor.fetchall()
    except Error as e:
        print(e)


def login(username, password):
    user = db_get_user(username, password)
    if not user:
        return 'Incorrect data'
    else:
        return user


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        res = list(login(request.form.get('username'), request.form.get('password'))[0])
        if res == 'Incorrect data':
            return render_template('auth.html', err="Err")
        else:
            session['username'] = res[1]
            session['privilege'] = res[3]
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
    return render_template('admin.html', users = db_get_all_users())

if __name__ == '__main__':
    db_create()
    db_table_create()
    app.run(debug=True, port='777')