from app import db
from app.dbmodels import User

def user_from_email(form_email):
    return User.query.filter_by(email=form_email).first()

def create_user(username, email, password):
    #create user object
    user = User(
        username=username,
        email=email
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

def update_user():
    pass

def get_user():
    pass

def remove_user():
    pass