from flask import Blueprint

bp = Blueprint('local', __name__)

from . import routes
