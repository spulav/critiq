from app.dbmodels import User
from flask import redirect, flash, url_for

def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None

def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))