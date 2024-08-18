from flask import Blueprint

bp = Blueprint('kanban', __name__)

from . import routes