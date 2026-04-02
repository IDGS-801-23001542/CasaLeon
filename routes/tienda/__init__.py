from flask import Blueprint

tienda = Blueprint("tienda", __name__)

from . import routes