from datetime import datetime
from decimal import Decimal

from flask import session
from models import db, Producto, CategoriaProducto, Pedido


def cart():
    return session.setdefault("cart", {})


def save_cart():
    session.modified = True


def cart_items():
    items = list(session.get("cart", {}).values())
    total = sum(Decimal(str(item["precio"])) * item["cantidad"] for item in items)
    return items, total


def producto_to_cart_item(producto):
    return {
        "id_producto": producto.id_producto,
        "nombre": producto.nombre,
        "precio": float(producto.precio_venta),
        "imagen": producto.imagen,
        "stock": int(float(producto.stock_actual)),
        "cantidad": 1,
    }


def next_folio():
    base = datetime.utcnow().strftime("PED%Y%m%d")
    count = Pedido.query.count() + 1
    return f"{base}-{count:04d}"


def query_productos_publicos(busqueda="", categoria_id="", limit=None):
    query = (
        db.session.query(
            Producto.id_producto,
            Producto.nombre,
            Producto.descripcion,
            Producto.precio_venta,
            Producto.stock_actual,
            Producto.imagen,
            CategoriaProducto.nombre.label("categoria"),
            CategoriaProducto.id_categoria_producto.label("categoria_id"),
        )
        .join(
            CategoriaProducto,
            Producto.id_categoria_producto == CategoriaProducto.id_categoria_producto,
        )
        .filter(Producto.activo == 1)
    )

    if busqueda:
        query = query.filter(Producto.nombre.ilike(f"%{busqueda}%"))

    if str(categoria_id).isdigit():
        query = query.filter(Producto.id_categoria_producto == int(categoria_id))

    query = query.order_by(Producto.nombre.asc())

    if limit:
        query = query.limit(limit)

    return query.all()