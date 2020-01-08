from functools import wraps
from flask import session, flash

# ============== User Management =============

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('logged_in') == True:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('index'))
    return wrap

def get_id():
    return session['uid']

def is_logged_in():
    return session.get('logged_in') == True

# ============== Error Handling ============

def errorhandler(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as err:
            flash('Error occurred: '+str(err))
            return redirect(url_for('login.index'))
    return wrap
