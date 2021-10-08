import SQL
from flask import session, render_template, redirect, url_for
from os import urandom


def login(username, password, remember):
    user = SQL.db_get_user(username, password)
    if not user:
        return render_template('auth.html', err="Err")
    else:
        if remember:
            session.permanent = True
        session['username'] = user[1]
        session['privilege'] = user[3]
        session['money'] = user[4]
        return redirect(url_for('index'))


def gen_new_key(value):
    SQL.db_add_key(urandom(32), value)


def get_table_column_names(table_name):
    columns = SQL.db_get_table_columns(table_name)
    names = []
    for column in columns:
        names.append(column[0])
    return names
