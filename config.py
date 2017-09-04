import os

basedir = os.path.abspath(os.path.dirname(__file__))


class GoogleAuth:
    CLIENT_ID = ('494541891672-0l2tvle2fp6vuolvnpbloc2572csr22i.apps.googleusercontent.com')
    CLIENT_SECRET = '4i_tPkEC92iEb9lf66_Nh9qZ'
    REDIRECT_URI = 'http://localhost:5000/callback/google'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']

class Config:
    APP_NAME = "Test Login"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "somethingsecret"
    OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '270182363473695',
        'secret': 'a1ebaa76f2aaa361f05c129f170fa13d'
    },
    'twitter': {
        'id': '0FGOj7Ww9dSXCPHrPjOgoy7YG',
        'secret': 'FTKPEPzeH38U5KL7ny1hjdLlAAOsvxhJ5yGAX4zmZUuQZxWBZI'
    },
    }


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "test.db")


class ProdConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "prod.db")


myconfig = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}