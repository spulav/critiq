from flask import (redirect, render_template, 
                    flash, request, url_for)
from flask_login import logout_user, current_user, login_user

from app.dbmodels import User
from app.forms.auth.forms import login, signup
from app.emails.auth.forgot import forgot_password_email

def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth_bp.home'))
    form = login.LoginForm()
    if form.validate_on_submit():
        user = User.user_from_email(form.email.data)
        if user and user.check_password(password=form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('auth_bp.home'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth_bp.login'))
    return render_template('auth/login.html', form=form)

def signup():
    form = signup.SignUpForm()
    if form.validate_on_submit():
        existing_user = User.user_from_email(form.email.data)
        if existing_user is None:
            user = User.create_user(form.username.data, form.email.data, form.password.data)
            login_user(user)
            return "Success"
        flash('A user already exists with that email address.')
    return render_template('auth/signup.html',form=form)

def logout():
    """User log-out logic."""
    logout_user()
    flash('You have successfully logged out.')
    return redirect(url_for('auth_bp.login'))

def forgot():
    form = forms.forgot.ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.user_from_email(form.email.data)
        if user:
            forgot_password_email(user)
        else:
            flash("There are no users with this email. Sign up or try again.")
            return redirect(url_for('auth_bp.signup'))
