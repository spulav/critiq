from flask import (redirect, render_template, 
                    flash, request, url_for)
from flask_login import logout_user, current_user, login_user

from app.repository.user import user_from_email, create_user
from forms.auth import LoginForm, SignUpForm

def login():
    if current_user.is_authenticated:
        return redirect(url_for('board.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = user_from_email(form.email.data)
        if user and user.check_password(password=form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main_bp.dashboard'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth_bp.login'))
    return render_template(form=form)

def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        existing_user=user_from_email(form.email.data)
        if existing_user is None:
            user = create_user(form.username.data, form.email.data, form.password.data)
            login_user(user)
            return "Success"
        flash('A user already exists with that email address.')
    return render_template(form=form)

def logout():
    """User log-out logic."""
    logout_user()
    flash('You have successfully logged out.')
    return redirect(url_for('auth_bp.login'))