from flask import Flask
import random
from .dashboard import board
from .logins import login
from .profile import profile
from .read import read

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

# ============== Error Handling ============

def errorhandler(view):
    @wraps(view)
    def wrap(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as err:
            flash('Error occurred: '+str(err))
            return redirect(url_for('login.index'))
    return wrap

# ============== Registrations =============
app.register_blueprint(board, url_prefix='/dashboard')
app.register_blueprint(login)
app.register_blueprint(profile, url_prefix='/profile')
app.register_blueprint(read)