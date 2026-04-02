from flask import Flask, render_template, g, session
from flask_migrate import Migrate

from config import DevelopmentConfig
from models import db, Usuario, Cliente
from utils.auth import get_identity

from routes.auth import auth
from routes.tienda import tienda
from routes.usuarios import usuarios
from routes.proveedores import proveedores
from routes.productos import productos
from routes.auditoria import auditoria
from routes.operaciones import operaciones

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth)
    app.register_blueprint(tienda)
    app.register_blueprint(usuarios)
    app.register_blueprint(proveedores)
    app.register_blueprint(productos)
    app.register_blueprint(auditoria)
    app.register_blueprint(operaciones)

    @app.before_request
    def load_identity():
        g.user = None
        g.role = None
        g.identity = None
        g.cart_count = (
            sum(item["cantidad"] for item in session.get("cart", {}).values())
            if session.get("cart")
            else 0
        )

        ident = get_identity()
        if not ident:
            return

        g.identity = ident

        if ident["type"] == "USUARIO":
            u = Usuario.query.filter_by(id_usuario=ident["id"], activo=1).first()
            if u:
                g.user = u
                g.role = u.rol.codigo if u.rol else None
        else:
            c = Cliente.query.filter_by(id_cliente=ident["id"], activo=1).first()
            if c:
                g.user = c
                g.role = "CLIENTE"

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
    app.run(debug=True)