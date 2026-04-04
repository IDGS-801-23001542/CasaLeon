from flask import Blueprint

produccion = Blueprint("produccion", __name__)

from . import routes