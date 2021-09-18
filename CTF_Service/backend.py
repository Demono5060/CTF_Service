import mysql.connector.errors
from flask import Flask, request, Response
from helpers import *
app = Flask(__name__)
app.secret_key = '\x10Y\xde\xb6|R\xd4,\xb8j\xd76\x1cWD\x08\x19P\xcb;{\xb8\x1d\n'
resp = Response()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_money = db_get_money(session.get('username'))
        if user_money >= int(request.form.get('price')):
            db_change_user_money(session.get('username'), user_money - int(request.form.get('price')))
            session['money'] = user_money-int(request.form.get('price'))
            return render_template('index.html')
        else:
            return render_template('index.html', err="This item is too expensive for you!")
    else:
        return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        login(request.form.get('username'), request.form.get('password'), request.form.get('remember'))
        return redirect(url_for('index'))
    else:
        return render_template('auth.html', err=None)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form.get('password') == request.form.get('cpassword') and request.form.get('cpassword') != '':
            if db_add_user(request.form.get('username'), request.form.get('password')) != 'Duplicate':
                login(request.form.get('username'), request.form.get('password'), request.form.get('remember'))
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
    session.clear()
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
