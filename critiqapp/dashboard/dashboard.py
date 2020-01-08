from . import board
from flask import (render_template, url_for, request,
                   redirect, flash, session, jsonify)
import dbi
from threading import Lock

import critiqapp.lookup as lookup
import critiqapp.wrappers as wrappers
import bcrypt

CONN = 'spulavar_db'

lock = Lock()

@board.route('/')
@wrappers.login_required
@wrappers.errorhandler
def dashboard():
    uid = session['uid']
    conn = lookup.getConn(CONN)
    stories = lookup.getStories(conn, uid)
    return render_template('manage.html', stories=stories, page_title="My Dashboard")

@board.route('/add/', methods=["GET", "POST"])
@wrappers.login_required
@wrappers.errorhandler
def add():
    if request.method == "GET":
        uid = session['uid']
        conn = lookup.getConn(CONN)
        genre = lookup.getTags(conn, 'genre')
        warnings = lookup.getTags(conn, 'warnings')
        audience = lookup.getTags(conn, 'audience')
        isFin = lookup.getTags(conn, 'isFin')
        return render_template('add.html', warnings=warnings, 
                            genre=genre, audience=audience, isFin=isFin, page_title="Add a Story")
                
    if request.method == "POST":
        uid = session['uid']
        title = request.form['title']
        summary = request.form['summary']
        genre = request.form.getlist('genre')
        audience = request.form['audience']
        warnings = request.form.getlist('warnings')
        status = request.form['isFin']
        if status == '32':
            status = 1 #work is finished
        elif status == '33':
            status = 0 #work is in progress
        
        conn = lookup.getConn(CONN)
        sid = lookup.addStory(conn, uid, title, summary, status)[0]
        lookup.addTags(conn, sid, genre, warnings, audience, status)

        return redirect(url_for('update', sid=sid))

@board.route('/update/<int:sid>/', defaults={'cnum':1}, methods=["GET","POST"])
@board.route('/update/<int:sid>/<int:cnum>/', methods=["GET","POST"])
@wrappers.login_required
@wrappers.errorhandler
def update(sid, cnum):
    conn = lookup.getConn(CONN)
    authorid = lookup.getAuthorId(conn,sid)[0]
    # print(authorid, session['uid'])

    if session['uid']==authorid:
        if request.method=="GET":
            chapter = lookup.getChapter(conn, sid, cnum)
            story = ""
            if chapter:
                with open(chapter['filename'], 'r') as infile:
                    # print("From db: "+chapter['filename'])
                    story = infile.read()
                    # print("Read for Update" + story)
            allch = lookup.getChapters(conn, sid)
            title = lookup.getTitle(conn, sid)
            return render_template('write.html', sid=sid, cnum=cnum, story=story, 
                                allch=allch, title=title['title'], page_title="Update '{}'".format(title['title']))

        if request.method=="POST":
            sometext = request.form['write']
            somehtml = bleach.clean(sometext, #allowed tags, attributes, and styles
                    tags=['b','blockquote','i','em','strong','p','ul','br','li','ol','span', 'pre'], 
                    attributes=['style'],
                    styles=['text-decoration', 'text-align'])

            dirname = os.path.dirname(__file__)
            relative = 'uploaded/'+'sid'+str(sid)+'cnum'+str(cnum)+'.html'
            filename = os.path.join(dirname, relative)
            # print(filename)

            with open(filename, 'w') as outfile:
                outfile.write(somehtml)
                # print("Where it's written:" + filename)
                # print("Write for Update" + somehtml)
                
            lock.acquire()
            chapter = lookup.getChapter(conn,sid,cnum)

            if chapter:
                cid = chapter['cid']
            if not chapter:
                cid = None

            lookup.setChapter(conn, sid, cnum, cid, filename)
            # print("ok i got this")
            lock.release()
            return redirect(url_for('read', sid=sid, cnum=cnum))
    else: 
        flash('''Unauthorized. Please log in with the account associated 
                with this work''', 'info')
        return redirect(url_for('index'))