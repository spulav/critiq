from critiqapp import app

import dbi
from threading import Lock
import critiqapp.lookup as lookup
import critiqapp.wrappers as wrappers
import bcrypt

from flask import (render_template, url_for, request,
                   redirect, flash, session)

CONN = 'spulavar_db'
lock = Lock()

def isValidPassword(passwd1, passwd2):
    if passwd1 != passwd2:
        flash('Passwords do not match')
        return False
    if len(passwd1) < 12:
        flash('Passwords must be at least 12 characters long')
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
    flash('Successfully logged in as '+username)

def createUser(username, hash):
    conn = lookup.getConn(CONN)
    lock.acquire()
    try:
        uid = lookup.insertUser(conn, username, hashed_str)
    except Exception as err: # this is not getting thrown
        flash(repr(err))#: {}'.format(repr(err)))
        return redirect(url_for('login.index'))
    lock.release()
    return uid

def checkPassword(username, password):
    conn = lookup.getConn(CONN)
    user = lookup.getUser(conn, username)

    if user is None: 
        return False
    
    hashed = user['passhash']
    hashed2 = bcrypt.hashpw(password.encode('utf-8'),hashed.encode('utf-8'))
    hashed2_str = hashed2.decode('utf-8')
    return hashed2_str == hashed

@login.route('/')
def index():
    if is_logged_in():
        return url_for('')
    else:
        return render_template('login.html', page_title="Welcome to Critiq")

@login.route('/join/', methods=["POST"])
@wrappers.errorhandler
def join():
    username = request.form['username']
    passwd1 = request.form['password1']
    passwd2 = request.form['password2']

    if not isValidPassword(passwd1, passwd2):
        return redirect(url_for('login.index'))
        
    hashed = hash(passwd1)
    uid = createUser(username, hashed)
    log(username, uid)
    return redirect(url_for('board.dashboard'))

@login.route('/login/', methods=["POST"])
@wrappers.errorhandler
def login():
    username = request.form['username']
    password = request.form['password']

    conn = lookup.getConn(CONN)
    user = lookup.getUser(conn, username)

    if checkPassword(username, password):
        log(username, user['uid'])
        return redirect(url_for('board.dashboard'))
    else:
        flash('Login incorrect. Try again or join')
        return redirect(url_for('login.index'))

@login.route('/logout/')
@wrappers.errorhandler
@wrappers.login_required
def logout():
    session.pop('username')
    session.pop('uid')
    session.pop('logged_in')
    flash('You are logged out')
    return redirect(url_for('login.index'))