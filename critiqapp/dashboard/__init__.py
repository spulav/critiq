from flask import Blueprint

board = Blueprint(
    'dashboard',
    __name__,
    template_folder='templates'
)

from . import dashboard