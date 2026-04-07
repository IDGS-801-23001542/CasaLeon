from flask import Blueprint

merma = Blueprint(
    "merma",
    __name__,
    template_folder="templates",
    static_folder="static",
)

from . import routes