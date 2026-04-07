from decimal import Decimal, InvalidOperation
import datetime

from flask import render_template, request, redirect, url_for, flash, g
from sqlalchemy import or_

from models import db, Producto, Venta, VentaDetalle, Pedido, PedidoDetalle
from utils.auth import login_required
from utils.audit import log_event
from . import ventas


def parse_decimal(value, default="0"):
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError, AttributeError):
        return Decimal(default)


def generar_folio_venta():
    ahora = datetime.datetime.now()
    base = ahora.strftime("VEN%Y%m%d")
    ultima = (
        Venta.query
        .filter(Venta.folio.like(f"{base}%"))
        .order_by(Venta.id_venta.desc())
        .first()
    )

    consecutivo = 1
    if ultima and ultima.folio:
        try:
            consecutivo = int(ultima.folio.split("-")[-1]) + 1
        except Exception:
            consecutivo = 1

    return f"{base}-{consecutivo:04d}"


def construir_registros_ventas_y_pedidos(q=""):
    q = (q or "").strip()

    ventas_query = Venta.query
    pedidos_query = Pedido.query

    if q:
        like_term = f"%{q}%"

        ventas_query = (
            ventas_query
            .join(Venta.usuario)
            .outerjoin(Venta.detalles)
            .filter(
                or_(
                    Venta.folio.ilike(like_term),
                    Venta.metodo_pago.ilike(like_term),
                    Venta.observaciones.ilike(like_term),
                    VentaDetalle.producto_nombre.ilike(like_term),
                )
            )
            .distinct()
        )

        pedidos_query = (
            pedidos_query
            .outerjoin(Pedido.detalles)
            .filter(
                or_(
                    Pedido.folio.ilike(like_term),
                    Pedido.estado.ilike(like_term),
                    Pedido.nombre_envio.ilike(like_term),
                    Pedido.telefono_envio.ilike(like_term),
                    Pedido.notas.ilike(like_term),
                    PedidoDetalle.producto_nombre.ilike(like_term),
                )
            )
            .distinct()
        )

    ventas_db = ventas_query.order_by(Venta.id_venta.desc()).all()
    pedidos_db = pedidos_query.order_by(Pedido.id_pedido.desc()).all()

    registros = []

    for venta in ventas_db:
        registros.append({
            "tipo": "INTERNA",
            "id": venta.id_venta,
            "folio": venta.folio,
            "responsable": venta.usuario.nombre if getattr(venta, "usuario", None) else "Usuario no disponible",
            "metodo_pago": venta.metodo_pago,
            "estado": "Pagada",
            "total": venta.total or Decimal("0"),
            "creado_en": venta.creado_en,
            "observaciones": venta.observaciones,
            "detalles": venta.detalles,
        })

    for pedido in pedidos_db:
        registros.append({
            "tipo": "TIENDA",
            "id": pedido.id_pedido,
            "folio": pedido.folio,
            "responsable": pedido.nombre_envio or "Cliente",
            "metodo_pago": "COMPRA SIMULADA",
            "estado": pedido.estado or "Pendiente",
            "total": pedido.total or Decimal("0"),
            "creado_en": pedido.creado_en,
            "observaciones": pedido.notas,
            "detalles": pedido.detalles,
        })

    registros.sort(
        key=lambda x: x["creado_en"] or datetime.datetime.min,
        reverse=True
    )

    return registros, ventas_db, pedidos_db


@ventas.route("/private/ventas")
@login_required(["ADMIN", "EMPLEADO"])
def listado_ventas():
    q = request.args.get("q", "").strip()

    registros, ventas_db, pedidos_db = construir_registros_ventas_y_pedidos(q=q)

    total_ventas = len(registros)
    total_ingresos = sum(float(r["total"] or 0) for r in registros)

    hoy = datetime.datetime.now().date()
    registros_hoy = [
        r for r in registros
        if r["creado_en"] and r["creado_en"].date() == hoy
    ]
    total_ventas_hoy = len(registros_hoy)
    ingresos_hoy = sum(float(r["total"] or 0) for r in registros_hoy)

    total_internas = len(ventas_db)
    total_tienda = len(pedidos_db)

    return render_template(
        "private/ventas/ventas.html",
        registros=registros,
        total_ventas=total_ventas,
        total_ingresos=f"{total_ingresos:,.2f}",
        total_ventas_hoy=total_ventas_hoy,
        ingresos_hoy=f"{ingresos_hoy:,.2f}",
        total_internas=total_internas,
        total_tienda=total_tienda,
        q=q,
    )


@ventas.route("/private/ventas/<string:tipo>/<int:registro_id>")
@login_required(["ADMIN", "EMPLEADO"])
def detalle_venta(tipo, registro_id):
    tipo = (tipo or "").upper()

    if tipo == "INTERNA":
        venta_db = Venta.query.filter_by(id_venta=registro_id).first()

        if not venta_db:
            flash("Venta no encontrada.", "danger")
            return redirect(url_for("ventas.listado_ventas"))

        return render_template(
            "private/ventas/venta_detalle.html",
            tipo="INTERNA",
            venta_db=venta_db,
            pedido_db=None,
        )

    if tipo == "TIENDA":
        pedido_db = Pedido.query.filter_by(id_pedido=registro_id).first()

        if not pedido_db:
            flash("Pedido no encontrado.", "danger")
            return redirect(url_for("ventas.listado_ventas"))

        return render_template(
            "private/ventas/venta_detalle.html",
            tipo="TIENDA",
            venta_db=None,
            pedido_db=pedido_db,
        )

    flash("Tipo de registro inválido.", "danger")
    return redirect(url_for("ventas.listado_ventas"))


@ventas.route("/private/ventas/create", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def crear_venta():
    productos_db = (
        Producto.query
        .filter_by(activo=1)
        .order_by(Producto.nombre.asc())
        .all()
    )

    if request.method == "POST":
        ids_producto = request.form.getlist("id_producto[]")
        cantidades = request.form.getlist("cantidad[]")
        metodo_pago = (request.form.get("metodo_pago") or "EFECTIVO").strip().upper()
        observaciones = (request.form.get("observaciones") or "").strip()

        if metodo_pago not in ["EFECTIVO", "TARJETA", "TRANSFERENCIA", "MIXTO"]:
            flash("Método de pago inválido.", "danger")
            return render_template(
                "private/ventas/ventas_create.html",
                productos_db=productos_db,
            )

        if not ids_producto:
            flash("Debes agregar al menos un producto.", "warning")
            return render_template(
                "private/ventas/ventas_create.html",
                productos_db=productos_db,
            )

        lineas = []
        total = Decimal("0")

        for i, id_producto_raw in enumerate(ids_producto):
            id_producto_raw = (id_producto_raw or "").strip()
            cantidad_raw = cantidades[i] if i < len(cantidades) else "0"

            if not id_producto_raw and not (cantidad_raw or "").strip():
                continue

            try:
                id_producto = int(id_producto_raw)
            except Exception:
                flash(f"Fila #{i + 1}: producto inválido.", "danger")
                return render_template(
                    "private/ventas/ventas_create.html",
                    productos_db=productos_db,
                )

            cantidad = parse_decimal(cantidad_raw)
            if cantidad <= 0:
                flash(f"Fila #{i + 1}: la cantidad debe ser mayor a 0.", "danger")
                return render_template(
                    "private/ventas/ventas_create.html",
                    productos_db=productos_db,
                )

            producto_db = Producto.query.filter_by(
                id_producto=id_producto,
                activo=1
            ).first()

            if not producto_db:
                flash(f"Fila #{i + 1}: producto no encontrado o inactivo.", "danger")
                return render_template(
                    "private/ventas/ventas_create.html",
                    productos_db=productos_db,
                )

            stock_actual = Decimal(str(producto_db.stock_actual or 0))
            precio = Decimal(str(producto_db.precio_venta or 0))

            if stock_actual < cantidad:
                flash(
                    f"Stock insuficiente para '{producto_db.nombre}'. "
                    f"Solicitado: {cantidad}, disponible: {stock_actual}.",
                    "danger"
                )
                log_event(
                    modulo="Ventas",
                    accion="Error de validación",
                    detalle=(
                        f"Intento de venta con stock insuficiente para "
                        f"'{producto_db.nombre}'. Solicitado: {cantidad}, disponible: {stock_actual}"
                    ),
                    severidad="WARNING",
                )
                return render_template(
                    "private/ventas/ventas_create.html",
                    productos_db=productos_db,
                )

            subtotal = cantidad * precio
            total += subtotal

            lineas.append({
                "producto": producto_db,
                "cantidad": cantidad,
                "precio": precio,
                "subtotal": subtotal,
            })

        if not lineas:
            flash("Debes capturar al menos una línea válida.", "warning")
            return render_template(
                "private/ventas/ventas_create.html",
                productos_db=productos_db,
            )

        usuario_id = getattr(g.user, "id_usuario", None)
        if not usuario_id:
            flash("No se pudo identificar al usuario actual.", "danger")
            return render_template(
                "private/ventas/ventas_create.html",
                productos_db=productos_db,
            )

        venta_db = Venta(
            folio=generar_folio_venta(),
            id_usuario=usuario_id,
            total=total,
            metodo_pago=metodo_pago,
            observaciones=observaciones or None,
        )
        db.session.add(venta_db)
        db.session.flush()

        for item in lineas:
            producto_db = item["producto"]

            detalle_db = VentaDetalle(
                id_venta=venta_db.id_venta,
                id_producto=producto_db.id_producto,
                producto_nombre=producto_db.nombre,
                precio_unitario=item["precio"],
                cantidad=item["cantidad"],
                subtotal=item["subtotal"],
            )
            db.session.add(detalle_db)

            producto_db.stock_actual = (
                Decimal(str(producto_db.stock_actual or 0)) - item["cantidad"]
            )
            db.session.add(producto_db)

        db.session.commit()

        log_event(
            modulo="Ventas",
            accion="Venta procesada",
            detalle=f"Venta {venta_db.folio} registrada con total ${venta_db.total} y {len(lineas)} producto(s)",
            severidad="INFO",
        )

        flash("Venta registrada correctamente.", "success")
        return redirect(url_for("ventas.listado_ventas"))

    return render_template(
        "private/ventas/ventas_create.html",
        productos_db=productos_db,
    )