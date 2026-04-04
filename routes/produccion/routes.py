from decimal import Decimal
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
)
from utils.auth import login_required
from utils.audit import log_event
from . import produccion


def cargar_productos_produccion(form):
    productos = (
        Producto.query
        .filter_by(activo=1)
        .order_by(Producto.nombre.asc())
        .all()
    )
    form.id_producto.choices = [
        (p.id_producto, p.nombre) for p in productos
    ]


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

        cantidad_base = Decimal(str(detalle.cantidad or 0))
        cantidad_requerida = cantidad_base * factor
        costo_unitario = Decimal(str(detalle.materia_prima.costo_unit_prom or 0))
        subtotal = cantidad_requerida * costo_unitario
        stock_actual = Decimal(str(detalle.materia_prima.stock_actual or 0))

        resumen.append({
            "id_materia_prima": detalle.materia_prima.id_materia_prima,
            "nombre": detalle.materia_prima.nombre,
            "unidad_medida": detalle.materia_prima.unidad_medida_rel.nombre,
            "cantidad_base": cantidad_base,
            "cantidad_requerida": cantidad_requerida,
            "stock_actual": stock_actual,
            "costo_unitario": costo_unitario,
            "subtotal": subtotal,
            "suficiente": stock_actual >= cantidad_requerida,
        })

    return resumen


@produccion.route("/private/produccion")
@login_required(["ADMIN", "EMPLEADO"])
def produccion_view():
    create_form = forms.ProduccionForm()
    cargar_productos_produccion(create_form)

    producciones_db = (
        OrdenProduccion.query
        .order_by(OrdenProduccion.id_orden_produccion.desc())
        .all()
    )

    total_producciones = len(producciones_db)

    producciones_completadas = sum(
        1 for orden in producciones_db if orden.estado == "COMPLETADA"
    )
    producciones_canceladas = sum(
        1 for orden in producciones_db if orden.estado == "CANCELADA"
    )
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

    resumen_materiales = []
    producto_db = None
    receta_db = None
    costo_total = Decimal("0")

    if request.method == "POST":
        if create_form.validate():
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

            cantidad_producir = Decimal(str(create_form.cantidad.data))
            resumen_materiales = obtener_resumen_receta_para_produccion(
                receta_db, cantidad_producir
            )

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

            costo_total = sum(
                (item["subtotal"] for item in resumen_materiales),
                Decimal("0")
            )

            estado_nuevo = create_form.estado.data

            if estado_nuevo == "COMPLETADA":
                insuficientes = [item for item in resumen_materiales if not item["suficiente"]]

                if insuficientes:
                    detalle_error = ", ".join(
                        f"{item['nombre']} (requiere {item['cantidad_requerida']} {item['unidad_medida']}, hay {item['stock_actual']})"
                        for item in insuficientes
                    )

                    log_event(
                        modulo="Producción",
                        accion="Producción rechazada por stock insuficiente",
                        detalle=f"No fue posible completar producción de '{producto_db.nombre}'. Insumos insuficientes: {detalle_error}",
                        severidad="ERROR",
                    )

                    flash("No hay suficiente materia prima para completar la producción.", "danger")
                    return render_template(
                        "private/produccion/produccion_create.html",
                        form=create_form,
                        resumen_materiales=resumen_materiales,
                        producto_db=producto_db,
                        receta_db=receta_db,
                        costo_total=costo_total,
                    )

            orden_db = OrdenProduccion(
                id_producto=producto_db.id_producto,
                folio=generar_folio_produccion(),
                cantidad=cantidad_producir,
                estado=estado_nuevo,
                costo_estimado=costo_total,
                observaciones=(
                    create_form.observaciones.data.strip()
                    if create_form.observaciones.data
                    else None
                ),
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
                    cantidad_consumida=item["cantidad_requerida"],
                    costo_unitario=item["costo_unitario"],
                    subtotal=item["subtotal"],
                )
                db.session.add(detalle_orden)

            if estado_nuevo == "COMPLETADA":
                for item in resumen_materiales:
                    materia_db = MateriaPrima.query.filter_by(
                        id_materia_prima=item["id_materia_prima"]
                    ).first()

                    if materia_db:
                        materia_db.stock_actual = (
                            Decimal(str(materia_db.stock_actual or 0)) - item["cantidad_requerida"]
                        )
                        db.session.add(materia_db)

                producto_db.stock_actual = (
                    Decimal(str(producto_db.stock_actual or 0)) + cantidad_producir
                )
                db.session.add(producto_db)

            db.session.commit()

            log_event(
                modulo="Producción",
                accion=f"Orden de producción {estado_nuevo.lower()}",
                detalle=(
                    f"Orden {orden_db.folio} registrada para '{producto_db.nombre}' "
                    f"con estado {estado_nuevo} y cantidad {cantidad_producir}"
                ),
                severidad="INFO" if estado_nuevo != "CANCELADA" else "WARNING",
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
    create_form = forms.ProduccionForm()
    cargar_productos_produccion(create_form)

    id_orden = request.args.get("id")
    orden_db = (
        OrdenProduccion.query
        .filter(OrdenProduccion.id_orden_produccion == id_orden)
        .first()
    )

    if not orden_db:
        flash("Orden de producción no encontrada.", "danger")
        return redirect(url_for("produccion.produccion_view"))

    if request.method == "GET":
        create_form.id_producto.data = orden_db.id_producto
        create_form.cantidad.data = orden_db.cantidad
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

        if estado_anterior in ["COMPLETADA", "CANCELADA"]:
            flash("No se puede modificar una orden completada o cancelada.", "danger")
            return redirect(url_for("produccion.produccion_view"))

        orden_db.observaciones = (
            create_form.observaciones.data.strip()
            if create_form.observaciones.data
            else None
        )
        orden_db.estado = estado_nuevo

        if estado_anterior != "COMPLETADA" and estado_nuevo == "COMPLETADA":
            insuficientes = []

            for detalle in orden_db.detalles:
                materia_db = MateriaPrima.query.filter_by(
                    id_materia_prima=detalle.id_materia_prima
                ).first()

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
                flash("No hay suficiente materia prima para completar la orden.", "danger")
                return render_template(
                    "private/produccion/produccion_update.html",
                    form=create_form,
                    orden_db=orden_db,
                )

            for detalle in orden_db.detalles:
                materia_db = MateriaPrima.query.filter_by(
                    id_materia_prima=detalle.id_materia_prima
                ).first()

                if materia_db:
                    materia_db.stock_actual = (
                        Decimal(str(materia_db.stock_actual or 0)) -
                        Decimal(str(detalle.cantidad_consumida or 0))
                    )
                    db.session.add(materia_db)

            producto_db = Producto.query.filter_by(id_producto=orden_db.id_producto).first()
            if producto_db:
                producto_db.stock_actual = (
                    Decimal(str(producto_db.stock_actual or 0)) +
                    Decimal(str(orden_db.cantidad or 0))
                )
                db.session.add(producto_db)

        db.session.add(orden_db)
        db.session.commit()

        log_event(
            modulo="Producción",
            accion="Orden de producción actualizada",
            detalle=f"Orden {orden_db.folio} cambió de {estado_anterior} a {estado_nuevo}",
            severidad="INFO" if estado_nuevo != "CANCELADA" else "WARNING",
        )

        flash("Orden de producción actualizada correctamente.", "success")
        return redirect(url_for("produccion.produccion_view"))

    return render_template(
        "private/produccion/produccion_update.html",
        form=create_form,
        orden_db=orden_db,
    )


@produccion.route("/private/produccion/delete", methods=["GET", "POST"])
@login_required(["ADMIN"])
def eliminar_produccion():
    id_orden = request.args.get("id")
    orden_db = (
        OrdenProduccion.query
        .filter(OrdenProduccion.id_orden_produccion == id_orden)
        .first()
    )

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