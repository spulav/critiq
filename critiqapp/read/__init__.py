from flask import Blueprint

read = Blueprint(
    'read',
    __name__,
    template_folder='templates'
)

from . import read