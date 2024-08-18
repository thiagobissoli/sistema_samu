from flask import Blueprint

bp = Blueprint('censo', __name__)

from . import routes