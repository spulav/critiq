from flask import Blueprint

board = Blueprint(
    'dashboard',
    __name__
)

from . import dashboard