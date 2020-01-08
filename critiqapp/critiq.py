from critiqapp import app

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
import dbi
from werkzeug import secure_filename
import sys,os,random
from threading import Thread, Lock

import critiqapp.lookup as lookup
import critiqapp.wrappers as wrappers
import bleach
import bcrypt

CONN = 'spulavar_db'

lock = Lock()

@app.route('/getTags/', methods=["POST"])
def getTags():
    conn = lookup.getConn(CONN)
    tags = lookup.getTags(conn, 'genre')

    return jsonify( {'tags': tags} )

@app.route('/404/')
def notFound():
    '''Lets user know that something is wrong when they try to
    access a chapter/story that doesn't exist; 
    redirecting them to index would be confusing.'''
    return render_template('404.html', page_title='404')

@app.route('/bookmarks/')
@wrappers.login_required
def bookmarks():
    uid = session['uid']
    conn = lookup.getConn(CONN)
    username = session['username'] if 'username' in session else ''

    books = lookup.getBookmarks(conn, uid)
              
    if not books:
        flash("No bookmarked works were found", 'info')
        
    return render_template('bookmarks.html',
                            res=books,
                            page_title="{}'s Bookmarks".format(username))

@app.route('/recommendations/', methods=["GET", "POST"])
@wrappers.login_required
def recommendations():
    uid = session['uid']
    conn = lookup.getConn(CONN)
    warnings = lookup.getTags(conn, 'warnings')
    username = session['username'] if 'username' in session else ''

    recs = lookup.getRecs(conn, uid, session['filters'])
              
    if not recs:
        flash("No works fitting your preferences were found", 'info')
        
    return render_template('search.html',
                                resKind="Recs", res = recs, warnings=[],
                                page_title="{}'s Home".format(username))

@app.route('/chapIndex/', methods=["POST"])
def chapIndex():
    sid = request.form.get('sid')
    cnum = request.form.get('cid')
    # print(sid, cnum)
    return redirect( url_for('read', sid=sid, cnum=cnum))

@app.route('/history/', methods = ["GET"])
@wrappers.login_required
def history():
    uid = session['uid']
    conn = lookup.getConn(CONN)
    hist = lookup.getHistory(conn, uid)
    username = session['username'] if 'username' in session else ""
    return render_template('history.html',
                            history=hist,
                            page_title="{}'s History".format(username))

@app.route('/markHelpful/', methods=["POST"])
def markHelpful():
    '''allows authors to mark particular comments as helpful or unhelpful'''
    conn = lookup.getConn(CONN)

    helpful = request.form.get('helpful')
    rid = request.form.get('rid') #review id
    
    lookup.changeHelpful(conn, rid, helpful)
    return jsonify(helpful=helpful, rid=rid)

@app.route('/addBookmark/', methods=["POST"])
@wrappers.login_required
def addBookmark():
    book = request.form['changemark']
    uid = session['uid']
    sid = request.form['sid']

    conn = lookup.getConn(CONN)
    isBooked = lookup.isBookmarked(conn, sid, uid)

    if isBooked and book == "Bookmarked":
        lookup.removeBookmark(conn, sid, uid)
        flash("Bookmark removed", 'info')
    elif isBooked is None and book == "Add Bookmark":
        lookup.addBookmark(conn, sid, uid)
        flash("Bookmark added", 'info')
    else:
        flash("Bookmark unchanged", 'info')

    return redirect(request.referrer)

@app.route('/markFinished/<sid>/')
@wrappers.login_required
def markFinished(sid):
    conn = lookup.getConn(CONN)
    lookup.setFinished(conn, sid)
    return(redirect(url_for('manage')))