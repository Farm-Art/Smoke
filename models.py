from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'F@iL0V3R_c1u5TeR'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/smoke.db'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
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
    __tablename__ = 'softwares'
    id = db.Column(db.Integer, primary_key=True)
    developer = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(1000), unique=False, nullable=False)
    link = db.Column(db.String(100), unique=False, nullable=False)
    approved = db.Column(db.Boolean, unique=False, nullable=False)
    news = db.relationship('News', backref='software', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)

    def __repr__(self):
        return '<Software {}>'.format(self.title)


class News(db.Model):
    __tablename__ = 'news_list'
    id = db.Column(db.Integer, primary_key=True)
    software_id = db.Column(db.Integer, db.ForeignKey('softwares.id'), nullable=False)
    title = db.Column(db.String(100), unique=False, nullable=False)
    contents = db.Column(db.String(1000), unique=False, nullable=False)
    comments = db.relationship('Comment', backref='onenews', lazy=True)

    def __repr__(self):
        return '<News {} {}>'.format(self.title, self.software)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    news = db.Column(db.Integer, db.ForeignKey('news_list.id'), nullable=False)
    contents = db.Column(db.String(1000), unique=False, nullable=False)

    def __repr__(self):
        return '<Comment {} {}>'.format(self.author, self.news)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    software = db.Column(db.Integer, db.ForeignKey('softwares.id'), nullable=False)
    rating = db.Column(db.String(100), unique=False, nullable=False)
    contents = db.Column(db.String(1000), unique=False, nullable=False)

    def __repr__(self):
        return '<Review {} {}>'.format(self.author, self.software)


db.create_all()
