from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class Rol(db.Model):
    __tablename__ = "Rol"
    id_rol = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)
    descripcion = db.Column(db.String(120), nullable=False)


class Usuario(db.Model):
    __tablename__ = "Usuario"
    id_usuario = db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey("Rol.id_rol"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Integer, nullable=False, default=1)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    rol = db.relationship("Rol")


class Cliente(db.Model):
    __tablename__ = "Cliente"
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    rfc = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    telefono = db.Column(db.String(30))
    calle = db.Column(db.String(120))
    numero = db.Column(db.String(20))
    colonia = db.Column(db.String(120))
    ciudad = db.Column(db.String(80))
    estado = db.Column(db.String(80))
    pais = db.Column(db.String(80))
    cp = db.Column(db.String(10))
    password_hash = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    activo = db.Column(db.Integer, nullable=False, default=1)

    pedidos = db.relationship("Pedido", backref="cliente", lazy=True)


class AuthToken(db.Model):
    __tablename__ = "AuthToken"
    id_token = db.Column(db.Integer, primary_key=True)
    subject_type = db.Column(db.Enum("USUARIO", "CLIENTE"), nullable=False)
    subject_id = db.Column(db.Integer, nullable=False)
    token_hash = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Integer, nullable=False, default=0)
    user_agent = db.Column(db.String(255))
    ip_addr = db.Column(db.String(45))


class Proveedor(db.Model):
    __tablename__ = "proveedores"

    id_proveedor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    rfc = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(30))
    calle = db.Column(db.String(120))
    numero = db.Column(db.String(20))
    colonia = db.Column(db.String(120))
    ciudad = db.Column(db.String(80))
    estado = db.Column(db.String(80))
    pais = db.Column(db.String(80))
    cp = db.Column(db.String(10))
    activo = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f"<Proveedor {self.id_proveedor} - {self.nombre}>"


class CategoriaProducto(db.Model):
    __tablename__ = "categorias_producto"

    id_categoria_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False, unique=True)

    productos = db.relationship("Producto", backref="categoria", lazy=True)

    def __repr__(self):
        return f"<CategoriaProducto {self.id_categoria_producto} - {self.nombre}>"


class Producto(db.Model):
    __tablename__ = "productos"

    id_producto = db.Column(db.Integer, primary_key=True)
    id_categoria_producto = db.Column(
        db.Integer,
        db.ForeignKey("categorias_producto.id_categoria_producto"),
        nullable=False
    )

    sku = db.Column(db.String(40), unique=True)
    nombre = db.Column(db.String(120), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))
    precio_venta = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    stock_actual = db.Column(db.Numeric(14, 4), nullable=False, default=0)
    costo_unit_prom = db.Column(db.Numeric(12, 4), nullable=False, default=0)
    activo = db.Column(db.Integer, nullable=False, default=1)
    imagen = db.Column(db.String(255))

    def __repr__(self):
        return f"<Producto {self.id_producto} - {self.nombre}>"


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("Cliente.id_cliente"), nullable=False)

    folio = db.Column(db.String(30), unique=True, nullable=False)
    estado = db.Column(db.String(30), nullable=False, default="Pendiente")
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    nombre_envio = db.Column(db.String(150), nullable=False)
    telefono_envio = db.Column(db.String(30))
    calle_envio = db.Column(db.String(120), nullable=False)
    numero_envio = db.Column(db.String(20), nullable=False)
    colonia_envio = db.Column(db.String(120), nullable=False)
    ciudad_envio = db.Column(db.String(80), nullable=False)
    estado_envio = db.Column(db.String(80), nullable=False)
    pais_envio = db.Column(db.String(80), nullable=False, default="México")
    cp_envio = db.Column(db.String(10), nullable=False)

    notas = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    detalles = db.relationship(
        "PedidoDetalle",
        backref="pedido",
        lazy=True,
        cascade="all, delete-orphan"
    )


class PedidoDetalle(db.Model):
    __tablename__ = "pedido_detalles"

    id_pedido_detalle = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("productos.id_producto"), nullable=False)

    producto_nombre = db.Column(db.String(120), nullable=False)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    producto = db.relationship("Producto")