from datetime import datetime
from decimal import Decimal

from flask import render_template, request, redirect, url_for, flash, abort, g
from werkzeug.security import generate_password_hash, check_password_hash

import forms
from models import db, Producto, CategoriaProducto, Pedido, PedidoDetalle
from services.mongo_store import (
    get_cart_items,
    add_to_cart,
    update_cart_quantity,
    remove_from_cart,
    clear_cart,
    save_order_snapshot,
)
from utils.auth import login_required
from utils.audit import log_event
from utils.tienda import (
    next_folio,
    query_productos_publicos,
)
from . import tienda


@tienda.route("/")
def home():
    productos_destacados = query_productos_publicos(limit=6)
    categorias = CategoriaProducto.query.order_by(CategoriaProducto.nombre.asc()).all()
    return render_template("tienda/home.html", productos=productos_destacados, categorias=categorias)


@tienda.route("/productos")
def productos_publico():
    busqueda = request.args.get("q", "").strip()
    categoria_id = request.args.get("categoria", "").strip()
    productos = query_productos_publicos(busqueda=busqueda, categoria_id=categoria_id)
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
@login_required("CLIENTE")
def carrito():
    items, total = get_cart_items(g.user.id_cliente)
    return render_template("tienda/carrito.html", items=items, total=total)


@tienda.route("/carrito/agregar/<int:id_producto>", methods=["POST"])
@login_required("CLIENTE")
def agregar_carrito(id_producto):
    producto = Producto.query.filter_by(id_producto=id_producto, activo=1).first_or_404()
    max_stock = int(float(producto.stock_actual or 0))

    if max_stock <= 0:
        flash("Este producto no tiene stock disponible.", "warning")
        return redirect(request.referrer or url_for("tienda.productos_publico"))

    items_actuales, _ = get_cart_items(g.user.id_cliente)
    cantidad_actual = 0

    for item in items_actuales:
        if int(item["id_producto"]) == int(id_producto):
            cantidad_actual = int(item["cantidad"])
            break

    if cantidad_actual + 1 > max_stock:
        flash("Se alcanzó el stock disponible para este producto.", "warning")
        return redirect(request.referrer or url_for("tienda.productos_publico"))

    add_to_cart(g.user.id_cliente, producto, 1)
    flash(f"{producto.nombre} agregado al carrito.", "success")
    return redirect(request.referrer or url_for("tienda.productos_publico"))


@tienda.route("/carrito/actualizar/<int:id_producto>", methods=["POST"])
@login_required("CLIENTE")
def actualizar_carrito(id_producto):
    try:
        cantidad = int(request.form.get("cantidad", 1))
    except (ValueError, TypeError):
        cantidad = 1

    producto = Producto.query.filter_by(id_producto=id_producto, activo=1).first()
    if not producto:
        flash("El producto ya no está disponible.", "warning")
        remove_from_cart(g.user.id_cliente, id_producto)
        return redirect(url_for("tienda.carrito"))

    if cantidad <= 0:
        remove_from_cart(g.user.id_cliente, id_producto)
        flash("Producto eliminado del carrito.", "info")
        return redirect(url_for("tienda.carrito"))

    max_stock = int(float(producto.stock_actual or 0))
    cantidad_final = min(cantidad, max_stock)

    update_cart_quantity(g.user.id_cliente, id_producto, cantidad_final)

    if cantidad_final < cantidad:
        flash("Se ajustó la cantidad al stock disponible.", "warning")
    else:
        flash("Cantidad actualizada.", "success")

    return redirect(url_for("tienda.carrito"))


@tienda.route("/carrito/eliminar/<int:id_producto>", methods=["POST"])
@login_required("CLIENTE")
def eliminar_carrito(id_producto):
    remove_from_cart(g.user.id_cliente, id_producto)
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
    items, total_carrito = get_cart_items(g.user.id_cliente)

    return render_template(
        "tienda/cliente_dashboard.html",
        pedidos=pedidos,
        cart_items=items,
        total_carrito=total_carrito,
    )


@tienda.route("/checkout", methods=["GET", "POST"])
@login_required("CLIENTE")
def checkout():
    items, total = get_cart_items(g.user.id_cliente)

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
        for item in items:
            producto_db = Producto.query.filter_by(
                id_producto=item["id_producto"],
                activo=1
            ).first()

            if not producto_db:
                flash(f"El producto '{item['nombre']}' ya no está disponible.", "danger")
                return redirect(url_for("tienda.carrito"))

            cantidad = Decimal(str(item["cantidad"]))
            stock_actual = Decimal(str(producto_db.stock_actual or 0))

            if stock_actual < cantidad:
                flash(
                    f"No hay stock suficiente para '{producto_db.nombre}'. Disponible: {stock_actual}.",
                    "danger"
                )
                return redirect(url_for("tienda.carrito"))

        folio = next_folio()

        try:
            pedido = Pedido(
                id_cliente=g.user.id_cliente,
                folio=folio,
                estado="Pendiente",
                total=Decimal(str(total)),
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
                subtotal = Decimal(str(item["precio"])) * Decimal(str(item["cantidad"]))

                detalle = PedidoDetalle(
                    id_pedido=pedido.id_pedido,
                    id_producto=item["id_producto"],
                    producto_nombre=item["nombre"],
                    precio_unitario=Decimal(str(item["precio"])),
                    cantidad=int(item["cantidad"]),
                    subtotal=subtotal,
                )
                db.session.add(detalle)

                producto_db = Producto.query.filter_by(id_producto=item["id_producto"]).first()
                producto_db.stock_actual = (
                    Decimal(str(producto_db.stock_actual or 0)) -
                    Decimal(str(item["cantidad"]))
                )
                db.session.add(producto_db)

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
            print("SQL PEDIDO COMMIT OK:", pedido.folio, pedido.id_pedido)

        except Exception as e:
            db.session.rollback()
            print("ERROR SQL CHECKOUT:", e)
            flash("Ocurrió un error al registrar el pedido.", "danger")
            return render_template("tienda/checkout.html", form=form, items=items, total=total)

        try:
            saved_order = save_order_snapshot(
                pedido=pedido,
                cliente=g.user,
                items=items,
            )
            print("ORDER EN MONGO OK:", saved_order)

        except Exception as e:
            import traceback
            print("ERROR GUARDANDO ORDER EN MONGO:", repr(e))
            traceback.print_exc()
            flash("El pedido se guardó en SQL, pero falló el respaldo en Mongo.", "warning")
            return redirect(url_for("tienda.pedido_detalle", id_pedido=pedido.id_pedido))
        try:
            clear_cart(g.user.id_cliente)
        except Exception as e:
            print("ERROR LIMPIANDO CART EN MONGO:", e)

        log_event(
            modulo="Pedidos",
            accion="Pedido creado",
            detalle=f"Pedido {pedido.folio} registrado por cliente '{g.user.email}' con total ${pedido.total}",
            severidad="INFO",
        )

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

        current_password = (form.current_password.data or "").strip()
        new_password = (form.new_password.data or "").strip()
        confirm_new_password = (form.confirm_new_password.data or "").strip()

        quiere_cambiar_password = bool(
            current_password or new_password or confirm_new_password
        )

        if quiere_cambiar_password:
            if not g.user.password_hash or not check_password_hash(g.user.password_hash, current_password):
                flash("La contraseña actual es incorrecta.", "danger")
                return render_template("tienda/mi_cuenta.html", form=form)

            g.user.password_hash = generate_password_hash(new_password)

            log_event(
                modulo="Clientes",
                accion="Cambio de contraseña",
                detalle=f"Cliente '{g.user.email}' actualizó su contraseña.",
                severidad="INFO",
                actor_tipo="CLIENTE",
                actor_id=g.user.id_cliente,
                actor_nombre=g.user.nombre,
                actor_email=g.user.email,
            )

        db.session.commit()

        log_event(
            modulo="Clientes",
            accion="Actualización de perfil",
            detalle=f"Cliente '{g.user.email}' actualizó su perfil.",
            severidad="INFO",
            actor_tipo="CLIENTE",
            actor_id=g.user.id_cliente,
            actor_nombre=g.user.nombre,
            actor_email=g.user.email,
        )

        flash("Tu perfil fue actualizado correctamente.", "success")
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