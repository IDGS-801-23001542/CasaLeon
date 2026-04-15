from decimal import Decimal
from flask import Flask, render_template, g
from dotenv import load_dotenv

from config import DevelopmentConfig
from extensions import mail, migrate
from models import db, Usuario, Cliente
from mongo import init_mongo, ensure_report_indexes
from services.mongo_store import count_cart_items
from utils.auth import get_identity

from routes.auth import auth
from routes.tienda import tienda
from routes.usuarios import usuarios
from routes.proveedores import proveedores
from routes.productos import productos
from routes.auditoria import auditoria
from routes.materia_prima import materia_prima
from routes.recetas import recetas
from routes.produccion import produccion
from routes.merma import merma
from routes.ventas import ventas
from routes.reportes import reportes


def create_app():
    app = Flask(__name__)

    load_dotenv(".env.local", override=True)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    init_mongo(app)

    app.register_blueprint(auth)
    app.register_blueprint(tienda)
    app.register_blueprint(usuarios)
    app.register_blueprint(proveedores)
    app.register_blueprint(productos)
    app.register_blueprint(auditoria)
    app.register_blueprint(materia_prima)
    app.register_blueprint(recetas)
    app.register_blueprint(produccion)
    app.register_blueprint(merma)
    app.register_blueprint(ventas)
    app.register_blueprint(reportes)

    @app.template_filter("num")
    def format_num(value, decimals=2, trim=True):
        try:
            n = Decimal(str(value or 0))
            text = f"{n:,.{int(decimals)}f}"
            if trim and "." in text:
                text = text.rstrip("0").rstrip(".")
            return text
        except Exception:
            return value

    @app.template_filter("money")
    def format_money(value):
        try:
            n = Decimal(str(value or 0))
            return f"{n:,.2f}"
        except Exception:
            return value

    @app.before_request
    def load_identity():
        g.user = None
        g.role = None
        g.identity = None
        g.cart_count = 0

        ident = get_identity()
        if not ident:
            return

        g.identity = ident

        if ident["type"] == "USUARIO":
            u = Usuario.query.filter_by(id_usuario=ident["id"], activo=1).first()
            if u:
                g.user = u
                g.role = u.rol.codigo if u.rol else None

        elif ident["type"] == "CLIENTE":
            c = Cliente.query.filter_by(id_cliente=ident["id"], activo=1).first()
            if c:
                g.user = c
                g.role = "CLIENTE"
                try:
                    g.cart_count = count_cart_items(c.id_cliente)
                except Exception as e:
                    print("ERROR COUNT CART ITEMS:", e)
                    g.cart_count = 0

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        ensure_report_indexes()
    app.run(debug=True)