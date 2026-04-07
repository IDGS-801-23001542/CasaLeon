from flask import Blueprint

merma = Blueprint(
    "merma",
    __name__,
    template_folder="templates",
    static_folder="static",
)

from . import routes
import csv
import datetime
from io import StringIO
from decimal import Decimal
from flask import render_template, request, redirect, url_for, flash, make_response, g
from sqlalchemy import or_

from models import db, Merma, MermaDetalle, Venta, VentaDetalle
from utils.auth import login_required
from utils.audit import log_event
from . import merma


ESTADOS_VALIDOS = ["DISPONIBLE", "REUTILIZADA", "VENDIDA", "DESECHADA"]
TIPOS_VALIDOS = ["RECUPERABLE", "NO_RECUPERABLE"]


def money(value):
    return f"{float(value or 0):,.2f}"


def generar_folio_venta_merma():
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


@merma.route("/private/merma")
@login_required(["ADMIN", "EMPLEADO"])
def listado_merma():
    q = request.args.get("q", "").strip()
    tipo = request.args.get("tipo", "").strip().upper()
    estado = request.args.get("estado", "").strip().upper()

    query = Merma.query

    if tipo and tipo in TIPOS_VALIDOS:
        query = query.filter(Merma.tipo == tipo)

    if estado and estado in ESTADOS_VALIDOS:
        query = query.filter(Merma.estado == estado)

    if q:
        like_term = f"%{q}%"
        query = query.join(Merma.detalles).filter(
            or_(
                Merma.observaciones.ilike(like_term),
                MermaDetalle.materia_prima_nombre.ilike(like_term),
                MermaDetalle.clasificacion.ilike(like_term),
            )
        ).distinct()

    mermas_db = query.order_by(Merma.creado_en.desc(), Merma.id_merma.desc()).all()

    total_mermas = Merma.query.count()
    total_recuperable = Merma.query.filter_by(tipo="RECUPERABLE").count()
    total_no_recuperable = Merma.query.filter_by(tipo="NO_RECUPERABLE").count()
    total_disponible = Merma.query.filter_by(estado="DISPONIBLE").count()

    valor_total = Decimal("0")
    valor_disponible = Decimal("0")
    detalles_count = 0

    for merma_db in mermas_db:
        for detalle in merma_db.detalles:
            detalles_count += 1
            valor_total += Decimal(str(detalle.valor_estimado_total or 0))
            if merma_db.estado == "DISPONIBLE":
                valor_disponible += Decimal(str(detalle.valor_estimado_total or 0))

    return render_template(
        "private/merma/merma.html",
        mermas_db=mermas_db,
        total_mermas=total_mermas,
        total_recuperable=total_recuperable,
        total_no_recuperable=total_no_recuperable,
        total_disponible=total_disponible,
        valor_total=money(valor_total),
        valor_disponible=money(valor_disponible),
        detalles_count=detalles_count,
        q=q,
        tipo=tipo,
        estado=estado,
        tipos_validos=TIPOS_VALIDOS,
        estados_validos=ESTADOS_VALIDOS,
    )


@merma.route("/private/merma/<int:id_merma>")
@login_required(["ADMIN", "EMPLEADO"])
def detalle_merma(id_merma):
    merma_db = Merma.query.filter_by(id_merma=id_merma).first()

    if not merma_db:
        flash("Registro de merma no encontrado.", "danger")
        return redirect(url_for("merma.listado_merma"))

    valor_total = Decimal("0")
    cantidad_total = Decimal("0")

    for detalle in merma_db.detalles:
        valor_total += Decimal(str(detalle.valor_estimado_total or 0))
        cantidad_total += Decimal(str(detalle.cantidad or 0))

    return render_template(
        "private/merma/merma_detalle.html",
        merma_db=merma_db,
        valor_total=money(valor_total),
        cantidad_total=f"{cantidad_total:,.4f}",
        estados_validos=ESTADOS_VALIDOS,
    )


@merma.route("/private/merma/<int:id_merma>/estado", methods=["POST"])
@login_required(["ADMIN", "EMPLEADO"])
def actualizar_estado_merma(id_merma):
    merma_db = Merma.query.filter_by(id_merma=id_merma).first()

    if not merma_db:
        flash("Registro de merma no encontrado.", "danger")
        return redirect(url_for("merma.listado_merma"))

    estado_nuevo = (request.form.get("estado") or "").strip().upper()

    if estado_nuevo not in ESTADOS_VALIDOS:
        flash("Estado inválido.", "danger")
        return redirect(url_for("merma.detalle_merma", id_merma=id_merma))

    estado_anterior = merma_db.estado
    if estado_anterior == estado_nuevo:
        flash("La merma ya tiene ese estado.", "info")
        return redirect(url_for("merma.detalle_merma", id_merma=id_merma))

    merma_db.estado = estado_nuevo
    db.session.add(merma_db)
    db.session.commit()

    log_event(
        modulo="Merma",
        accion="Estado de merma actualizado",
        detalle=f"Merma #{merma_db.id_merma} cambió de {estado_anterior} a {estado_nuevo}",
        severidad="INFO" if estado_nuevo != "DESECHADA" else "WARNING",
    )

    flash("Estado de merma actualizado correctamente.", "success")
    return redirect(url_for("merma.detalle_merma", id_merma=id_merma))


@merma.route("/private/merma/<int:id_merma>/vender", methods=["POST"])
@login_required(["ADMIN", "EMPLEADO"])
def vender_merma(id_merma):
    merma_db = Merma.query.filter_by(id_merma=id_merma).first()

    if not merma_db:
        flash("Registro de merma no encontrado.", "danger")
        return redirect(url_for("merma.listado_merma"))

    if merma_db.estado != "DISPONIBLE":
        flash("Solo se puede vender merma disponible.", "warning")
        return redirect(url_for("merma.detalle_merma", id_merma=id_merma))

    metodo_pago = (request.form.get("metodo_pago") or "EFECTIVO").strip().upper()
    observaciones = (request.form.get("observaciones") or "").strip()
    usuario_id = getattr(g.user, "id_usuario", None)

    if not usuario_id:
        flash("No se pudo identificar al usuario actual.", "danger")
        return redirect(url_for("merma.detalle_merma", id_merma=id_merma))

    if metodo_pago not in ["EFECTIVO", "TARJETA", "TRANSFERENCIA", "MIXTO"]:
        flash("Método de pago inválido.", "danger")
        return redirect(url_for("merma.detalle_merma", id_merma=id_merma))

    total = Decimal("0")
    lineas = []

    for detalle in merma_db.detalles:
        precio_unitario = Decimal(str(detalle.valor_estimado_unit or 0))
        cantidad = Decimal(str(detalle.cantidad or 0))
        subtotal = precio_unitario * cantidad
        total += subtotal

        lineas.append({
            "producto_nombre": f"MERMA - {detalle.materia_prima_nombre}",
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal,
        })

    if not lineas:
        flash("La merma no tiene detalles para vender.", "warning")
        return redirect(url_for("merma.detalle_merma", id_merma=id_merma))

    venta_db = Venta(
        folio=generar_folio_venta_merma(),
        id_usuario=usuario_id,
        total=total,
        metodo_pago=metodo_pago,
        observaciones=observaciones or f"Venta de merma #{merma_db.id_merma}",
    )
    db.session.add(venta_db)
    db.session.flush()

    for item in lineas:
        detalle_venta = VentaDetalle(
            id_venta=venta_db.id_venta,
            id_producto=None,
            producto_nombre=item["producto_nombre"],
            precio_unitario=item["precio_unitario"],
            cantidad=item["cantidad"],
            subtotal=item["subtotal"],
        )
        db.session.add(detalle_venta)

    merma_db.estado = "VENDIDA"
    db.session.add(merma_db)

    db.session.commit()

    log_event(
        modulo="Merma",
        accion="Merma vendida",
        detalle=f"Merma #{merma_db.id_merma} vendida en la venta {venta_db.folio} por total ${venta_db.total}",
        severidad="INFO",
    )

    log_event(
        modulo="Ventas",
        accion="Venta de merma procesada",
        detalle=f"Venta {venta_db.folio} generada a partir de la merma #{merma_db.id_merma}",
        severidad="INFO",
    )

    flash("Merma vendida correctamente.", "success")
    return redirect(url_for("ventas.detalle_venta", id_venta=venta_db.id_venta))


@merma.route("/private/merma/export")
@login_required(["ADMIN"])
def exportar_merma():
    q = request.args.get("q", "").strip()
    tipo = request.args.get("tipo", "").strip().upper()
    estado = request.args.get("estado", "").strip().upper()

    query = Merma.query

    if tipo and tipo in TIPOS_VALIDOS:
        query = query.filter(Merma.tipo == tipo)

    if estado and estado in ESTADOS_VALIDOS:
        query = query.filter(Merma.estado == estado)

    if q:
        like_term = f"%{q}%"
        query = query.join(Merma.detalles).filter(
            or_(
                Merma.observaciones.ilike(like_term),
                MermaDetalle.materia_prima_nombre.ilike(like_term),
                MermaDetalle.clasificacion.ilike(like_term),
            )
        ).distinct()

    mermas_db = query.order_by(Merma.creado_en.desc(), Merma.id_merma.desc()).all()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID_MERMA",
        "ID_ORDEN_PRODUCCION",
        "TIPO",
        "ESTADO",
        "OBSERVACIONES",
        "ID_DETALLE",
        "MATERIA_PRIMA",
        "UNIDAD_MEDIDA",
        "CANTIDAD",
        "CLASIFICACION",
        "VALOR_UNITARIO",
        "VALOR_TOTAL",
        "FECHA",
    ])

    for merma_db in mermas_db:
        if merma_db.detalles:
            for detalle in merma_db.detalles:
                writer.writerow([
                    merma_db.id_merma,
                    merma_db.id_orden_produccion,
                    merma_db.tipo,
                    merma_db.estado,
                    merma_db.observaciones or "",
                    detalle.id_merma_detalle,
                    detalle.materia_prima_nombre,
                    detalle.unidad_medida,
                    detalle.cantidad,
                    detalle.clasificacion,
                    detalle.valor_estimado_unit,
                    detalle.valor_estimado_total,
                    merma_db.creado_en.strftime("%d/%m/%Y %H:%M:%S") if merma_db.creado_en else "",
                ])
        else:
            writer.writerow([
                merma_db.id_merma,
                merma_db.id_orden_produccion,
                merma_db.tipo,
                merma_db.estado,
                merma_db.observaciones or "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                merma_db.creado_en.strftime("%d/%m/%Y %H:%M:%S") if merma_db.creado_en else "",
            ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=merma.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response