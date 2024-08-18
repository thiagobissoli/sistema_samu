from flask import Blueprint

bp = Blueprint('calendar', __name__)

from . import routes