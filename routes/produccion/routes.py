from flask import Blueprint

produccion = Blueprint("produccion", __name__)

from . import routes
from decimal import Decimal, InvalidOperation
import datetime
from flask import render_template, request, redirect, url_for, flash
import forms
from models import (
    db,
    MateriaPrima,
    Receta,
    Producto,
    OrdenProduccion,
    OrdenProduccionDetalle,
    Merma,
    MermaDetalle,
    Lote,
)
from utils.auth import login_required
from utils.audit import log_event
from . import produccion


def parse_decimal(value, default="0"):
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError, AttributeError):
        return Decimal(default)

def truncar_detalle_auditoria(texto, limite=255):
    texto = (texto or "").strip()
    if len(texto) <= limite:
        return texto
    return texto[:limite - 3].rstrip() + "..."

def cargar_productos_produccion(form):
    productos = Producto.query.filter_by(activo=1).order_by(Producto.nombre.asc()).all()
    form.id_producto.choices = [(p.id_producto, p.nombre) for p in productos]

def cargar_lotes_produccion(form):
    lotes = Lote.query.filter_by(activo=1).order_by(Lote.cantidad.asc()).all()
    form.id_lote.choices = [(l.id_lote, l.nombre) for l in lotes]


def generar_folio_produccion():
    ahora = datetime.datetime.now()
    base = ahora.strftime("OP%Y%m%d")
    ultimo = (
        OrdenProduccion.query
        .filter(OrdenProduccion.folio.like(f"{base}%"))
        .order_by(OrdenProduccion.id_orden_produccion.desc())
        .first()
    )

    consecutivo = 1
    if ultimo and ultimo.folio:
        try:
            consecutivo = int(ultimo.folio.split("-")[-1]) + 1
        except Exception:
            consecutivo = 1

    return f"{base}-{consecutivo:04d}"


def obtener_resumen_receta_para_produccion(receta_db, cantidad_producir):
    resumen = []
    cantidad_producir = Decimal(str(cantidad_producir))
    rendimiento = Decimal(str(receta_db.rendimiento or 1))

    if rendimiento <= 0:
        rendimiento = Decimal("1")

    factor = cantidad_producir / rendimiento

    for detalle in receta_db.detalles:
        if not detalle.materia_prima:
            continue

        mp = detalle.materia_prima
        cantidad_base = Decimal(str(detalle.cantidad or 0))
        merma_pct = Decimal(str(mp.merma_pct or 0))

        cantidad_teorica = cantidad_base * factor
        cantidad_merma = cantidad_teorica * (merma_pct / Decimal("100"))
        cantidad_requerida = cantidad_teorica + cantidad_merma

        costo_unitario = Decimal(str(mp.costo_unit_prom or 0))
        subtotal = cantidad_requerida * costo_unitario
        stock_actual = Decimal(str(mp.stock_actual or 0))

        resumen.append({
            "id_materia_prima": mp.id_materia_prima,
            "nombre": mp.nombre,
            "unidad_medida": mp.unidad_medida_rel.nombre if mp.unidad_medida_rel else "",
            "cantidad_base": cantidad_base,
            "cantidad_teorica": cantidad_teorica,
            "cantidad_merma": cantidad_merma,
            "cantidad_requerida": cantidad_requerida,
            "stock_actual": stock_actual,
            "costo_unitario": costo_unitario,
            "subtotal": subtotal,
            "merma_pct": merma_pct,
            "suficiente": stock_actual >= cantidad_requerida,
        })

    return resumen


@produccion.route("/private/produccion")
@login_required(["ADMIN", "EMPLEADO"])
def produccion_view():
    create_form = forms.ProduccionForm()
    cargar_productos_produccion(create_form)
    cargar_lotes_produccion(create_form)

    producciones_db = OrdenProduccion.query.order_by(OrdenProduccion.id_orden_produccion.desc()).all()
    total_producciones = len(producciones_db)
    producciones_completadas = sum(1 for orden in producciones_db if orden.estado == "COMPLETADA")
    producciones_canceladas = sum(1 for orden in producciones_db if orden.estado == "CANCELADA")
    costo_total = sum(float(orden.costo_estimado or 0) for orden in producciones_db)

    return render_template(
        "private/produccion/produccion.html",
        form=create_form,
        producciones_db=producciones_db,
        total_producciones=total_producciones,
        producciones_completadas=producciones_completadas,
        producciones_canceladas=producciones_canceladas,
        costo_total=f"{costo_total:,.2f}",
    )


@produccion.route("/private/produccion/create", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def crear_produccion():
    create_form = forms.ProduccionForm()
    cargar_productos_produccion(create_form)
    cargar_lotes_produccion(create_form)

    resumen_materiales = []
    producto_db = None
    receta_db = None
    costo_total = Decimal("0")

    if request.method == "POST" and create_form.validate():
        producto_db = Producto.query.filter_by(
            id_producto=create_form.id_producto.data,
            activo=1
        ).first()

        if not producto_db:
            flash("Producto no encontrado o inactivo.", "danger")
            return render_template(
                "private/produccion/produccion_create.html",
                form=create_form,
                resumen_materiales=resumen_materiales,
                producto_db=producto_db,
                receta_db=receta_db,
                costo_total=costo_total,
            )

        receta_db = Receta.query.filter_by(
            id_producto=producto_db.id_producto,
            activo=1
        ).first()

        if not receta_db:
            flash("El producto seleccionado no tiene una receta activa.", "warning")
            return render_template(
                "private/produccion/produccion_create.html",
                form=create_form,
                resumen_materiales=resumen_materiales,
                producto_db=producto_db,
                receta_db=receta_db,
                costo_total=costo_total,
            )

        lote = Lote.query.get(create_form.id_lote.data)
        if not lote:
            flash("Lote inválido.", "danger")
            return render_template(
                "private/produccion/produccion_create.html",
                form=create_form,
                resumen_materiales=resumen_materiales,
                producto_db=producto_db,
                receta_db=receta_db,
                costo_total=costo_total,
            )

        cantidad_producir = Decimal(str(lote.cantidad))
        resumen_materiales = obtener_resumen_receta_para_produccion(receta_db, cantidad_producir)

        if not resumen_materiales:
            flash("La receta no tiene insumos registrados.", "warning")
            return render_template(
                "private/produccion/produccion_create.html",
                form=create_form,
                resumen_materiales=resumen_materiales,
                producto_db=producto_db,
                receta_db=receta_db,
                costo_total=costo_total,
            )

        costo_total = sum((item["subtotal"] for item in resumen_materiales), Decimal("0"))

        insuficientes = [item for item in resumen_materiales if not item["suficiente"]]
        if insuficientes:
            detalle_error = ", ".join(
                f"{item['nombre']} (requiere {item['cantidad_requerida']}, hay {item['stock_actual']})"
                for item in insuficientes
            )

            detalle_log = truncar_detalle_auditoria(
                f"No fue posible registrar producción de '{producto_db.nombre}'. "
                f"Insumos insuficientes: {detalle_error}"
            )

            log_event(
                modulo="Producción",
                accion="Producción rechazada por stock insuficiente",
                detalle=detalle_log,
                severidad="ERROR",
            )
            flash("No hay suficiente materia prima para registrar la orden.", "danger")
            return render_template(
                "private/produccion/produccion_create.html",
                form=create_form,
                resumen_materiales=resumen_materiales,
                producto_db=producto_db,
                receta_db=receta_db,
                costo_total=costo_total,
            )

        estado_nuevo = "PENDIENTE"

        orden_db = OrdenProduccion(
            id_producto=producto_db.id_producto,
            id_lote=lote.id_lote,
            folio=generar_folio_produccion(),
            cantidad=cantidad_producir,
            estado=estado_nuevo,
            costo_estimado=costo_total,
            observaciones=create_form.observaciones.data.strip() if create_form.observaciones.data else None,
        )
        db.session.add(orden_db)
        db.session.flush()

        for item in resumen_materiales:
            detalle_orden = OrdenProduccionDetalle(
                id_orden_produccion=orden_db.id_orden_produccion,
                id_materia_prima=item["id_materia_prima"],
                materia_prima_nombre=item["nombre"],
                unidad_medida=item["unidad_medida"],
                cantidad_base=item["cantidad_base"],
                cantidad_teorica=item["cantidad_teorica"],
                cantidad_consumida=item["cantidad_requerida"],
                costo_unitario=item["costo_unitario"],
                subtotal=item["subtotal"],
            )
            db.session.add(detalle_orden)

        db.session.commit()

        log_event(
            modulo="Producción",
            accion="Orden de producción creada",
            detalle=f"Orden {orden_db.folio} registrada para '{producto_db.nombre}' con cantidad {cantidad_producir} en estado PENDIENTE",
            severidad="INFO",
        )
        flash("Orden de producción registrada correctamente.", "success")
        return redirect(url_for("produccion.produccion_view"))

    return render_template(
        "private/produccion/produccion_create.html",
        form=create_form,
        resumen_materiales=resumen_materiales,
        producto_db=producto_db,
        receta_db=receta_db,
        costo_total=costo_total,
    )


@produccion.route("/private/produccion/update", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def actualizar_produccion():
    id_orden = request.args.get("id")

    orden_db = OrdenProduccion.query.filter(
        OrdenProduccion.id_orden_produccion == id_orden
    ).first()

    if not orden_db:
        flash("Orden de producción no encontrada.", "danger")
        return redirect(url_for("produccion.produccion_view"))

    if orden_db.estado in ["COMPLETADA", "CANCELADA"]:
        flash("No se puede modificar una orden completada o cancelada.", "danger")
        return redirect(url_for("produccion.produccion_view"))

    create_form = forms.ProduccionForm()

    create_form.id_lote.choices = [
        (orden_db.id_lote, orden_db.lote.nombre if orden_db.lote else "Lote actual")
    ]
    create_form.id_lote.data = orden_db.id_lote
    create_form.id_lote.validators = []
    
    create_form.id_producto.choices = [
        (
            orden_db.id_producto,
            orden_db.producto.nombre if orden_db.producto else "Producto actual"
        )
    ]
    create_form.id_producto.data = orden_db.id_producto
    create_form.id_producto.validators = []

    create_form.estado.choices = [
        ("PENDIENTE", "Pendiente"),
        ("EN_PROCESO", "En proceso"),
    ]

    if request.method == "GET":
        create_form.estado.data = orden_db.estado
        create_form.observaciones.data = orden_db.observaciones

        return render_template(
            "private/produccion/produccion_update.html",
            form=create_form,
            orden_db=orden_db,
        )

    if create_form.validate():
        estado_anterior = orden_db.estado
        estado_nuevo = create_form.estado.data

        if estado_nuevo not in ["PENDIENTE", "EN_PROCESO"]:
            flash(
                "Solo puedes cambiar la orden a Pendiente o En proceso desde esta vista.",
                "danger",
            )
            return render_template(
                "private/produccion/produccion_update.html",
                form=create_form,
                orden_db=orden_db,
            )

        orden_db.estado = estado_nuevo
        orden_db.observaciones = (
            create_form.observaciones.data.strip()
            if create_form.observaciones.data else None
        )

        db.session.add(orden_db)
        db.session.commit()

        log_event(
            modulo="Producción",
            accion="Orden de producción actualizada",
            detalle=f"Orden {orden_db.folio} cambió de {estado_anterior} a {estado_nuevo}",
            severidad="INFO",
        )

        flash("Orden de producción actualizada correctamente.", "success")
        return redirect(url_for("produccion.produccion_view"))

    return render_template(
        "private/produccion/produccion_update.html",
        form=create_form,
        orden_db=orden_db,
    )


@produccion.route("/private/produccion/finalizar", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def finalizar_produccion():
    id_orden = request.args.get("id")
    orden_db = OrdenProduccion.query.filter_by(id_orden_produccion=id_orden).first()

    if not orden_db:
        flash("Orden de producción no encontrada.", "danger")
        return redirect(url_for("produccion.produccion_view"))

    if orden_db.estado in ["COMPLETADA", "CANCELADA"]:
        flash("Esta orden ya no puede finalizarse.", "warning")
        return redirect(url_for("produccion.produccion_view"))

    resumen_cierre = []

    for detalle in orden_db.detalles:
        cantidad_teorica = Decimal(str(detalle.cantidad_teorica or 0))
        cantidad_consumida = Decimal(str(detalle.cantidad_consumida or 0))
        excedente = cantidad_consumida - cantidad_teorica
        if excedente < 0:
            excedente = Decimal("0")

        resumen_cierre.append({
            "detalle": detalle,
            "cantidad_teorica": cantidad_teorica,
            "cantidad_consumida": cantidad_consumida,
            "excedente": excedente,
        })

    if request.method == "POST":
        detalles_merma = []
        hubo_error = False

        insuficientes = []
        for item in resumen_cierre:
            detalle = item["detalle"]
            materia_db = MateriaPrima.query.filter_by(id_materia_prima=detalle.id_materia_prima).first()
            if not materia_db:
                insuficientes.append(f"{detalle.materia_prima_nombre} no existe")
                continue

            stock_actual = Decimal(str(materia_db.stock_actual or 0))
            cantidad_consumida = Decimal(str(detalle.cantidad_consumida or 0))

            if stock_actual < cantidad_consumida:
                insuficientes.append(
                    f"{detalle.materia_prima_nombre} (requiere {cantidad_consumida}, hay {stock_actual})"
                )

        if insuficientes:
            flash("No hay suficiente materia prima para finalizar la orden.", "danger")
            detalle_log = truncar_detalle_auditoria(
                f"Orden {orden_db.folio}. Insumos insuficientes: {', '.join(insuficientes)}"
            )

            log_event(
                modulo="Producción",
                accion="Finalización rechazada por stock insuficiente",
                detalle=detalle_log,
                severidad="ERROR",
            )
            return render_template(
                "private/produccion/produccion_finalizar.html",
                orden_db=orden_db,
                resumen_cierre=resumen_cierre,
            )

        for item in resumen_cierre:
            detalle = item["detalle"]
            excedente = item["excedente"]

            regresar_mp = parse_decimal(request.form.get(f"regresar_mp_{detalle.id_orden_produccion_detalle}", "0"))
            enviar_merma = parse_decimal(request.form.get(f"enviar_merma_{detalle.id_orden_produccion_detalle}", "0"))

            if regresar_mp < 0 or enviar_merma < 0:
                flash(f"No se permiten cantidades negativas en {detalle.materia_prima_nombre}.", "danger")
                hubo_error = True
                break

            if regresar_mp + enviar_merma != excedente:
                flash(
                    f"En {detalle.materia_prima_nombre}, la suma de regresar a MP + enviar a merma debe ser exactamente {excedente}.",
                    "danger"
                )
                hubo_error = True
                break

        if hubo_error:
            return render_template(
                "private/produccion/produccion_finalizar.html",
                orden_db=orden_db,
                resumen_cierre=resumen_cierre,
            )

        total_merma = Decimal("0")
        total_reintegrado = Decimal("0")

        for item in resumen_cierre:
            detalle = item["detalle"]
            materia_db = MateriaPrima.query.filter_by(id_materia_prima=detalle.id_materia_prima).first()
            if not materia_db:
                continue

            cantidad_consumida = Decimal(str(detalle.cantidad_consumida or 0))
            regresar_mp = parse_decimal(request.form.get(f"regresar_mp_{detalle.id_orden_produccion_detalle}", "0"))
            enviar_merma = parse_decimal(request.form.get(f"enviar_merma_{detalle.id_orden_produccion_detalle}", "0"))

            materia_db.stock_actual = Decimal(str(materia_db.stock_actual or 0)) - cantidad_consumida

            if regresar_mp > 0:
                materia_db.stock_actual += regresar_mp
                total_reintegrado += regresar_mp

            db.session.add(materia_db)

            if enviar_merma > 0:
                valor_unit = Decimal(str(materia_db.costo_unit_prom or 0))
                detalles_merma.append({
                    "id_materia_prima": materia_db.id_materia_prima,
                    "materia_prima_nombre": materia_db.nombre,
                    "unidad_medida": detalle.unidad_medida,
                    "cantidad": enviar_merma,
                    "clasificacion": "MERMA_PROCESO",
                    "valor_estimado_unit": valor_unit,
                    "valor_estimado_total": enviar_merma * valor_unit,
                })
                total_merma += enviar_merma

        producto_db = Producto.query.filter_by(id_producto=orden_db.id_producto).first()
        if producto_db:
            producto_db.stock_actual = Decimal(str(producto_db.stock_actual or 0)) + Decimal(str(orden_db.cantidad or 0))
            db.session.add(producto_db)

        orden_db.estado = "COMPLETADA"
        db.session.add(orden_db)

        if detalles_merma:
            merma_db = Merma(
                id_orden_produccion=orden_db.id_orden_produccion,
                tipo="RECUPERABLE",
                estado="DISPONIBLE",
                observaciones=f"Merma capturada manualmente al finalizar la orden {orden_db.folio}",
            )
            db.session.add(merma_db)
            db.session.flush()

            for det in detalles_merma:
                db.session.add(MermaDetalle(
                    id_merma=merma_db.id_merma,
                    id_materia_prima=det["id_materia_prima"],
                    materia_prima_nombre=det["materia_prima_nombre"],
                    unidad_medida=det["unidad_medida"],
                    cantidad=det["cantidad"],
                    clasificacion=det["clasificacion"],
                    valor_estimado_unit=det["valor_estimado_unit"],
                    valor_estimado_total=det["valor_estimado_total"],
                ))

        db.session.commit()

        log_event(
            modulo="Producción",
            accion="Orden de producción finalizada",
            detalle=(
                f"Orden {orden_db.folio} finalizada. "
                f"Producto terminado +{orden_db.cantidad}. "
                f"Sobrante reintegrado MP: {total_reintegrado}. "
                f"Merma generada: {total_merma}."
            ),
            severidad="INFO",
        )

        flash("Orden finalizada correctamente.", "success")
        return redirect(url_for("produccion.produccion_view"))

    return render_template(
        "private/produccion/produccion_finalizar.html",
        orden_db=orden_db,
        resumen_cierre=resumen_cierre,
    )


@produccion.route("/private/produccion/delete", methods=["GET", "POST"])
@login_required(["ADMIN"])
def eliminar_produccion():
    id_orden = request.args.get("id")

    orden_db = OrdenProduccion.query.filter(OrdenProduccion.id_orden_produccion == id_orden).first()
    if not orden_db:
        flash("Orden de producción no encontrada.", "danger")
        return redirect(url_for("produccion.produccion_view"))

    if orden_db.estado == "COMPLETADA":
        flash("No se puede cancelar una orden completada.", "danger")
        return redirect(url_for("produccion.produccion_view"))

    orden_db.estado = "CANCELADA"
    db.session.add(orden_db)
    db.session.commit()

    log_event(
        modulo="Producción",
        accion="Orden de producción cancelada",
        detalle=f"Orden {orden_db.folio} cancelada",
        severidad="WARNING",
    )
    flash("Orden de producción cancelada correctamente.", "success")
    return redirect(url_for("produccion.produccion_view"))