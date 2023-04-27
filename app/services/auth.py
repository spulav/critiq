from flask import (redirect, render_template, 
                    flash, url_for)
from flask_login import logout_user, current_user, login_user
from app import mail
from flask_mail import Message
import os
from dotenv import load_dotenv
from app.dbmodels import User
from app.forms.auth import *

load_dotenv()

def login():
    if current_user.is_authenticated:
        return redirect(url_for('base_bp.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.user_from_email(form.email.data)
        if user and user.check_password(password=form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('base_bp.home'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth_bp.login'))
    return render_template('auth/form.html', form=form, page_title="Critiq Log In")

def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        existing_user = User.user_from_email(form.email.data)
        if existing_user is None:
            user = User.create_user(form.username.data, form.email.data, form.password.data)
            login_user(user)
            flash("Success","info")
            return redirect(url_for('base_bp.home'))
        flash('A user already exists with that email address.')
    return render_template('auth/signup.html',form=form, page_title="Critiq Sign Up")

def logout():
    logout_user()
    flash('You have successfully logged out.', "info")
    return redirect(url_for('auth_bp.login'))

def forgot():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.user_from_email(form.email.data)
        if user:
            token = user.get_token()
            url = url_for('newpass', token=token, _external=True)
            msg = Message()
            msg.subject = "Critiq Password Reset"
            msg.sender = os.environ.get('MAIL_USERNAME')
            msg.recipients = [user.email]
            msg.html = render_template('auth/reset_email.html',
                                url=url)
            mail.send(msg)
            flash("Password Reset. Please check your email for instructions.")
            return(redirect(url_for('base_bp.home')))
        else:
            flash("There are no users with this email. Sign up or try again.")
            return redirect(url_for('auth_bp.signup'))
    return render_template('auth/form.html',form=form, page_title="Forgot Password")

def newpass(token):
    try: 
        user = User.get_user_from_token(token)
    except:
        flash("URL not valid.")
        return redirect(url_for('base_bp.home'))

    form = NewPassword()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        return redirect(url_for('auth_bp.login'))
    return render_template('auth/form.html', form=form, page_title="New Password")