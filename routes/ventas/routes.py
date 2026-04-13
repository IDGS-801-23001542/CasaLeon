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
        Venta.query.filter(Venta.folio.like(f"{base}%"))
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
            ventas_query.join(Venta.usuario)
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
            pedidos_query.outerjoin(Pedido.detalles)
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
        registros.append(
            {
                "tipo": "INTERNA",
                "id": venta.id_venta,
                "folio": venta.folio,
                "responsable": venta.usuario.nombre
                if getattr(venta, "usuario", None)
                else "Usuario no disponible",
                "metodo_pago": venta.metodo_pago,
                "estado": "Pagada",
                "total": venta.total or Decimal("0"),
                "creado_en": venta.creado_en,
                "observaciones": venta.observaciones,
                "detalles": venta.detalles,
            }
        )

    for pedido in pedidos_db:
        registros.append(
            {
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
            }
        )

    registros.sort(key=lambda x: x["creado_en"] or datetime.datetime.min, reverse=True)

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
        r for r in registros if r["creado_en"] and r["creado_en"].date() == hoy
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


@ventas.route("/private/ventas/pedido/entregar", methods=["POST"])
@login_required(["ADMIN", "EMPLEADO"])
def marcar_pedido_entregado():
    id_pedido = request.form.get("id_pedido", "").strip()

    if not id_pedido:
        flash("No se recibió el pedido a actualizar.", "warning")
        return redirect(url_for("ventas.listado_ventas"))

    pedido_db = Pedido.query.filter_by(id_pedido=id_pedido).first()

    if not pedido_db:
        flash("Pedido no encontrado.", "danger")
        return redirect(url_for("ventas.listado_ventas"))

    estado_actual = (pedido_db.estado or "").strip().lower()

    if estado_actual == "entregado":
        flash("El pedido ya estaba marcado como entregado.", "info")
        return redirect(url_for("ventas.listado_ventas"))

    pedido_db.estado = "Entregado"
    db.session.add(pedido_db)
    db.session.commit()

    log_event(
        modulo="Ventas",
        accion="Pedido marcado como entregado",
        detalle=f"Pedido '{pedido_db.folio}' marcado como Entregado",
        severidad="INFO",
    )

    flash("Pedido marcado como entregado correctamente.", "success")
    return redirect(url_for("ventas.listado_ventas"))
