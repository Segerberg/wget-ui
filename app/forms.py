from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo


class AddUserForm(FlaskForm):
    username = StringField('User')
    password1 = PasswordField('Password')
    password2 = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password1')])

class LoginForm(FlaskForm):
    username = StringField('User')
    password = PasswordField('Password')