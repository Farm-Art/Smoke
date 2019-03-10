from flask import *
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'F@iL0V3R_c1u5TeR'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/smoke.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    account_type = db.Column(db.String(20), unique=False, nullable=False)
    softwares = db.relationship('Software', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Software(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(1000), unique=False, nullable=False)
    screenshots = db.relationship('Screenshot', backref='software', lazy=True)
    link = db.Column(db.String(100), unique=True, nullable=False)
    news = db.relationship('News', backref='software', lazy=True)
    reviews = db.relationship('Review', backref='software', lazy=True)

    def __repr__(self):
        return '<Software {}>'.format(self.title)


class Screenshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    software_id = db.Column(db.Integer, db.ForeignKey('software.id'), nullable=False)
    link = db.Column(db.String(100), unique=True, nullable=False)
    caption = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(200), unique=False, nullable=False)

    def __repr__(self):
        return '<Screenshot {} {}>'.format(self.caption, self.software)


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    software_id = db.Column(db.Integer, db.ForeignKey('software.id'), nullable=False)
    title = db.Column(db.String(100), unique=False, nullable=False)
    body = db.Column(db.String(1000), unique=False, nullable=False)
    comments = db.relationship('Comment', backref='news', lazy=True)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(500), unique=False, nullable=False)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    software_id = db.Column(db.Integer, db.ForeignKey('software.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    body = db.Column(db.String(1000), unique=False, nullable=False)


db.create_all()
