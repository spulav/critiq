from flask import Blueprint
from flask_login import login_required

board_bp = Blueprint(
    "dashboard", __name__
)

@board_bp.route('/', methods=['GET'])
@login_required
def main():
    return "Hello World"

