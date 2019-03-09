from models import *
from flask import redirect


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Smoke - Main', session=session)


@app.route('/catalog/<int:page>')
def catalog(page):
    page -= 1
    length = len(Software.query.all())
    if page < 0 or page * 10 > len(Software.query.all()):
        return redirect('/catalog/1)', 400)
    products = Software.query.filter(Software.id >= page * 10).limit(10).all()
    return render_template('catalog.html', title='Smoke - Catalog',
                           products=products, page=page, length=length)


if __name__ == '__main__':
    app.run('127.0.0.1', port=8080)