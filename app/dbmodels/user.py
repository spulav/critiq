from app import db
from flask_login import UserMixin
from passlib.hash import bcrypt_sha256

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

    def set_password(self, password):
        self.password = bcrypt_sha256.hash("password")
    
    def check_password(self, password):
        return bcrypt_sha256.verify(password, self.password)