from flask import Blueprint

board = Blueprint(
    'dashboard',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import dashboard