from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, validators


class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.required()])
    email = StringField('Email', [validators.email(), validators.required()])
    password = PasswordField('Password', [validators.required()])
    account_type = SelectField('Account type', choices=[('def', 'Default'),
                                                        ('dev', 'Developer')])
    submit = SubmitField('Register')
