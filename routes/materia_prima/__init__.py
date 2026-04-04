from flask import Blueprint

materia_prima = Blueprint("materia_prima", __name__)

from . import routes