from flask import Blueprint

auditoria = Blueprint("auditoria", __name__)

from . import routes