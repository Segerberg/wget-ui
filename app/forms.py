from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    email = StringField('E-post')
    password1 = PasswordField('Lösenord')
    password2 = PasswordField('Bekräfta lösenord', validators=[DataRequired(), EqualTo('password1')])
    consent = BooleanField('Samtyck')

