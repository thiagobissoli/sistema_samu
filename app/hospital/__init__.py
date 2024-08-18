from flask import Blueprint

bp = Blueprint('hospital', __name__)

from . import routes