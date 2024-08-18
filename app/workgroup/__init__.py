from flask import Blueprint

bp = Blueprint('workgroup', __name__)

from . import routes