from models import *
from forms import *
from sqlalchemy.exc import IntegrityError


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Smoke - Main', session=session)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data,
                        email=form.email.data,
                        password_hash=generate_password_hash(form.password.data),
                        account_type=form.account_type.data)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            return render_template('register.html', title='Smoke - Register',
                                   form=form,
                                   errors=['Another user with this email/username already exists!'])
        else:
            session['user_id'] = user.id
            return redirect('/index')
    return render_template('register.html', title='Smoke - Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                return redirect('/index')
            else:
                return render_template('login.html',
                                       title='Smoke - Login',
                                       form=form,
                                       errors=['Incorrect password'])
        else:
            return render_template('login.html',
                                   title='Smoke - Login',
                                   form=form,
                                   errors=['No such user found!'])
    return render_template('login.html', title='Smoke - Login',
                           form=form)


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
