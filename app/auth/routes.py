from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
import json
import requests
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    '''Route to authenticate users'''
    if current_user.is_authenticated: #used redirect user to home page if user has been authenticated
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next') #redirects user to the page they were originally looking for after authentication
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    '''Route to unauthenticate users'''
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    '''Route to register a new user users'''
    if current_user.is_authenticated: #used redirect user to home page if user has been authenticated
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit(): #if it is a POST request and form clears validation checks
        user = User(username=form.username.data, email=form.email.data, postcode=form.postcode.data)
        user.set_password(form.password.data) #sets user's password
        user.set_representativeandconst() #sets user's representative and postcode
        db.session.add(user) #adds user to the user database
        db.session.commit()
        flash('Congratulations, you are now a registered user!') #flashes message once on the next page.
        return redirect(url_for('auth.login')) #redirects user to log in with credentials they just created
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    '''Route for users to request a reset password token'''
    if current_user.is_authenticated: #used redirect user to home page if user has been authenticated
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() #find user with certain email
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    '''Route for users to reset their password once they navigate to this page, using a user token'''
    if current_user.is_authenticated: #used redirect user to home page if user has been authenticated
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user: #if improper token redirect user to main index
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit(): #if this is a POST request and form completes validation
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
