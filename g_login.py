import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


import json
import datetime

from flask import Flask, url_for, redirect, \
    render_template, session, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_required, login_user, \
    logout_user, current_user, UserMixin,  AnonymousUserMixin
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from oauth import OAuthSignIn

basedir = os.path.abspath(os.path.dirname(__file__))

"""App Configuration"""
from config import myconfig, GoogleAuth


"""APP creation and configuration"""
app = Flask(__name__)
app.config.from_object(myconfig['dev'])
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

""" DB Models """


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    name = db.Column(db.String(100))
    avatar = db.Column(db.String(200))
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    social_id = db.Column(db.String(64))
    nickname = db.Column(db.String(64))

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<User %r>' % self.name

    @classmethod
    def get(cls, id):
        """Return user instance of id, return None if not exist"""
        try:
            return cls(id)
        except UserWarning:
            return None

#flask-login anonymous user class
class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.username = 'Guest'

login_manager.anonymous_user = Anonymous
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
""" OAuth Session creation """


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(GoogleAuth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            GoogleAuth.CLIENT_ID,
            state=state,
            redirect_uri=GoogleAuth.REDIRECT_URI)
    oauth = OAuth2Session(
        GoogleAuth.CLIENT_ID,
        redirect_uri=GoogleAuth.REDIRECT_URI,
        scope=GoogleAuth.SCOPE)
    return oauth


@app.route('/')
@login_required
def index1():
    return render_template('index1.html')


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index1'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        GoogleAuth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)


@app.route('/callback/google')
def callback():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index1', user=current_user))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                GoogleAuth.TOKEN_URI,
                client_secret=GoogleAuth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(GoogleAuth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            print (user_data)
            email = user_data['email']
            try:
                user = User.query.filter_by(email=email).first()
            except Exception as e:
                user = User()
                user.email = email

            if user is None:
                user = User()
                user.email = email
            user.social_id = user_data['id']
            user.name = user_data['name']
            print(token)
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            if user:
                print ( "**callback/google** user name={} social_id={} email={}".format (user.name, user.social_id, user.email) )
            login_user(user)            
            return redirect(url_for('index1', user=user))
        return 'Could not fetch your information.'

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index1'))
    if provider in ['twitter', 'facebook']:
        oauth = OAuthSignIn.get_provider(provider)
        return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    user=None
    if not current_user.is_anonymous:
        return redirect(url_for('index1'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index1', user=user))
    user = User.query.filter_by(social_id=social_id).first()

    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    if user:
        print ( "user name={} social_id={} email={}".format (user.name, user.social_id, user.email) )
    login_user(user, True)
    return redirect(url_for('index1', user=user))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route("/settings")
@login_required
def settings():
    pass
