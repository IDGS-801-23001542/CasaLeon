from . import proveedores

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


@proveedores.route("/private/admin/proveedores")
def proveedores_page():
    return render_template("private/proveedores.html")