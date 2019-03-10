from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, validators


class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.required()])
    email = StringField('Email', [validators.email(), validators.required()])
    password = PasswordField('Password', [validators.required()])
    account_type = SelectField('Account type', choices=[('def', 'Default'),
                                                        ('dev', 'Developer')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.required()])
    password = PasswordField('Password', [validators.required()])
    submit = SubmitField('Login')


class AddNewsForm(FlaskForm):
    title = StringField('Title', [validators.required()])
    body = TextAreaField('Contents', [validators.required()])
    submit = SubmitField('Publish')

class AddCommentForm(FlaskForm):
    body = TextAreaField('Comment', [validators.required()])
    submit = SubmitField('Publish')


class AddSoftwareForm(FlaskForm):
    title = StringField('Title', [validators.required()])
    description = TextAreaField('Description', [validators.required()])
    screenshots = TextAreaField('Screenshots', [validators.required()])
    link = StringField('Download link', [validators.required()])
    submit = SubmitField('Publish')


class AddReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[('Horrible', 'Horrible'),
                                            ('Below average', 'Below average'),
                                            ('Average', 'Average'),
                                            ('Above average', 'Above average'),
                                            ('Great', 'Great')])
    body = TextAreaField('Contents', [validators.required()])
    submit = SubmitField('Publish')
