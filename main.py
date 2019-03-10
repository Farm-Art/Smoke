from models import *


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Smoke - Main', session=session)


@app.route('/catalog')
def catalog():
    products = Software.query.all()
    return render_template('catalog.html', title='Smoke - Catalog',
                           products=products)


@app.route('/product/<int:id>')
def product_page(id):
    logged_in = 'username' in session
    product = Software.query.get(id)
    if product:
        news = product.news[0] if product.news else None
        return render_template('productpage.html',
                               title='Smoke - {}'.format(product.title),
                               session=session,
                               news=news,
                               logged_in=logged_in)
    else:
        return abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('not_found.html', title='Smoke - 404')


if __name__ == '__main__':
    app.run('127.0.0.1', port=8080)