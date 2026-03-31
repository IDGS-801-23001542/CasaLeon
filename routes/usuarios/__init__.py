from flask import Blueprint

#Blueprint: Configuracion de rutas que usaremos para nuestros modulos

usuarios = Blueprint( #Aqui se cambien el nombre a su modulo, tambien en la siguiente linea entre ''
    'usuarios',
    __name__,
    template_folder='templates',
    static_folder='static') 
from . import routes