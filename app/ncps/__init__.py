from flask import Blueprint

bp = Blueprint('ncps', __name__)

from . import routes
