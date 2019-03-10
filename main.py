from models import *
from forms import *
from sqlalchemy.exc import IntegrityError


@app.route('/')
@app.route('/index')
def index():
    logged_in = 'username' in session
    return render_template('index.html', title='Smoke - Main',
                           logged_in=logged_in)


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
            session['username'] = user.username
            return redirect('/index')
    return render_template('register.html', title='Smoke - Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                session['user_id'] = user.id
                session['username'] = user.username
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


@app.route('/logout')
def logout():
    try:
        session.pop('user_id')
        session.pop('username')
    except KeyError:
        pass
    return redirect('/index')


@app.route('/catalog')
def catalog():
    logged_in = 'username' in session
    if logged_in:
        acc_type = User.query.get(session['user_id']).account_type
    else:
        acc_type = 'def'
    products = Software.query.all()
    return render_template('catalog.html', title='Smoke - Catalog',
                           products=products,
                           logged_in=logged_in,
                           account_type=acc_type)


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


@app.route('/product/<int:id>/news')
def all_news(id):
    logged_in = 'username' in session
    if logged_in:
        is_developer = Software.query.get(id).user_id == session['user_id']
    else:
        is_developer = False
    if Software.query.get(id):
        return render_template('news.html',
                               product=Software.query.get(id),
                               news=Software.query.get(id).news,
                               is_developer=is_developer,
                               logged_in=logged_in)
    else:
        return abort(404)


@app.route('/product/<int:product_id>/news/<int:news_id>')
def news(product_id, news_id):
    logged_in = 'username' in session
    if logged_in:
        user_id = session['user_id']
        is_developer = Software.query.get(product_id).user_id == user_id
    else:
        user_id = -1
        is_developer = False
    if Software.query.get(product_id):
        return render_template('onenews.html',
                               product=Software.query.get(product_id),
                               news=News.query.get(news_id),
                               is_developer=is_developer,
                               logged_in=logged_in,
                               user_id=user_id)


@app.route('/product/<int:product_id>/news/add_news', methods=['GET', 'POST'])
def add_news(product_id):
    form = AddNewsForm()
    product = Software.query.get(product_id)
    if form.validate_on_submit():
        news = News(software_id=product_id,
                    title=form.title.data,
                    body=form.body.data)
        db.session.add(news)
        db.session.commit()
        return redirect('/product/{}/news'.format(product_id))
    if product:
        logged_in = 'username' in session
        if logged_in:
            user = User.query.get(session['user_id'])
            if user.id == product.user_id:
                return render_template('add_news.html', title='Smoke - Add News',
                                       logged_in=logged_in,
                                       form=form)
            return abort(403)
        return abort(403)
    return abort(404)


@app.route('/add_software', methods=['GET', 'POST'])
def add_software():
    logged_in = 'username' in session
    form = AddSoftwareForm()
    if form.validate_on_submit():
        errors = []
        if len(form.title.data) > 100:
            errors.append('Title is too long! Max length - 100 symbols')
        if len(form.description.data) > 1000:
            errors.append('Description is too long! Max length - 1000 symbols')
        if errors:
            return render_template('add_software.html',
                                   title='Smoke - Add Software',
                                   logged_in=logged_in,
                                   form=form,
                                   errors=errors)
        else:
            software = Software(title=form.title.data,
                                description=form.description.data,
                                link=form.link.data)
            screenshots = form.screenshots.data.split('\n')
            for screenshot in screenshots:
                caption, description, link = screenshot.split(';')
                software.screenshots.append(Screenshot(link=link,
                                                       caption=caption,
                                                       description=description))
            db.session.add(software)
            db.session.commit()
            return redirect('/product/' + str(software.id))
    if logged_in:
        user = User.query.get(session['user_id'])
        if user.account_type == 'dev':
            return render_template('add_software.html',
                                   title='Smoke - Add Software',
                                   logged_in=logged_in,
                                   form=form)
        return abort(403)
    return abort(403)


@app.route('/product/<int:id>/add_review')
def add_review(id):
    form = AddReviewForm()
    logged_in = 'username' in session
    if logged_in:
        user = User.query.get(session['user_id'])
        software = Software.query.get(id)
        if software:
            if software in user.softwares:
                return abort(403)
            if form.validate_on_submit():
                if len(form.body.data) > 1000:
                    return render_template('add_review.html',
                                           title='Smoke - Add Review',
                                           form=form,
                                           logged_in=logged_in,
                                           errors=[
                                               'Your review is too long! Max length - 1000'])
                review = Review(rating=form.rating.data,
                                body=form.body.data,
                                user_id=user.id)
                db.session.add(review)
                db.session.commit()
                return redirect('/product/' + str(id))
            return render_template('add_review.html',
                                   title='Smoke - Add Review',
                                   form=form,
                                   logged_in=logged_in)
        return abort(404)
    return abort(403)


@app.route('/product/<int:product_id>/news/<int:news_id>/add_comment')
def add_comment(product_id, news_id):
    form = AddCommentForm()
    logged_in = 'username' in session
    if logged_in:
        user = User.query.get(session['user_id'])
        news = News.query.get(news_id)
        if news:
            if form.validate_on_submit():
                if len(form.body.data) > 1000:
                    return render_template('add_comment.html',
                                           title='Smoke - Add Comment',
                                           form=form,
                                           logged_in=logged_in,
                                           errors=[
                                               'Your comment is too long! Max length - 1000'])
                comment = Comment(body=form.body.data,
                                  user_id=user.id)
                db.session.add(comment)
                db.session.commit()
                return redirect('/product/{}/news/{}'.format(product_id, news_id))
            return render_template('add_comment.html',
                                   title='Smoke - Add Comment',
                                   form=form,
                                   logged_in=logged_in)
        return abort(404)
    return abort(403)


@app.route('/delete_comment/<int:id>')
def delete_comment(id):
    comment = Comment.query.get(id)
    if comment:
        logged_in = 'username' in session
        if logged_in:
            user = User.query.get(session['user_id'])
            news = comment.news
            if user.id == comment.user_id:
                db.session.delete(comment)
                db.session.commit()
                return redirect('/product/{}/news/{}'.format(news.software_id, news.id))
            return abort(403)
        return abort(403)
    return abort(404)


@app.route('/delete_news/<int:id>')
def delete_news(id):
    news = News.query.get(id)
    if news:
        product_id = news.software_id
        logged_in = 'username' in session
        if logged_in:
            user = User.query.get(session['user_id'])
            if news in user.news:
                db.session.delete(news)
                db.session.commit()
                return redirect('/product/{}/news'.format(product_id))
            return abort(403)
        return abort(403)
    return abort(404)


@app.route('/delete_software/<int:id>')
def delete_software(id):
    software = Software.query.get(id)
    if software:
        logged_in = 'username' in session
        if logged_in:
            user = User.query.get(session['user_id'])
            if software in user.softwares:
                db.session.delete(software)
                db.session.commit()
            return abort(403)
        return abort(403)
    return abort(404)


@app.route('/delete_review/<int:id>')
def delete_review(id):
    review = Review.query.get(id)
    if review:
        logged_in = 'username' in session
        if logged_in:
            user = User.query.get(session['user_id'])
            if review in user.reviews:
                product_id = review.software_id
                db.session.delete(review)
                db.session.commit()
                return redirect('/product/' + str(product_id))
            return abort(403)
        return abort(403)
    return abort(404)


@app.errorhandler(404)
def page_not_found(error):
    logged_in = 'username' in session
    return render_template('not_found.html', title='Smoke - 404',
                           logged_in=logged_in)


@app.errorhandler(403)
def not_allowed(error):
    logged_in = 'username' in session
    return render_template('not_allowed.html', title='Smoke - 403',
                           logged_in=logged_in)

@app.route('/403')
def not_allowed_check():
    return abort(403)


if __name__ == '__main__':
    app.run('127.0.0.1', port=8080)
