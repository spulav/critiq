from . import read
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
import dbi
from werkzeug import secure_filename
import sys,os,random
from threading import Lock

import critiqapp.lookup as lookup
import critiqapp.wrappers as wrappers

CONN = 'spulavar_db'

lock = Lock()

@read.route('/read/<int:sid>', defaults={'cnum': 1}, methods=["GET", "POST"])
@read.route('/read/<int:sid>/<int:cnum>/', methods=["GET", "POST"])
@wrappers.login_required
@wrappers.errorhandler
def read(sid, cnum): 
    conn = lookup.getConn(CONN)

    try:
        chapter = lookup.getChapter(conn, sid, cnum)
        cid = chapter['cid']
        try:
            #check if they're logged in
            if 'username' not in session:
                return redirect(url_for('index'))

            uid = session['uid']

            #add to history
            print(lookup.addToHistory(conn, uid, sid, cid))

            #check if they've rated the piece already
            rating = lookup.getRating(conn, sid, uid)
            if rating is not None:
                rating = rating['rating']
                avgRating = float(lookup.calcAvgRating(conn, sid)['avg(rating)'])
            else:
                avgRating = None

            #these are the comments the user has posted on this chapter
            comments = lookup.getComments(conn, uid, cid)

            story = ""

            with open(chapter['filename'], 'r') as infile:
                story = infile.read()
                # print("Read for Reading:" + story)

            isBookmarked = lookup.isBookmarked(conn,sid,uid)

            allch = lookup.getChapters(conn,sid)
            numChap = lookup.getNumChaps(conn, sid)['count(cid)']
            work = lookup.getStory(conn, sid)
            
            #only display all comments on a work if the author is viewing
            #otherwise, users can only see the comments they've written
            if uid == work['uid']:
                allComments = lookup.getAllComments(conn, cid)
            else:
                allComments = None

            if session['username'] == work['username']:
                isUpdate = True
            else:
                isUpdate = False
            return render_template('read.html', 
                                    page_title=work['title'], 
                                    story=story,
                                    chapter=chapter,
                                    author=work['username'],
                                    cnum=cnum,
                                    isBookmark=isBookmarked,
                                    sid=sid,
                                    update=isUpdate,
                                    allch=allch,
                                    comments=comments,
                                    uid=uid,
                                    maxCh=numChap,
                                    allComments=allComments,
                                    old_rating=rating,
                                    avgRating=avgRating)
        except Exception as err:
            # print(err)
            return redirect( url_for('index') )
    except Exception as err:
        return redirect( url_for('notFound') )

@read.route('/addComment/', methods=["POST"])
def addComment():
    conn = lookup.getConn(CONN)
    commentText = request.form["commentText"]
    cid = request.form['chapcid']

    if 'uid' in session:
        uid = session['uid']
        lookup.addComment(conn, commentText, uid, cid)
        flash('Comment submitted!')
        return redirect(request.referrer)
    else:
        return redirect(url_for('index'))

@read.route('/rateAjax/', methods=["POST"])
def rateAjax():
    conn = lookup.getConn(CONN)
    rating = request.form.get('rating')
    sid = request.form.get('sid')
    uid = session['uid']

    lookup.addRating(conn, uid, sid, rating)
    avgRating = float(lookup.calcAvgRating(conn, sid)['avg(rating)'])
    lookup.updateAvgRating(conn, sid, avgRating)
    return jsonify(rating=rating, avgRating=avgRating)

@read.route('/search/<search_kind>/', defaults={'search_term': ""}, methods=["GET", "POST"])
@read.route('/search/<search_kind>/<search_term>', methods=["GET", "POST"])
@wrappers.login_required
@wrappers.errorhandler
def worksByTerm(search_kind, search_term):
    '''searches for works by work, author or tag. if no term then default to all'''
    if 'uid' in session:
        term = search_term

        kind = search_kind
        conn = lookup.getConn(CONN)
        
        filters = []
        completion = None
        audience = None
        sortBy = None
        exclude = session['filters'] if 'filters' in session else []
        
        if (request.method == "POST") and not (kind == "author"):
            filters = request.form.getlist('warnings[]')
            sortBy = request.form.get('sortby')
            completion = request.form.get('finished')
            audience = request.form.get('audience')

        res = (lookup.searchAuthors(conn, term) if kind == "author" 
        else lookup.searchWorks(conn, kind, term, set(filters + exclude))
        )
        # print (str(res))

        if not kind == "author":
            # print("pre everything\n", str(res))
            if completion:

                res = ([work for work in res if not work['wip']] 
                        if completion == 'wip' else
                        [work for work in res if work['wip']])
            # print ("completion\n", str(res))
            if audience:
                res = [work for work in res if work['audience'] == audience]


            if sortBy:
                if sortBy == 'avgRating':
                    for work in res:
                        if work.get('avgRating') == None:
                            work.update({'avgRating': 0})
                
                # print ("checking\n {}".format(str(res)))

                res = sorted(res, reverse = True, key = lambda work: work[sortBy])
                # print ("sorted byyyyy\n {}".format(str(res)))


        resKind = "Authors" if kind == "author" else "Works"
        nm = "Tag" if (kind == "tag") else "Term"

        if not res:
            flash("No {} Found Including {}: {} :( ".format(resKind, nm, term))
        
        return render_template('search.html', resKind=resKind, term=term, 
                                res=res, warnings=lookup.getTags(conn, 'warnings'),
                                page_title="Search")
    else:
        flash('Log in to search.')
        return redirect(url_for('index'))