import mysql.connector.errors
from flask import Flask, request, Response, session, render_template, redirect, url_for
import SQL
from helpers import login, get_table_column_names
app = Flask(__name__)
app.secret_key = '\x10Y\xde\xb6|R\xd4,\xb8j\xd76\x1cWD\x08\x19P\xcb;{\xb8\x1d\n'
resp = Response()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_money = SQL.db_get_money(session.get('username'))
        count = SQL.db_get_product(request.form.get('id'))[3]
        if user_money >= int(count):
            SQL.db_change_user_money(session.get('username'), user_money - int(count))
            session['money'] = user_money-int(count)
            return render_template('index.html', products=SQL.db_get_all_elements('products'))
        else:
            return render_template('index.html', err="This item is too expensive for you!",
                                   products=SQL.db_get_all_elements('products'))
    else:
        return render_template('index.html', products=SQL.db_get_all_elements('products'))


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
            if SQL.db_add_user(request.form.get('username'), request.form.get('password')) != 'Duplicate':
                login(request.form.get('username'), request.form.get('password'), request.form.get('remember'))
                return redirect(url_for('index'))
            else:
                return render_template('register.html', err='This nickname already taken')
        else:
            return render_template('register.html', err='Passwords are not equal')
    else:
        return render_template('register.html', err=None)


@app.route('/admin/<table_name>', methods=['GET', 'POST'])
def admin(table_name='users'):
    if request.method == 'POST':
        if request.form.get('command') and session.get('privilege') == 1:
            result = SQL.db_execute(request.form.get('command'))
            if type(result) is list:
                return render_template('admin.html', items=result, page=table_name)
            if type(result) is mysql.connector.errors.ProgrammingError:
                return render_template('admin.html', items=SQL.db_get_all_elements(table_name),
                                       columns=get_table_column_names(table_name), err=result, page=table_name)
            else:
                return render_template('admin.html', items=SQL.db_get_all_elements(table_name),
                                       columns=get_table_column_names(table_name), other=result, page=table_name)
    return render_template('admin.html', items=SQL.db_get_all_elements(table_name),
                           columns=get_table_column_names(table_name), page=table_name)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        if request.form.get('new_password') == request.form.get('confirm_password') and request.form.get(
                'new_password'):
            if SQL.db_get_user(session.get('username'), request.form.get('old_password')):
                SQL.db_change_user_password(session.get('username'), request.form.get('new_password'))
                return render_template('settings.html', result='Ok')
            else:
                return render_template('settings.html', err='Old password is incorrect')
        else:
            return render_template('settings.html', err='Passwords are not equal')
    else:
        return render_template('settings.html')


@app.route('/funds', methods=['GET', 'POST'])
def funds():
    if request.method == 'POST':
        fund_code = request.form.get('fund')
        if SQL.db_find_key(fund_code):
            money = list(SQL.db_find_key(fund_code)[0])[2]
            SQL.db_remove_key(fund_code)
            SQL.db_change_user_money(session.get('username'), int(session.get('money')) + int(money))
            SQL.db_add_key(money)
            session['money'] = int(session.get('money')) + int(money)
            return render_template('funds.html', res='Added {}'.format(money))
        else:
            return render_template('funds.html', err='Unknown code')
    return render_template('funds.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port='777')
    SQL.shop_db.disconnect()
