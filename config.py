import os
from dotenv import load_dotenv
import urllib.parse


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):

    db_string = os.environ.get('db_string')
    params = urllib.parse.quote_plus(db_string)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=%s" % params
    SQLALCHEMY_BINDS = {'hansard': 'sqlite:///' + os.path.join(basedir, 'app.db')}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['michelleyuyingwong@gmail.com']
    MS_TRANSLATOR_KEY = os.getenv('MS_TRANSLATOR_KEY')
    LANGUAGES = ['en', 'es']
    POSTS_PER_PAGE = 10
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    ELASTICUSER = os.environ.get('ELASTICUSER')
    ELASTICPW = os.environ.get('ELASTICPW')
