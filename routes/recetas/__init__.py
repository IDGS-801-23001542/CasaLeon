from flask import Blueprint

recetas = Blueprint("recetas", __name__)

from . import routes