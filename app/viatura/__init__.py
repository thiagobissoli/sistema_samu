from flask import Blueprint

bp = Blueprint('viatura', __name__)

from . import routes
