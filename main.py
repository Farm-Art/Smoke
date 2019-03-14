from models import *
from forms import *
from sqlalchemy.exc import IntegrityError


def check_for_logged_in():
    return User.query.get(session.get('user_id', 0))


def check_for_permission(user, item_id, item_type):
    if user:
        item = item_type.query.get(item_id)
        if item:
            return item
        return 404
    return 403


@app.route('/')
@app.route('/index')
def index():
    user = check_for_logged_in()
    return render_template('index.html', title='Smoke - Main',
                           logged_in=user)


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
            return redirect(url_for('index'))
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
                return redirect(url_for('index'))
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
    return redirect(url_for('index'))


@app.route('/catalog')
def catalog():
    user = check_for_logged_in()
    if user:
        acc_type = user.account_type
    else:
        acc_type = 'def'
    products = Software.query.all()
    return render_template('catalog.html', title='Smoke - Catalog',
                           products=products,
                           logged_in=user,
                           account_type=acc_type)


@app.route('/product/<int:id>')
def product_page(id):
    user = check_for_logged_in()
    product = Software.query.get(id)
    if product:
        reviews = product.reviews
        news = product.news[0] if product.news else None
        return render_template('productpage.html',
                               title='Smoke - {}'.format(product.title),
                               session=session,
                               news=news,
                               logged_in=user,
                               product=product,
                               reviews=reviews)
    else:
        return abort(404)


@app.route('/product/<int:id>/news')
def all_news(id):
    user = check_for_logged_in()
    software = Software.query.get(id)
    if software:
        return render_template('news.html',
                               product=Software.query.get(id),
                               news=Software.query.get(id).news,
                               is_developer=software.user_id == user.id,
                               logged_in=user)
    else:
        return abort(404)


@app.route('/product/<int:product_id>/news/<int:news_id>')
def news(product_id, news_id):
    user = check_for_logged_in()
    software = Software.query.get(product_id)
    if user:
        is_developer = software.user_id == user.id
    else:
        is_developer = False
    software = Software.query.get(product_id)
    if software:
        news = News.query.get(news_id)
        if news:
            return render_template('onenews.html',
                                   product=software,
                                   news=news,
                                   is_developer=is_developer,
                                   logged_in=user,
                                   user_id=user.id,
                                   comments=news.comments)


@app.route('/product/<int:product_id>/news/add_news', methods=['GET', 'POST'])
def add_news(product_id):
    form = AddNewsForm()
    user = check_for_logged_in()
    product = check_for_permission(user, product_id, Software)
    if isinstance(product, int):
        return abort(product)
    if product.user_id == user.id:
        if form.validate_on_submit():
            news = News(software_id=product_id,
                        title=form.title.data,
                        body=form.body.data)
            db.session.add(news)
            db.session.commit()
            return redirect(url_for('all_news', id=product_id))
        return render_template('add_news.html', title='Smoke - Add News',
                                logged_in=user, form=form)


@app.route('/add_software', methods=['GET', 'POST'])
def add_software():
    form = AddSoftwareForm()
    user = check_for_logged_in()
    if user:
        if user.account_type == 'dev':
            if form.validate_on_submit():
                errors = []
                if len(form.title.data) > 100:
                    errors.append('Title is too long! Max length - 100 symbols')
                if len(form.description.data) > 1000:
                    errors.append('Description is too long! Max length - 1000 symbols')
                if errors:
                    return render_template('add_software.html',
                                           title='Smoke - Add Software',
                                           logged_in=user,
                                           form=form,
                                           errors=errors)
                software = Software(user_id=user.id,
                                    title=form.title.data,
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
                    return redirect(url_for('product_page', id=software.id))
                return render_template('add_software.html',
                                       title='Smoke - Add Software',
                                       logged_in=user,
                                       form=form)
            return render_template('add_software.html',
                                   title='Smoke - Add Software',
                                   logged_in=user,
                                   form=form)
        return abort(403)
    return abort(403)


@app.route('/product/<int:id>/add_review', methods=['GET', 'POST'])
def add_review(id):
    form = AddReviewForm()
    user = check_for_logged_in()
    software = check_for_permission(user, id, Software)
    if isinstance(software, int):
        return abort(software)
    if software.user_id != user.id:
        if form.validate_on_submit():
            if len(form.body.data) > 1000:
                return render_template('add_review.html',
                                       title='Smoke - Add Review',
                                       form=form,
                                       logged_in=user,
                                       errors=[
                                           'Your review is too long! Max length - 1000'])
            review = Review(rating=form.rating.data,
                            body=form.body.data,
                            user_id=user.id,
                            software_id=id)
            db.session.add(review)
            db.session.commit()
            return redirect(url_for('product_page', id=id))
        return render_template('add_review.html',
                               title='Smoke - Add Review',
                               form=form,
                               logged_in=user)
    return abort(403)


@app.route('/product/<int:product_id>/news/<int:news_id>/add_comment', methods=['GET', 'POST'])
def add_comment(product_id, news_id):
    form = AddCommentForm()
    user = check_for_logged_in()
    news = check_for_permission(user, news_id, News)
    if isinstance(news, int):
        return abort(news)
    if form.validate_on_submit():
        if len(form.body.data) > 1000:
            return render_template('add_comment.html',
                                   title='Smoke - Add Comment',
                                   form=form,
                                   logged_in=user,
                                   errors=[
                                       'Your comment is too long! Max length - 1000'])
        comment = Comment(body=form.body.data,
                          user_id=user.id,
                          news_id=news.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('news', product_id=product_id, news_id=news_id))
    return render_template('add_comment.html',
                           title='Smoke - Add Comment',
                           form=form,
                           logged_in=user)


@app.route('/delete_comment/<int:id>')
def delete_comment(id):
    user = check_for_logged_in()
    comment = check_for_permission(user, id, Comment)
    if isinstance(comment, int):
        return abort(comment)
    if comment.user_id == user.id:
        news = comment.news
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('news', product_id=news.software_id, news_id=news.id))
    return abort(403)


@app.route('/delete_news/<int:id>')
def delete_news(id):
    user = check_for_logged_in()
    news = check_for_permission(user, id, News)
    if isinstance(news, int):
        return abort(news)
    if news.user_id == user.id:
        for comment in news.comments:
            db.session.delete(comment)
        db.session.delete(news)
        db.session.commit()
        return redirect(url_for('all_news', id=news.software_id))
    return abort(403)


@app.route('/delete_software/<int:id>')
def delete_software(id):
    user = check_for_logged_in()
    software = check_for_permission(user, id, Software)
    if isinstance(software, int):
        return abort(software)
    if software.user_id == user.id:
        for screenshot in software.screenshots:
            db.session.delete(screenshot)
        for review in software.reviews:
            db.session.delete(review)
        for news in software.news:
            for comment in news.comments:
                db.session.delete(comment)
            db.session.delete(news)
        db.session.delete(software)
        db.session.commit()
        return redirect(url_for('catalog'))
    return abort(403)


@app.route('/delete_review/<int:id>')
def delete_review(id):
    review = Review.query.get(id)
    if review:
        user = check_for_logged_in()
        if user:
            if review in user.reviews:
                product_id = review.software_id
                db.session.delete(review)
                db.session.commit()
                return redirect(url_for('product_page', id=product_id))
            return abort(403)
        return abort(403)
    return abort(404)


@app.errorhandler(404)
def page_not_found(error):
    user = check_for_logged_in()
    return render_template('not_found.html', title='Smoke - 404',
                           logged_in=user)


@app.errorhandler(403)
def not_allowed(error):
    user = check_for_logged_in()
    return render_template('not_allowed.html', title='Smoke - 403',
                           logged_in=user)

@app.route('/403')
def not_allowed_check():
    return abort(403)


if __name__ == '__main__':
    app.run('127.0.0.1', port=8080)
