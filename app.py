from flask import Flask, redirect, url_for, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user

from flask_oauth import OAuth
from urllib.request import Request, urlopen, URLError 
import json

from oauth import OAuthSignIn




@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    if provider in ['twitter', 'facebook']:
        oauth = OAuthSignIn.get_provider(provider)
        return oauth.authorize()
    if provider in ['google2']:
        from app_google import google_index
        return google_index() #google_authen () #google_authorize();
   

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


