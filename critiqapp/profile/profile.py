from flask import (Flask, render_template, url_for, request,
                   redirect, flash, session, jsonify)
import dbi
import sys,os,random
from threading import Lock

import critiqapp.lookup as lookup
import critiqapp.wrappers as wrappers
import bleach
import bcrypt

CONN = 'spulavar_db'

lock = Lock()

@profile.route('/<username>')
@wrappers.login_required
@wrappers.errorhandler
def profile(username):
    conn = lookup.getConn(CONN)
    try:
        if request.method == "POST":
            # if either prefs or warnings were updated
            if 'uid' in session:
                uid = session['uid']

                if request.form.get('submit-btn') == "Update Preferences":
                    lookup.updatePrefs(conn, uid, request.form.getlist('pref[]'), False)
                else:
                    lookup.updatePrefs(conn, uid, request.form.getlist('warning[]'), True)
                    
                    session['filters'] = lookup.getPrefs(conn, uid, True)                

                flash('Your preferences have been updated!')      
        
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            currentUsername = session['username']
            uid = lookup.getUID(conn, username)
            
            # retrieve user's current prefs and content filters
            prefs = lookup.getPrefs(conn, uid, False)
            warns = lookup.getPrefs(conn, uid, True)

            # get all genre tags and warnings
            allTags = lookup.getTags(conn, 'genre')

            allWarns = lookup.getTags(conn, 'warnings')

            # default values if profile does not already have any prefs or content filters 
            prefTags = [(tag, False) for tag in allTags]
            warnTags = [(tag, False) for tag in allWarns]

            # set up current prefs and content filters for auto-population
            if prefs: 
                prefTags = ([((tag, True) if tag['tid'] in prefs else (tag, False))
                            for tag in allTags])

            if warns:
                warnTags = ([((tag, True) if tag['tid'] in warns else (tag, False))
                            for tag in allWarns])
            

            stories = lookup.getStories(conn, uid)
            return render_template('profile.html',
                                page_title="{}'s Profile".format(username),
                                username=username, uid=uid, prefs=prefTags, 
                                warnings=warnTags, stories=stories, 
                                currentUsername=currentUsername
                                )
        else:
            flash('You are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('Some kind of error '+str(err))
        return redirect( url_for('index') )

@profile.route('/updateProfile/', methods=["POST"])
@wrappers.login_required
@wrappers.errorhandler
def updateProfile():
    conn = lookup.getConn(CONN)
    uid = session['uid']
    dob = request.form.get('dob')

    lookup.updateProfile(conn, uid, dob)
    username = session['username']
    return redirect( url_for('profile.profile', username=username))