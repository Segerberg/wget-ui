
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from app.models import Crawler


class AddUserForm(FlaskForm):
    username = StringField('User')
    password1 = PasswordField('Password')
    password2 = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password1')])

class LoginForm(FlaskForm):
    username = StringField('User')
    password = PasswordField('Password')

class AddCrawlerForm(FlaskForm):
    name = StringField('Name')
    type = SelectField('Type', choices=[('crawler','crawler'),('scraper', 'scraper'),('other', 'other')],validate_choice=False)
    cmd = StringField('Command')
    settings = TextAreaField('Settings')


class AddTargetForm(FlaskForm):
    title = StringField('Title')
    description = TextAreaField('Description')


class AddSeedForm(FlaskForm):
    url = StringField('Url')
    depth = StringField('Depth')
    exclude_patterns = StringField('Exclude regex')
    include_patterns = StringField('Include regex')
    domains = StringField('Allowed Domains')


class AddJobForm(FlaskForm):
    crawler = SelectField('Crawler')

class AddContentOwnerForm(FlaskForm):
    content = StringField('content')
    owner = StringField('Owner name')