from . import login
import dbi
from threading import Lock
import critiqapp.lookup as lookup
import critiqapp.wrappers as wrappers
import bcrypt
import hmac_token
from flask_mail import Mail, Message

from flask import (render_template, url_for, request,
                   redirect, flash, session
                   )
from flask import current_app as app

from datetime import datetime, timedelta

CONN = 'spulavar_db'
lock = Lock()
mail = Mail(login)
MYSQL_DT = '%Y-%m-%d %H:%M'

def isValidPassword(passwd1, passwd2):
    if passwd1 != passwd2:
        flash('Passwords do not match', 'warning')
        return False
    if len(passwd1) < 12:
        flash('Passwords must be at least 12 characters long', 'warning')
        return False
    return True

def hash(password):
    hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
    hashed_str = hashed.decode('utf-8')
    return hashed_str

def log(username, uid):
    session['username'] = username
    session['uid'] = uid
    session['logged_in'] = True
    session.permanent = True
    flash('Successfully logged in as '+username, 'success')

def createUser(username, email, hash):
    conn = lookup.getConn(CONN)
    lock.acquire()
    lookup.insertUser(conn, username, email, hash)
    lock.release()
    flash('Password updated', 'info')

def checkPassword(username, password):
    conn = lookup.getConn(CONN)
    user = lookup.getUser(conn, username)

    if user is None: 
        return False
    
    hashed = user['passhash']
    hashed2 = bcrypt.hashpw(password.encode('utf-8'),hashed.encode('utf-8'))
    hashed2_str = hashed2.decode('utf-8')
    return hashed2_str == hashed

def checkEmail(email):
    conn = lookup.getConn(CONN)
    user = lookup.getUserFromEmail(conn, email)
    if user == 0:
        flash('invalid email', 'warning')
        return False
    return True

def getResetTime():
    reset_time = datetime.now()
    reset_time_str = reset_time.strftime(MYSQL_DT)
    return reset_time_str

def sendResetEmail(email, token):
    url = url_for('reset_password',
                      username=email,
                      token=token,
                      _external=True)

    body = ('''Click the link to reset your password: {reset}'''
            .format(reset=url))

    msg = Message(subject='forgot password',
                    sender=app.config["MAIL_USERNAME"],
                    recipients=[email],
                    body=body)
    mail.send(msg)
    flash('check your email for the reset link', 'info')

def checkToken(user_token, token, email, reset_time):
    expire_time = reset_time + timedelta(minutes=5)
    if expire_time < datetime.now():
        flash('link has expired; sorry', 'warning')
        return False
    reset_time_str = reset_time.strftime(MYSQL_DT)
    token2 = hmac_token.make_token(app.secret_key,email+reset_time_str)
    if user_token != token2:
        flash('invalid token')
        return False
    return True

def updatePassword(uid, hashed):
    conn = lookup.getConn(CONN)
    lock.acquire()
    lookup.changePassword(conn, username, hashed_str)
    lock.release()
    return uid

@login.route('/')
def index():
    if wrappers.is_logged_in():
        return url_for('board.dashboard')
    else:
        return render_template('logins/login.html', page_title="Welcome to Critiq")

@login.route('/join/', methods=["POST"])
@wrappers.errorhandler
def join():
    username = request.form['username']
    email = request.form['email']
    passwd1 = request.form['password1']
    passwd2 = request.form['password2']

    if not isValidPassword(passwd1, passwd2):
        return redirect(url_for('login.index'))
        
    hashed = hash(passwd1)
    uid = createUser(username, email, hashed)
    log(username, uid)
    return redirect(url_for('board.dashboard'))

@login.route('/login/', methods=["POST"])
@wrappers.errorhandler
def logger():
    username = request.form['username']
    password = request.form['password']

    conn = lookup.getConn(CONN)
    user = lookup.getUser(conn, username)

    if checkPassword(username, password):
        log(username, user['uid'])
        return redirect(url_for('board.dashboard'))
    else:
        flash('Login incorrect. Try again or join', 'warning')
        return redirect(url_for('login.index'))

@login.route('/logout/')
@wrappers.errorhandler
@wrappers.login_required
def logout():
    session.pop('username')
    session.pop('uid')
    session.pop('logged_in')
    flash('You are logged out', 'info')
    return redirect(url_for('login.index'))

@login.route('/forgot_password/', methods=["POST"])
@wrappers.errorhandler
def forgot():
    email = request.form['email']
    isEmail = checkEmail(email)
    if isEmail:
        reset_time_str = getResetTime()
        msg = email+reset_time_str
        token = hmac_token.make_token(app.secret_key,email+reset_time_str)
        conn = lookup.getConn(CONN)
        lookup.updateToken(conn, reset_time_str, email, token)
        sendResetEmail(email, token)
    return redirect(request.referrer)

@login.route('/reset_password/<email>')
@wrappers.errorhandler
def reset(email):
    user_token = request.args.get('token')
    isEmail = checkEmail(email)
    conn = lookup.getConn(CONN)
    uid, reset_time, token = getUserFromEmail(conn, email)
    isToken = checkToken(user_token, token, email, reset_time)
    if isToken:
        log(username, uid)
        return redirect(url_for('login.change_password'))
    else:
        return redirect(url_for('login.index'))

@login.route('/change_password/', methods=['GET','POST'])
@wrappers.login_required
@wrappers.errorhandler
def changepass():
    if request.method == "POST":
        username = session["username"]
        passwd1 = request.form['password1']
        passwd2 = request.form['password2']

        if not isValidPassword(passwd1, passwd2):
            return redirect(url_for('changepass.index'))
    
        hashed = hash(passwd1)
        updatePassword(uid, hashed)
        return redirect(url_for('board.dashboard'))
    if request.method == 'GET':
            return render_template('change_password.html',
                                    page_title = "Change Password")