from app import db
from flask_login import UserMixin
import jwt
from time import time
from passlib.hash import bcrypt_sha256
import os
from dotenv import load_dotenv

load_dotenv()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(),
        nullable=False,
        unique=False
    )

    email = db.Column(
        db.String(),
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.String(),
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
    
    #def get_token(self):
    #   pass
    
    @staticmethod
    def user_from_email(form_email):
        return User.query.filter_by(email=form_email).first()

    @staticmethod
    def create_user(username, email, password):
    #create user object
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()