from flask import Blueprint
from flask_login import login_required
from services import auth

auth_bp = Blueprint(
    "auth", __name__
)

@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    auth.login()

@auth_bp.route('/signup/', methods=['GET','POST'])
def signup():
    auth.signup()

@auth_bp.route('/logout/')
@login_required
def logout():
    auth.logout()