from flask import Flask
import random

app = Flask(__name__)

app.config['PERMANENT_SESSION_LIFETIME'] = 300000
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['SECRET_KEY'] = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])
app.config['UPLOAD_FOLDER'] = '/uploaded/'

# ============== User Management =============

def login_required(view):
    @wraps(view)
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

import critiqapp.critiq
import logins.py
import dashboard.py
