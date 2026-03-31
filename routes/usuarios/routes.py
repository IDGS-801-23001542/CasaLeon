from . import usuarios

from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, render_template, request, redirect, url_for
from flask import flash
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from flask import g
import forms
from flask_migrate import Migrate
from models import db
from models import Usuario

# ======================================================================================================
# Aqui se definen las rutas y las funciones para los modulos
# Para rutas private la ruta debera comenzar con /private
# Si es una ruta de admin, se agrega el prefijo /admin
# Si es ruta de empleado, se queda solo /private 
# Al final se agrega el nombre del modulo o la funcion de la ruta. Ejemplo: /private/admin/crearUsuario
# Si es una ruta publica el prefijo sera solamente /public y luego el nombre de la funciond de la ruta
# Ejemplo para public: /public/miCarrito
# ======================================================================================================
# ================== Para usarlos vayan al archivo app.py y sigan los comentarios ======================


@usuarios.route("/private/admin/usuarios")
def usuarios_page():
    return render_template("private/usuarios.html")