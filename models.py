from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class Rol(db.Model):
    __tablename__ = "Rol"

    id_rol = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)
    descripcion = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<Rol {self.codigo}>"


class Usuario(db.Model):
    __tablename__ = "Usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey("Rol.id_rol"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(10), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Integer, nullable=False, default=1)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    rol = db.relationship("Rol")

    def __repr__(self):
        return f"<Usuario {self.id_usuario} - {self.email}>"


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

    def __repr__(self):
        return f"<Cliente {self.id_cliente} - {self.email}>"


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

    def __repr__(self):
        return f"<AuthToken {self.id_token} - {self.subject_type}:{self.subject_id}>"


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
        nullable=False,
    )

    sku = db.Column(db.String(40), unique=True)
    nombre = db.Column(db.String(120), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))
    precio_venta = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    stock_actual = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    costo_unit_prom = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    activo = db.Column(db.Integer, nullable=False, default=1)
    imagen = db.Column(db.String(255))

    recetas = db.relationship("Receta", backref="producto_ref", lazy=True)
    pedidos_detalle = db.relationship(
        "PedidoDetalle", backref="producto_ref_pedido", lazy=True
    )
    ventas_detalle = db.relationship(
        "VentaDetalle", backref="producto_ref_venta", lazy=True
    )
    ordenes_produccion = db.relationship(
        "OrdenProduccion", backref="producto_ref_orden", lazy=True
    )

    def __repr__(self):
        return f"<Producto {self.id_producto} - {self.nombre}>"


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(
        db.Integer, db.ForeignKey("Cliente.id_cliente"), nullable=False
    )

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
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Pedido {self.id_pedido} - {self.folio}>"


class PedidoDetalle(db.Model):
    __tablename__ = "pedido_detalles"

    id_pedido_detalle = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(
        db.Integer, db.ForeignKey("pedidos.id_pedido"), nullable=False
    )
    id_producto = db.Column(
        db.Integer, db.ForeignKey("productos.id_producto"), nullable=False
    )

    producto_nombre = db.Column(db.String(120), nullable=False)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    producto = db.relationship("Producto")

    def __repr__(self):
        return f"<PedidoDetalle {self.id_pedido_detalle} - {self.producto_nombre}>"


class Venta(db.Model):
    __tablename__ = "ventas"

    id_venta = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(30), unique=True, nullable=False)
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("Usuario.id_usuario"), nullable=False
    )
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    metodo_pago = db.Column(db.String(30), nullable=False, default="EFECTIVO")
    observaciones = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    usuario = db.relationship("Usuario")
    detalles = db.relationship(
        "VentaDetalle",
        backref="venta",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Venta {self.id_venta} - {self.folio}>"


class VentaDetalle(db.Model):
    __tablename__ = "ventas_detalle"

    id_venta_detalle = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey("ventas.id_venta"), nullable=False)
    id_producto = db.Column(
        db.Integer, db.ForeignKey("productos.id_producto"), nullable=False
    )
    producto_nombre = db.Column(db.String(120), nullable=False)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    cantidad = db.Column(db.Numeric(14, 2), nullable=False, default=1)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    producto = db.relationship("Producto")

    def __repr__(self):
        return f"<VentaDetalle {self.id_venta_detalle} - {self.producto_nombre}>"


class CategoriaMateriaPrima(db.Model):
    __tablename__ = "categorias_materia_prima"

    id_categoria_materia_prima = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False, unique=True)
    activo = db.Column(db.Integer, nullable=False, default=1)

    materias_primas = db.relationship("MateriaPrima", backref="categoria_mp", lazy=True)

    def __repr__(self):
        return (
            f"<CategoriaMateriaPrima {self.id_categoria_materia_prima} - {self.nombre}>"
        )


class UnidadMedida(db.Model):
    __tablename__ = "unidades_medida"

    id_unidad_medida = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False, unique=True)
    activo = db.Column(db.Integer, nullable=False, default=1)

    materias_primas = db.relationship(
        "MateriaPrima", backref="unidad_medida_rel", lazy=True
    )

    def __repr__(self):
        return f"<UnidadMedida {self.id_unidad_medida} - {self.nombre}>"


class MateriaPrima(db.Model):
    __tablename__ = "materias_primas"

    id_materia_prima = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False, unique=True)

    id_categoria_materia_prima = db.Column(
        db.Integer,
        db.ForeignKey("categorias_materia_prima.id_categoria_materia_prima"),
        nullable=False,
    )

    id_unidad_medida = db.Column(
        db.Integer,
        db.ForeignKey("unidades_medida.id_unidad_medida"),
        nullable=False,
    )

    id_proveedor = db.Column(
        db.Integer,
        db.ForeignKey("proveedores.id_proveedor"),
        nullable=False,
    )

    stock_actual = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    stock_minimo = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    costo_unit_prom = db.Column(db.Numeric(12, 2), nullable=False, default=None)
    merma_pct = db.Column(db.Numeric(5, 2), nullable=True, default=0)
    activo = db.Column(db.Integer, nullable=False, default=1)

    receta_detalles = db.relationship(
        "RecetaDetalle", backref="materia_prima_ref_receta", lazy=True
    )
    ordenes_detalle = db.relationship(
        "OrdenProduccionDetalle", backref="materia_prima_ref_orden", lazy=True
    )
    mermas_detalle = db.relationship(
        "MermaDetalle", backref="materia_prima_ref_merma", lazy=True
    )

    def __repr__(self):
        return f"<MateriaPrima {self.id_materia_prima} - {self.nombre}>"


class MovimientoMateriaPrima(db.Model):
    __tablename__ = "movimientos_materia_prima"

    id_movimiento_materia_prima = db.Column(db.Integer, primary_key=True)

    id_materia_prima = db.Column(
        db.Integer,
        db.ForeignKey("materias_primas.id_materia_prima"),
        nullable=False,
    )

    id_proveedor = db.Column(
        db.Integer,
        db.ForeignKey("proveedores.id_proveedor"),
        nullable=True,
    )

    tipo = db.Column(db.String(20), nullable=False)  # ENTRADA / SALIDA
    cantidad = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    motivo = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    materia_prima = db.relationship("MateriaPrima")
    proveedor = db.relationship("Proveedor")

    def __repr__(self):
        return (
            f"<MovimientoMateriaPrima {self.id_movimiento_materia_prima} - {self.tipo}>"
        )


class Receta(db.Model):
    __tablename__ = "recetas"

    id_receta = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(
        db.Integer, db.ForeignKey("productos.id_producto"), nullable=True, unique=True
    )
    nombre = db.Column(db.String(150), nullable=False)
    rendimiento = db.Column(db.Numeric(14, 2), nullable=False, default=1)
    costo_estimado = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    activo = db.Column(db.Integer, nullable=False, default=1)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    producto = db.relationship("Producto")
    detalles = db.relationship(
        "RecetaDetalle",
        backref="receta",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Receta {self.id_receta} - {self.nombre}>"


class RecetaDetalle(db.Model):
    __tablename__ = "receta_detalles"

    id_receta_detalle = db.Column(db.Integer, primary_key=True)
    id_receta = db.Column(
        db.Integer, db.ForeignKey("recetas.id_receta"), nullable=False
    )
    id_materia_prima = db.Column(
        db.Integer, db.ForeignKey("materias_primas.id_materia_prima"), nullable=False
    )
    cantidad = db.Column(db.Numeric(14, 2), nullable=False, default=0)

    materia_prima = db.relationship("MateriaPrima")

    def __repr__(self):
        return f"<RecetaDetalle {self.id_receta_detalle}>"


class OrdenProduccion(db.Model):
    __tablename__ = "ordenes_produccion"

    id_orden_produccion = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(
        db.Integer,
        db.ForeignKey("productos.id_producto"),
        nullable=False,
    )

    folio = db.Column(db.String(30), unique=True, nullable=False)
    id_lote = db.Column(db.Integer, db.ForeignKey("lotes.id_lote"), nullable=False)
    lote = db.relationship("Lote")
    cantidad = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    estado = db.Column(db.String(30), nullable=False, default="COMPLETADA")
    costo_estimado = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    observaciones = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    producto = db.relationship("Producto")
    detalles = db.relationship(
        "OrdenProduccionDetalle",
        backref="orden_produccion",
        lazy=True,
        cascade="all, delete-orphan",
    )
    mermas = db.relationship(
        "Merma",
        backref="orden",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<OrdenProduccion {self.id_orden_produccion} - {self.folio}>"


class OrdenProduccionDetalle(db.Model):
    __tablename__ = "ordenes_produccion_detalles"

    id_orden_produccion_detalle = db.Column(db.Integer, primary_key=True)
    id_orden_produccion = db.Column(
        db.Integer,
        db.ForeignKey("ordenes_produccion.id_orden_produccion"),
        nullable=False,
    )
    id_materia_prima = db.Column(
        db.Integer,
        db.ForeignKey("materias_primas.id_materia_prima"),
        nullable=False,
    )

    materia_prima_nombre = db.Column(db.String(120), nullable=False)
    unidad_medida = db.Column(db.String(20), nullable=False)
    cantidad_base = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    cantidad_teorica = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    cantidad_consumida = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    costo_unitario = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    materia_prima = db.relationship("MateriaPrima")

    def __repr__(self):
        return f"<OrdenProduccionDetalle {self.id_orden_produccion_detalle}>"


class Merma(db.Model):
    __tablename__ = "mermas"

    id_merma = db.Column(db.Integer, primary_key=True)
    id_orden_produccion = db.Column(
        db.Integer,
        db.ForeignKey("ordenes_produccion.id_orden_produccion"),
        nullable=False,
    )
    tipo = db.Column(db.String(30), nullable=False, default="RECUPERABLE")
    estado = db.Column(db.String(30), nullable=False, default="DISPONIBLE")
    observaciones = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    detalles = db.relationship(
        "MermaDetalle",
        backref="merma",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Merma {self.id_merma} - {self.tipo}>"


class MermaDetalle(db.Model):
    __tablename__ = "mermas_detalle"

    id_merma_detalle = db.Column(db.Integer, primary_key=True)
    id_merma = db.Column(
        db.Integer,
        db.ForeignKey("mermas.id_merma"),
        nullable=False,
    )
    id_materia_prima = db.Column(
        db.Integer,
        db.ForeignKey("materias_primas.id_materia_prima"),
        nullable=False,
    )

    materia_prima_nombre = db.Column(db.String(120), nullable=False)
    unidad_medida = db.Column(db.String(20), nullable=False)
    cantidad = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    clasificacion = db.Column(db.String(50), nullable=False, default="RECORTE_UTIL")
    valor_estimado_unit = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    valor_estimado_total = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    materia_prima = db.relationship("MateriaPrima")

    def __repr__(self):
        return f"<MermaDetalle {self.id_merma_detalle} - {self.materia_prima_nombre}>"


class AuditoriaLog(db.Model):
    __tablename__ = "auditoria_logs"

    id_log = db.Column(db.Integer, primary_key=True)
    modulo = db.Column(db.String(50), nullable=False)
    accion = db.Column(db.String(120), nullable=False)
    detalle = db.Column(db.String(255), nullable=False)
    severidad = db.Column(db.String(20), nullable=False, default="INFO")

    actor_tipo = db.Column(db.String(20))
    actor_id = db.Column(db.Integer)
    actor_nombre = db.Column(db.String(150))
    actor_email = db.Column(db.String(120))

    ip_addr = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return f"<AuditoriaLog {self.id_log} - {self.modulo} - {self.accion}>"


class Lote(db.Model):
    __tablename__ = "lotes"

    id_lote = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Integer, nullable=False, default=1)
