from flask import Blueprint

bp = Blueprint('googleforms', __name__)

from . import routes