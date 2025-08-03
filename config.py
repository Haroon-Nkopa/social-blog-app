import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config():
    #config required by FlaskForm extension 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    #config required by SQLAlchemy for database location
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'app.db')

    #config required mail-server
    MAIL_SERVER =  os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['rethabilejames26@gmail.com']

    POST_PER_PAGE = 3

    #supported languages. 
    LANGUAGES = [ 'en', 'es' ]
    
