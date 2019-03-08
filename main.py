from models import *


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Smoke - Main', session=session)


@app.route('/catalog')
def catalog():
    return render_template('catalog.html', title='Smoke - Catalog', session=session)


if __name__ == '__main__':
    app.run('127.0.0.1', port=8080)