import dbi
from datetime import *

DSN = None

# We need to add transaction locking eventually

def getConn(db):
    '''returns a database connection to the given database'''
    global DSN
    if DSN is None:
        DSN = dbi.read_cnf()
    conn = dbi.connect(DSN)
    conn.select_db(db)
    return conn

# ------------------------ Passwords and UIDs

def insertUser(conn, username, email, hashed_str):
    '''inserts user into database when they make an account'''
    curs = dbi.cursor(conn)
    curs.execute('start transaction')
    curs.execute('lock tables users write')
    curs.execute('''INSERT INTO users(uid,username,email,passhash)
                            VALUES(null,%s,%s,%s)''',
                         [username, email, hashed_str])
    curs.execute('select LAST_INSERT_ID()')
    row = curs.fetchone()
    uid = row[0]
    curs.execute('unlock tables')
    curs.execute('commit')
    return uid

def getUID(conn, username):
    curs = dbi.cursor(conn)
    curs.execute('''select uid from users where username=%s''', [username])
    return curs.fetchone()

def getUser(conn, username):
    '''gets hashed password to check for login'''
    curs = dbi.dictCursor(conn)
    curs.execute('''SELECT uid,username,passhash
                      FROM users
                      WHERE username = %s''',
                     [username])
    return curs.fetchone()

def getUserFromEmail(conn, email):
    '''gets user from email'''
    curs = dbi.dictCursor(conn)
    curs.execute('''SELECT uid, username, reset_time, reset_token
                    FROM users
                    WHERE email=%s''',
                    [email])
    return curs.fetchone()

def checkEmail(conn, email):
    '''checks if email is valid'''
    curs = dbi.dictCursor(conn)
    curs.execute('''SELECT count(*)
                    FROM users
                    WHERE email = %s''',
                    [email])
    return curs.fetchone()[0]

def updateToken(conn, reset_time_str, email, token):
    curs = dbi.dictCursor(conn)
    curs.execute('lock tables users write')
    curs.execute('''UPDATE users
                    SET reset_time = %s, reset_token = %s
                    WHERE email=%s''',
                    [reset_time_str, token, email])
    curs.execute('unlock tables')

def changePassword(conn, uid, hashed):
    curs = dbi.dictCursor(conn)
    curs.execute('lock tables users write')
    curs.execute('''UPDATE userpass
                    SET passhash = %s
                    WHERE uid=%s''',
                    [hashed, uid])
    curs.execute('unlock tables')

# ------------------ Profiles and Preferences

def updateProfile(conn, uid, dob):
    curs = dbi.dictCursor(conn)
    curs.execute('lock tables users write')
    curs.execute('''update users
                    set dob=%s
                    where uid=%s''', [dob, uid])
    curs.execute('unlock tables')

def getStories(conn, uid):
    '''Returns all works associated with an account'''
    curs=dbi.dictCursor(conn)
    curs.execute('''select * from works
                where uid = %s''', [uid])
    return curs.fetchall()

def getPrefs(conn, uid, wantsWarnings):
    '''given uid, retrieves users prefs or warning'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select tid from 
                prefs left outer join tags 
                using(tid) where uid=%s and isWarning=%s''', 
                [uid, wantsWarnings])
    return [tag['tid'] for tag in curs.fetchall()]
    
def updatePrefs(conn, uid, prefs, isWarnings):
    '''updates user preferences'''
    curs = dbi.dictCursor(conn)
    curs.execute('lock tables prefs write')
    curs.execute('''delete from prefs where uid=%s and isWarning=%s''',
                [uid, isWarnings])
    for pref in prefs:
        curs.execute('''insert into prefs values(%s, %s, %s)''',
                    [uid, pref, isWarnings])
    curs.execute('unlock tables')
    # return getPrefs(conn, uid)

# --------------------------- Searching and Recommended Works

def searchWorks(conn, kind, searchterm, filters):
    '''finds works with the title including searchterm or tag = searchterm 
        takes chosen filters into acct'''
    curs = dbi.dictCursor(conn)

    dofilter = ("where sid not in (select sid from taglink where tid in %s)" 
                if filters else "")


    searchParam =  (['%' + searchterm + '%'] if kind == "work" 
                        else [searchterm])     

    params = ([searchParam, filters] if filters else [searchParam])

    if kind == "work":
        curs.execute('''select * from (select sid, uid, title, updated, 
                    summary, stars, wip, avgRating, count(sid) from
                    (select * from works where title like %s) as q1 
                    left outer join chapters using(sid) group by sid) as q2 
                    left outer join (select uid, username from users) as q3 
                    using(uid) left outer join 
                    (select sid, tname as audience from (select * from tags 
                    where ttype='audience') as q4
                    left outer join taglink using(tid)) as q5
                    using(sid) ''' + dofilter, 
                params)
    else:
        curs.execute('''select * from (select sid, uid, title, updated, 
                        summary, stars, wip, avgRating, count(sid) from 
                        (select tid from tags where tname = %s) as q1 
                        left outer join taglink using(tid) 
                        left outer join works using(sid) 
                        left outer join chapters using(sid) group by sid) as q3 
                        left outer join (select uid, username from users) as q4 
                        using(uid) left outer join 
                        (select sid, tname as audience from (select * from tags 
                        where ttype='audience') as q4 
                        left outer join taglink using(tid)) as q5 using(sid) ''' + dofilter, 
                        params)
            
    return curs.fetchall()

def getRecs(conn, uid, filters):
    '''gets recommended stories'''
    curs = dbi.dictCursor(conn)
    currentPrefs = getPrefs(conn, uid, False)
    if currentPrefs:
        isFilters = (" where sid not in (select sid from taglink where tid in %s) " 
                    if filters else "")

        curs.execute('''select * from (select sid, uid, title, updated, summary, 
                        stars, avgRating, count(sid), username, wip from 
                        (select sid from taglink where tid in %s group by sid) as q1 
                        left outer join works using(sid) 
                        left outer join 
                        (select uid, username from users) as q2 
                        using (uid) 
                        left outer join chapters using(sid) group by sid) as q3 ''' 
                        + isFilters + 
                        '''order by avgRating desc''', 
                        ([currentPrefs, filters] if filters else [currentPrefs]))
        res = curs.fetchall()
        return res
    else:
        return {}

def searchAuthors(conn, author):
    '''finds authors matching name'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select uid, username from users where 
                 username like %s''', 
                 ['%' + author + '%'])
    return curs.fetchall()

def getTags(conn, type):
    '''given a tag type, gets tags of that type'''
    curs=dbi.dictCursor(conn)
    curs.execute('select * from tags where ttype=%s',[type])
    return curs.fetchall()

def getAuthor(conn, sid):
    '''given an sid, gets the username'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select username from works inner join users using (uid)
                    where sid=%s''', [sid])
    return curs.fetchone()

def getAuthorId(conn, sid):
    '''given an sid, gets the uid'''
    curs = dbi.cursor(conn)
    curs.execute('''select uid from works inner join users using (uid)
                    where sid=%s''', [sid])
    return curs.fetchone()

def getWarnings(conn, uid):
    '''given uid, retrieves users prefs'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select tid, tname from 
                prefs left outer join tags 
                using(tid) where uid=%s''', 
                [uid])
    return curs.fetchall()

# ----------------------- Reading Stories

def getStory(conn, sid):
    '''Returns a work with given sid'''
    curs=dbi.dictCursor(conn)
    curs.execute('''select * from works inner join users
                    on users.uid=works.uid where sid=%s''', [sid])
    return curs.fetchone()

def getChapter(conn, sid, cnum):
    '''returns a chapter of a story'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select works.title as title,
                    works.wip as wip,
                    works.summary as summary, 
                    works.wip as wip,
                    works.title as title, 
                    chapters.filename as filename,
                    chapters.cid as cid
                    from works inner join chapters using (sid)
                    where sid=%s and cnum=%s
                    ''', [sid, cnum])
    return curs.fetchone()

def getChapters(conn, sid):
    '''given sid, gets all chapters'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select * from chapters 
                where sid=%s
                order by cnum asc''',[sid])
    return curs.fetchall()

def getNumChaps(conn, sid):
    '''returns the number of chapters for a story'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select count(cid) from chapters where sid=%s''', [sid])
    return curs.fetchone()

def getTitle(conn, sid):
    '''retrieves story title'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select title from works where sid=%s''', [sid])
    return curs.fetchone()

# -------------------- Adding and Updating Stories

def setChapter(conn, sid, cnum, cid, filename):
    '''Given sid, cnum, filename, sets the chapter'''
    curs = dbi.cursor(conn)
    curs.execute('lock tables chapters write')

    isTrans = False

    if cid is None:
        isTrans = True
        curs.execute('start transaction')
        curs.execute('select max(cid) from chapters')
        cid = curs.fetchone()[0] + 1
    
    curs.execute('''insert into chapters(sid, cnum, cid, filename)
                values (%s, %s, %s, %s)
                on duplicate key update
                filename=%s''',
                [sid, cnum, cid, filename, filename])
    
    lastUpdated(conn, sid)
    if isTrans == True:
        curs.execute('commit')
    curs.execute('unlock tables')

def lastUpdated(conn, sid):
    '''changes updated to current date whenever a work is updated '''
    curs = dbi.cursor(conn)
    curs.execute('lock tables works write')
    curs.execute('''update works set updated = %s where sid = %s''',
                [datetime.now(), sid])
    curs.execute('unlock tables')

def addStory(conn, uid, title, summary, isFin):
    '''given a uid, title, summary, adds the story'''
    curs = dbi.cursor(conn)
    curs.execute('lock tables works write')
    curs.execute('''insert into works(uid, title, updated, summary, wip, avgRating)
                    values (%s, %s, %s, %s, %s, 0)''', 
                    [uid, title, datetime.now(), summary, isFin])
    curs.execute('select last_insert_id()')
    curs.execute('unlock tables')
    return curs.fetchone()

def setFinished(conn, sid):
    curs = dbi.cursor(conn)
    curs.execute('lock tables works write')
    curs.execute('''update works set wip=1 where sid=%s''', [sid])
    curs.execute('unlock tables')

# def getTagsAjax(conn):
#     '''given a conn, gets all tag names'''
#     curs = dbi.dictCursor(conn)
#     curs.execute('''select tname from tags''')
#     return curs.fetchall()
    
def addTags(conn, sid, genre, warnings, audience, isFin):
    '''adds tags to a story'''
    curs = dbi.cursor(conn)
    curs.execute('lock tables taglink write')
    tagslist = [*genre, *warnings, *audience, *isFin]
    for i in tagslist:
        curs.execute('''insert into taglink(tid, sid)
        values (%s, %s)''', [i, sid])
    curs.execute('unlock tables')

# ------------------------- Comments

def addComment(conn, commentText, uid, cid):
    '''adds a comment to a chapter'''
    curs = dbi.cursor(conn)
    # print(uid)
    # print(cid)
    curs.execute('lock tables reviews write, reviewCredits write')
    curs.execute('''insert into reviews(commenter, reviewText) values(%s, %s)''', [uid, commentText])
    curs.execute('select LAST_INSERT_ID()')
    row = curs.fetchone()
    rid = row[0]
    curs.execute('''insert into reviewCredits values(%s, %s)''', [rid, cid])
    curs.execute('unlock tables')

def getComments(conn, uid, cid):
    '''gets comments for the chapter with a certain commenter'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select reviewText from reviews inner join reviewCredits using(rid)
                    where commenter=%s and cid=%s
                    ''', [uid, cid])
    return curs.fetchall()

def calcAvgRating(conn, sid):
    '''calculates the average rating of a story'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select avg(rating) from ratings
                        inner join works using(sid)
                        where sid=%s''', [sid])
    return curs.fetchone()

def updateAvgRating(conn, sid, avg):
    '''updates the average rating for a story'''
    curs = dbi.dictCursor(conn)
    curs.execute('lock tables works write')
    curs.execute('''update works set avgRating=%s 
                    where sid=%s''', [avg, sid])
    curs.execute('unlock tables')

def addRating(conn, uid, sid, rating):
    '''adds a rating to a story'''
    curs = dbi.dictCursor(conn)
    curs.execute('lock tables ratings write')
    curs.execute('''select * from ratings where sid=%s and uid=%s''', [sid, uid])
    if curs.fetchone() is not None:
        curs.execute('''update ratings set rating=%s 
                    where sid=%s and uid=%s''', [rating, sid, uid])
    else:
        curs.execute('''insert into ratings(uid, sid, rating) 
                        values(%s, %s, %s)''', [uid, sid, rating])
    curs.execute('unlock tables')

def getAllComments(conn, cid):
    '''gets all comments for a chapter'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select reviews.reviewText as reviewText, reviews.rid as rid, 
                        users.username as commenter, reviews.ishelpful as ishelpful
                        from reviews inner join reviewCredits using(rid)
                        inner join users on reviews.commenter=users.uid
                        where cid=%s
                        ''', [cid])
    return curs.fetchall()

def changeHelpful(conn, rid, helpful):
    '''sets a review as helpful or not helpful'''
    curs = dbi.dictCursor(conn)
    curs.execute('lock tables reviews write')
    curs.execute('''update reviews set ishelpful=%s where rid=%s''', [helpful, rid])
    curs.execute('unlock tables')

def getRating(conn, sid, uid):
    '''gets a rating for a story'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select rating from ratings where sid=%s and uid=%s''',[sid, uid])
    return curs.fetchone()

# ----------------------------------- History

def addToHistory(conn, uid, sid, cid):
    '''adds a chapter to history'''
    now = datetime.now()
    #frmat = now.strftime('%Y-%m-%d %H:%M:%S')
    curs = dbi.dictCursor(conn)
    curs.execute('lock tables history write')
    curs.execute('''insert into history values(%s, %s, %s, %s) 
                    on duplicate key update visited = %s''',
                    [uid, sid, cid, now, now])
    curs.execute('unlock tables')

def getHistory(conn, uid):
    '''gets a user's history'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select sid, cid, uid, title, updated, summary, 
                    stars, count(sid), username, visited from  
                    (select sid, visited from history where uid = %s) as q1
                    left outer join works using(sid)
                    left outer join 
                    (select uid, username from users) as q2 
                    using(uid) 
                    left outer join chapters using(sid) group by sid
                    order by visited desc''', 
                    [uid])
    return curs.fetchall()
    
# ----------------------------- Bookmarks

def addBookmark(conn, sid, uid):
    '''adds a bookmark'''
    curs = dbi.dictCursor(conn)
    curs.execute('lock tables bookmarks write')
    curs.execute('''insert into bookmarks(sid, uid)
                    values (%s,%s)''', 
                    [sid, uid])
    curs.execute('unlock tables')

def removeBookmark(conn, sid, uid):
    '''removes a bookmark'''
    curs = dbi.dictCursor(conn)
    curs.execute('lock tables bookmarks write')
    curs.execute('''delete from bookmarks
                    where sid=%s and uid=%s''', 
                    [sid, uid])
    curs.execute('unlock tables')

def isBookmarked(conn, sid, uid):
    '''checks if a work is bookmarked'''
    curs = dbi.cursor(conn)
    curs.execute('''select * from bookmarks 
                where sid=%s and uid=%s''',
                [sid,uid])
    return curs.fetchone()

def getBookmarks(conn, uid):
    '''gets a list of bookmarks'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select sid, username, title, summary from bookmarks
                    inner join works using (sid)
                    inner join users on (works.uid = users.uid)
                    where bookmarks.uid=%s''', [uid])
    return curs.fetchall()