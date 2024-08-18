from flask import Blueprint

bp = Blueprint('patio', __name__)

from . import routes
