from flask import Blueprint

operaciones = Blueprint("operaciones", __name__)

from . import routes