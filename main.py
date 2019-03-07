from flask import Flask, render_template, session


app = Flask(__name__)
app.secret_key = 'F@iL0V3R_c1u5TeR'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Smoke - Главная', session=session)


if __name__ == '__main__':
    app.run('127.0.0.1', port=8080)