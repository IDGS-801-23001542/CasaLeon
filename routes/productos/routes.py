from . import productos

from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, render_template, request, redirect, url_for
from flask import flash
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from flask import g
import forms
from flask_migrate import Migrate
from models import db
# from models import Proveedores


@productos.route("/private/inventario")
def inventario_page():
    return render_template("private/inventario.html")