from flask import Blueprint

read = Blueprint(
    'read',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import read