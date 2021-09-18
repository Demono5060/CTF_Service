from SQL import *
from flask import session, render_template, redirect, url_for


def login(username, password, remember):
    user = db_get_user(username, password)
    if not user:
        return render_template('auth.html', err="Err")
    else:
        user = list(user[0])
        if remember:
            session.permanent = True
        session['username'] = user[1]
        session['privilege'] = user[3]
        session['money'] = user[4]
        return redirect(url_for('index'))
