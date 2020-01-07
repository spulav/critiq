from critiqapp import app

from flask import (render_template, url_for, request,
                   redirect, flash, session, jsonify)
import dbi
from threading import Lock

import critiqapp.lookup as lookup
import bcrypt

CONN = 'spulavar_db'

lock = Lock()

@app.route('/dashboard/')
@login_required
def dashboard():
    try:
        uid = session['uid']
        conn = lookup.getConn(CONN)
        stories = lookup.getStories(conn, uid)
        return render_template('dashboard.html', stories=stories, page_title="My Dashboard")
    except Exception as err:
        flash('Error: '+str(err))
        return redirect(url_for('index'))