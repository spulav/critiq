from app import db
from flask_login import UserMixin
from passlib.hash import bcrypt_sha256
import os
from datetime import datetime, timezone, timedelta
import jwt
from dotenv import load_dotenv

load_dotenv()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    username = db.Column(
        db.String(50),
        nullable=False,
        unique=False
    )

    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
        primary_key=True
    )

    password = db.Column(
        db.String(1000),
        primary_key=False,
        unique=False,
        nullable=False
    )
    
    last_login = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )

    def set_password(self, password, commit=False):
        self.password = bcrypt_sha256.hash(password)
        if commit == True:
            db.session.commit()
    
    def check_password(self, password):
        return bcrypt_sha256.verify(password, self.password)
    
    def get_token(self, expires):
        return jwt.encode({'reset_password': self.email, 
                           'exp': datetime.now(tz=timezone.utc) + timedelta(hours=expires)},
                            key=os.environ.get("SECRET_KEY"))
    
    def get_id(self):
        return self.email
    
def get_user_from_token(token):
    try: 
        email = jwt.decode(token, key=os.environ.get("SECRET_KEY"))
    except:
        raise Exception()
    return User.query.get(email)

def user_from_email(form_email):
    return User.query.get(form_email)

def create_user(username, email, password):
    user = User(
        username=username,
        email=email
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return user
    