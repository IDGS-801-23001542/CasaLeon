from datetime import datetime
from decimal import Decimal

from flask import render_template, request, redirect, url_for, flash, abort, g, session

import forms
from models import db, Producto, CategoriaProducto, Pedido, PedidoDetalle
from utils.auth import login_required
from utils.tienda import (
    cart,
    save_cart,
    cart_items,
    producto_to_cart_item,
    next_folio,
    query_productos_publicos,
)
from . import tienda


@tienda.route("/")
def home():
    productos_destacados = query_productos_publicos(limit=6)
    categorias = CategoriaProducto.query.order_by(CategoriaProducto.nombre.asc()).all()

    return render_template(
        "tienda/home.html",
        productos=productos_destacados,
        categorias=categorias,
    )


@tienda.route("/productos")
def productos_publico():
    busqueda = request.args.get("q", "").strip()
    categoria_id = request.args.get("categoria", "").strip()

    productos = query_productos_publicos(
        busqueda=busqueda,
        categoria_id=categoria_id,
    )
    categorias = CategoriaProducto.query.order_by(CategoriaProducto.nombre.asc()).all()

    return render_template(
        "tienda/productos.html",
        productos=productos,
        categorias=categorias,
        busqueda=busqueda,
        categoria_id=categoria_id,
    )


@tienda.route("/nosotros")
def nosotros():
    return render_template("tienda/nosotros.html")


@tienda.route("/contacto")
def contacto():
    return render_template("tienda/contacto.html")


@tienda.route("/tienda")
def tienda_redirect():
    return redirect(url_for("tienda.productos_publico"))


@tienda.route("/carrito")
def carrito():
    items, total = cart_items()
    return render_template("tienda/carrito.html", items=items, total=total)


@tienda.route("/carrito/agregar/<int:id_producto>", methods=["POST"])
def agregar_carrito(id_producto):
    producto = Producto.query.filter_by(id_producto=id_producto, activo=1).first_or_404()

    max_stock = int(float(producto.stock_actual))
    if max_stock <= 0:
        flash("Este producto no tiene stock disponible.", "warning")
        return redirect(request.referrer or url_for("tienda.productos_publico"))

    carrito_sesion = cart()
    key = str(id_producto)

    if key in carrito_sesion:
        carrito_sesion[key]["cantidad"] += 1
    else:
        carrito_sesion[key] = producto_to_cart_item(producto)

    if carrito_sesion[key]["cantidad"] > max_stock:
        carrito_sesion[key]["cantidad"] = max_stock
        flash("Se ajustó la cantidad al stock disponible.", "warning")
    else:
        flash(f"{producto.nombre} agregado al carrito.", "success")

    save_cart()
    return redirect(request.referrer or url_for("tienda.productos_publico"))


@tienda.route("/carrito/actualizar/<int:id_producto>", methods=["POST"])
def actualizar_carrito(id_producto):
    carrito_sesion = cart()
    key = str(id_producto)

    if key not in carrito_sesion:
        return redirect(url_for("tienda.carrito"))

    try:
        cantidad = int(request.form.get("cantidad", 1))
    except (ValueError, TypeError):
        cantidad = 1

    if cantidad <= 0:
        carrito_sesion.pop(key, None)
        flash("Producto eliminado del carrito.", "info")
    else:
        producto = Producto.query.get_or_404(id_producto)
        max_stock = int(float(producto.stock_actual))
        carrito_sesion[key]["cantidad"] = min(cantidad, max_stock)
        flash("Cantidad actualizada.", "success")

    save_cart()
    return redirect(url_for("tienda.carrito"))


@tienda.route("/carrito/eliminar/<int:id_producto>", methods=["POST"])
def eliminar_carrito(id_producto):
    carrito_sesion = cart()
    carrito_sesion.pop(str(id_producto), None)
    save_cart()
    flash("Producto eliminado del carrito.", "info")
    return redirect(url_for("tienda.carrito"))


@tienda.route("/cliente")
@login_required("CLIENTE")
def cliente_dashboard():
    pedidos = (
        Pedido.query.filter_by(id_cliente=g.user.id_cliente)
        .order_by(Pedido.creado_en.desc())
        .limit(3)
        .all()
    )

    items, total_carrito = cart_items()

    return render_template(
        "tienda/cliente_dashboard.html",
        pedidos=pedidos,
        cart_items=items,
        total_carrito=total_carrito,
    )


@tienda.route("/checkout", methods=["GET", "POST"])
@login_required("CLIENTE")
def checkout():
    items, total = cart_items()

    if not items:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for("tienda.carrito"))

    form = forms.CheckoutForm()

    if request.method == "GET":
        form.nombre.data = g.user.nombre
        form.telefono.data = g.user.telefono
        form.calle.data = g.user.calle
        form.numero.data = g.user.numero
        form.colonia.data = g.user.colonia
        form.ciudad.data = g.user.ciudad
        form.estado.data = g.user.estado
        form.pais.data = g.user.pais or "México"
        form.cp.data = g.user.cp

    if form.validate_on_submit():
        pedido = Pedido(
            id_cliente=g.user.id_cliente,
            folio=next_folio(),
            estado="Pendiente",
            total=total,
            nombre_envio=form.nombre.data.strip(),
            telefono_envio=form.telefono.data.strip() if form.telefono.data else None,
            calle_envio=form.calle.data.strip(),
            numero_envio=form.numero.data.strip(),
            colonia_envio=form.colonia.data.strip(),
            ciudad_envio=form.ciudad.data.strip(),
            estado_envio=form.estado.data.strip(),
            pais_envio=form.pais.data.strip(),
            cp_envio=form.cp.data.strip(),
            notas=form.notas.data.strip() if form.notas.data else None,
            creado_en=datetime.utcnow(),
        )
        db.session.add(pedido)
        db.session.flush()

        for item in items:
            subtotal = Decimal(str(item["precio"])) * item["cantidad"]
            detalle = PedidoDetalle(
                id_pedido=pedido.id_pedido,
                id_producto=item["id_producto"],
                producto_nombre=item["nombre"],
                precio_unitario=Decimal(str(item["precio"])),
                cantidad=item["cantidad"],
                subtotal=subtotal,
            )
            db.session.add(detalle)

        g.user.nombre = form.nombre.data.strip()
        g.user.telefono = form.telefono.data.strip() if form.telefono.data else None
        g.user.calle = form.calle.data.strip()
        g.user.numero = form.numero.data.strip()
        g.user.colonia = form.colonia.data.strip()
        g.user.ciudad = form.ciudad.data.strip()
        g.user.estado = form.estado.data.strip()
        g.user.pais = form.pais.data.strip()
        g.user.cp = form.cp.data.strip()

        db.session.commit()
        session["cart"] = {}
        flash("Compra simulada realizada correctamente. Tu pedido fue registrado.", "success")
        return redirect(url_for("tienda.pedido_detalle", id_pedido=pedido.id_pedido))

    return render_template("tienda/checkout.html", form=form, items=items, total=total)


@tienda.route("/mis-pedidos")
@login_required("CLIENTE")
def mis_pedidos():
    pedidos = (
        Pedido.query.filter_by(id_cliente=g.user.id_cliente)
        .order_by(Pedido.creado_en.desc())
        .all()
    )
    return render_template("tienda/mis_pedidos.html", pedidos=pedidos)


@tienda.route("/pedido/<int:id_pedido>")
@login_required("CLIENTE")
def pedido_detalle(id_pedido):
    pedido = Pedido.query.filter_by(
        id_pedido=id_pedido,
        id_cliente=g.user.id_cliente,
    ).first()

    if not pedido:
        abort(404)

    return render_template("tienda/pedido_detalle.html", pedido=pedido)


@tienda.route("/mi-cuenta", methods=["GET", "POST"])
@login_required("CLIENTE")
def mi_cuenta():
    form = forms.UpdateClienteForm(obj=g.user)

    if form.validate_on_submit():
        g.user.nombre = form.nombre.data.strip()
        g.user.telefono = form.telefono.data.strip() if form.telefono.data else None
        g.user.calle = form.calle.data.strip() if form.calle.data else None
        g.user.numero = form.numero.data.strip() if form.numero.data else None
        g.user.colonia = form.colonia.data.strip() if form.colonia.data else None
        g.user.ciudad = form.ciudad.data.strip() if form.ciudad.data else None
        g.user.estado = form.estado.data.strip() if form.estado.data else None
        g.user.pais = form.pais.data.strip() if form.pais.data else None
        g.user.cp = form.cp.data.strip() if form.cp.data else None

        db.session.commit()
        flash("Tu perfil fue actualizado.", "success")
        return redirect(url_for("tienda.mi_cuenta"))

    return render_template("tienda/mi_cuenta.html", form=form)


@tienda.route("/app/admin/dashboard")
@login_required("ADMIN")
def admin_dashboard():
    return render_template("app/admin_dashboard.html")


@tienda.route("/app/vendedor/dashboard")
@login_required("EMPLEADO")
def vendedor_dashboard():
    return render_template("app/vendedor_dashboard.html")