from flask import Blueprint

bp = Blueprint('migracao', __name__)

from . import routes
