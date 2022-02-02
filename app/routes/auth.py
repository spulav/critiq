from flask import Blueprint
from flask_login import login_required
from app.services import auth

auth_bp = Blueprint(
    "auth_bp", __name__
)

@auth_bp.route('/', methods=['GET'])
def home():
    return "Hello World"

@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    return auth.login()

@auth_bp.route('/signup/', methods=['GET','POST'])
def signup():
    return auth.signup()

@auth_bp.route('/logout/')
@login_required
def logout():
    return auth.logout()