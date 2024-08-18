from flask import Blueprint

bp = Blueprint('gestor', __name__)

from . import routes