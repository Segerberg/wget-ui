import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    LANGUAGES = {
        'en': 'English',
        'sv': 'Swedish'
    }
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://:redispw@localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://:redispw@localhost:6379/0'

    #MAIL_SERVER = os.environ.get('MAIL_SERVER')
    #MAIL_PORT = os.environ.get('MAIL_PORT')
    #MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    #MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    #MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')