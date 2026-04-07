from datetime import datetime
from decimal import Decimal

from mongo import get_mongo_db


def _to_decimal(value):
    try:
        return Decimal(str(value or 0))
    except Exception:
        return Decimal("0")


def _to_float(value):
    return float(_to_decimal(value))


def _cart_collection():
    return get_mongo_db()["carts"]


def _orders_collection():
    return get_mongo_db()["orders"]


def _build_cart_item(producto, cantidad=1):
    cantidad = int(cantidad)
    precio = _to_float(producto.precio_venta)
    subtotal = round(precio * cantidad, 2)

    return {
        "id_producto": int(producto.id_producto),
        "sku": producto.sku,
        "nombre": producto.nombre,
        "precio": precio,
        "cantidad": cantidad,
        "subtotal": subtotal,
        "imagen": producto.imagen,
    }


def _recalc_cart(cart_doc):
    items = cart_doc.get("items", [])
    total = round(sum(float(item.get("subtotal", 0)) for item in items), 2)
    cart_doc["total"] = total
    cart_doc["updatedAt"] = datetime.utcnow()
    return cart_doc


def get_or_create_cart(user_id):
    user_id = int(user_id)
    coll = _cart_collection()

    cart_doc = coll.find_one({"userId": user_id})
    if cart_doc:
        return cart_doc

    new_cart = {
        "userId": user_id,
        "items": [],
        "total": 0.0,
        "updatedAt": datetime.utcnow(),
    }
    coll.insert_one(new_cart)
    return coll.find_one({"userId": user_id})


def get_cart_items(user_id):
    cart_doc = get_or_create_cart(user_id)
    items = cart_doc.get("items", [])
    total = _to_decimal(cart_doc.get("total", 0))
    return items, total


def count_cart_items(user_id):
    cart_doc = get_or_create_cart(user_id)
    return sum(int(item.get("cantidad", 0)) for item in cart_doc.get("items", []))


def add_to_cart(user_id, producto, cantidad=1):
    user_id = int(user_id)
    cantidad = int(cantidad)

    if cantidad <= 0:
        return get_or_create_cart(user_id)

    cart_doc = get_or_create_cart(user_id)
    items = cart_doc.get("items", [])

    found = False
    for item in items:
        if int(item["id_producto"]) == int(producto.id_producto):
            item["cantidad"] = int(item.get("cantidad", 0)) + cantidad
            item["subtotal"] = round(float(item["precio"]) * int(item["cantidad"]), 2)
            item["sku"] = producto.sku
            item["nombre"] = producto.nombre
            item["imagen"] = producto.imagen
            found = True
            break

    if not found:
        items.append(_build_cart_item(producto, cantidad))

    cart_doc["items"] = items
    cart_doc = _recalc_cart(cart_doc)

    _cart_collection().update_one(
        {"userId": user_id},
        {
            "$set": {
                "userId": user_id,
                "items": cart_doc["items"],
                "total": cart_doc["total"],
                "updatedAt": cart_doc["updatedAt"],
            }
        },
        upsert=True,
    )

    saved = get_or_create_cart(user_id)
    print("MONGO CART SAVED:", saved)
    return saved


def update_cart_quantity(user_id, id_producto, cantidad):
    user_id = int(user_id)
    id_producto = int(id_producto)
    cantidad = int(cantidad)

    cart_doc = get_or_create_cart(user_id)
    new_items = []

    for item in cart_doc.get("items", []):
        if int(item["id_producto"]) == id_producto:
            if cantidad > 0:
                item["cantidad"] = cantidad
                item["subtotal"] = round(float(item["precio"]) * cantidad, 2)
                new_items.append(item)
        else:
            new_items.append(item)

    cart_doc["items"] = new_items
    cart_doc = _recalc_cart(cart_doc)

    _cart_collection().update_one(
        {"userId": user_id},
        {
            "$set": {
                "userId": user_id,
                "items": cart_doc["items"],
                "total": cart_doc["total"],
                "updatedAt": cart_doc["updatedAt"],
            }
        },
        upsert=True,
    )

    saved = get_or_create_cart(user_id)
    print("MONGO CART UPDATED:", saved)
    return saved


def remove_from_cart(user_id, id_producto):
    return update_cart_quantity(user_id, id_producto, 0)


def clear_cart(user_id):
    user_id = int(user_id)
    _cart_collection().update_one(
        {"userId": user_id},
        {
            "$set": {
                "userId": user_id,
                "items": [],
                "total": 0.0,
                "updatedAt": datetime.utcnow(),
            }
        },
        upsert=True,
    )
    print("MONGO CART CLEARED FOR USER:", user_id)


def save_order_snapshot(pedido, cliente, items):
    now = datetime.utcnow()

    shipping = {
        "nombre": pedido.nombre_envio,
        "telefono": pedido.telefono_envio,
        "calle": pedido.calle_envio,
        "numero": pedido.numero_envio,
        "colonia": pedido.colonia_envio,
        "ciudad": pedido.ciudad_envio,
        "estado": pedido.estado_envio,
        "pais": pedido.pais_envio,
        "cp": pedido.cp_envio,
        "notas": pedido.notas,
    }

    mongo_items = []
    for item in items:
        mongo_items.append(
            {
                "id_producto": int(item["id_producto"]),
                "sku": item.get("sku"),
                "nombre": item["nombre"],
                "precio": float(item["precio"]),
                "cantidad": int(item["cantidad"]),
                "subtotal": float(item.get("subtotal", 0)),
                "imagen": item.get("imagen"),
            }
        )

    doc = {
        "folio": pedido.folio,
        "sqlPedidoId": int(pedido.id_pedido),
        "userId": int(cliente.id_cliente),
        "userEmail": cliente.email,
        "status": pedido.estado,
        "total": float(pedido.total),
        "items": mongo_items,
        "shipping": shipping,
        "statusHistory": [
            {
                "status": pedido.estado,
                "changedBy": cliente.email,
                "changedAt": now,
                "comment": "Pedido creado desde checkout",
            }
        ],
        "createdAt": now,
        "updatedAt": now,
    }

    print("MONGO ORDER TO SAVE:", doc)

    result = _orders_collection().insert_one(doc)

    saved = _orders_collection().find_one({"_id": result.inserted_id})
    print("MONGO ORDER SAVED:", saved)

    return saved


def get_order_by_folio(folio):
    return _orders_collection().find_one({"folio": folio})