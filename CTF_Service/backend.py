from flask import Flask, render_template, url_for, request, redirect
app = Flask(__name__)


def login(username, password):
    print("Username: {} Pass: {}".format(username, password))
    return redirect(url_for('index'))


def add_user(username, password):
    pass


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
        return render_template('auth.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form.get('password') == request.form.get('cpassword') and request.form.get('cpassword') != '':
            add_user(request.form.get('username'), request.form.get('password'))
            login(request.form.get('username'), request.form.get('password'))
            return redirect(url_for('index'))
    else:
        return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True, port='777')