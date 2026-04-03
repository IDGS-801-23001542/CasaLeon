from decimal import Decimal, InvalidOperation
import datetime

from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import or_

import forms
from models import (
    db,
    MateriaPrima,
    Receta,
    RecetaDetalle,
    Producto,
    AuditoriaLog,
    OrdenProduccion,
    OrdenProduccionDetalle,
)
from utils.auth import login_required
from utils.audit import log_event
from . import operaciones


#MATERIA PRIMA

@operaciones.route("/private/materia-prima")
@login_required(["ADMIN", "EMPLEADO"])
def materia_prima():
    create_form = forms.MateriaPrimaForm()
    search = request.args.get("search", "").strip()

    query = MateriaPrima.query

    if search:
        like_term = f"%{search}%"
        query = query.filter(
            or_(
                MateriaPrima.nombre.ilike(like_term),
                MateriaPrima.categoria.ilike(like_term),
                MateriaPrima.unidad_medida.ilike(like_term),
            )
        )

    materias_db = query.order_by(MateriaPrima.nombre.asc()).all()

    total_materias = MateriaPrima.query.count()
    materias_activas = MateriaPrima.query.filter_by(activo=1).count()
    materias_inactivas = MateriaPrima.query.filter_by(activo=0).count()

    stock_bajo = sum(
        1
        for materia in MateriaPrima.query.all()
        if float(materia.stock_actual or 0) <= float(materia.stock_minimo or 0)
    )

    valor_inventario = sum(
        float(materia.stock_actual or 0) * float(materia.costo_unit_prom or 0)
        for materia in MateriaPrima.query.all()
    )

    return render_template(
        "private/materia_prima/materia_prima.html",
        form=create_form,
        materias_db=materias_db,
        total_materias=total_materias,
        materias_activas=materias_activas,
        materias_inactivas=materias_inactivas,
        stock_bajo=stock_bajo,
        valor_inventario=f"{valor_inventario:,.2f}",
        search=search,
    )


@operaciones.route("/private/materia-prima/create", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def crear_materia_prima():
    create_form = forms.MateriaPrimaForm()

    if request.method == "POST":
        if create_form.validate():
            nombre = create_form.nombre.data.strip()

            existe_nombre = MateriaPrima.query.filter(
                db.func.lower(MateriaPrima.nombre) == nombre.lower()
            ).first()

            if existe_nombre:
                flash("Ya existe una materia prima con ese nombre.", "warning")
                return render_template(
                    "private/materia_prima/materia_prima_create.html",
                    form=create_form,
                )

            materia = MateriaPrima(
                nombre=nombre,
                categoria=create_form.categoria.data.strip(),
                unidad_medida=create_form.unidad_medida.data.strip(),
                stock_actual=create_form.stock_actual.data,
                stock_minimo=create_form.stock_minimo.data,
                costo_unit_prom=create_form.costo_unit_prom.data,
                merma_pct=create_form.merma_pct.data,
                activo=1,
            )

            db.session.add(materia)
            db.session.commit()

            log_event(
                modulo="Inventario",
                accion="Materia prima creada",
                detalle=(
                    f"Materia prima '{materia.nombre}' creada con stock "
                    f"{materia.stock_actual} {materia.unidad_medida}"
                ),
                severidad="INFO",
            )

            flash("Materia prima creada correctamente.", "success")
            return redirect(url_for("operaciones.materia_prima"))

    return render_template(
        "private/materia_prima/materia_prima_create.html",
        form=create_form,
    )


@operaciones.route("/private/materia-prima/update", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def actualizar_materia_prima():
    create_form = forms.MateriaPrimaForm()

    id_materia = request.args.get("id")
    materia_db = (
        db.session.query(MateriaPrima)
        .filter(MateriaPrima.id_materia_prima == id_materia)
        .first()
    )

    if not materia_db:
        flash("Materia prima no encontrada.", "danger")
        return redirect(url_for("operaciones.materia_prima"))

    if request.method == "GET":
        create_form.nombre.data = materia_db.nombre
        create_form.categoria.data = materia_db.categoria
        create_form.unidad_medida.data = materia_db.unidad_medida
        create_form.stock_actual.data = materia_db.stock_actual
        create_form.stock_minimo.data = materia_db.stock_minimo
        create_form.costo_unit_prom.data = materia_db.costo_unit_prom
        create_form.merma_pct.data = materia_db.merma_pct

        return render_template(
            "private/materia_prima/materia_prima_update.html",
            form=create_form,
            materia_db=materia_db,
        )

    if create_form.validate():
        nombre = create_form.nombre.data.strip()

        existe_nombre = MateriaPrima.query.filter(
            db.func.lower(MateriaPrima.nombre) == nombre.lower(),
            MateriaPrima.id_materia_prima != materia_db.id_materia_prima,
        ).first()

        if existe_nombre:
            flash("Ya existe otra materia prima con ese nombre.", "warning")
            return render_template(
                "private/materia_prima/materia_prima_update.html",
                form=create_form,
                materia_db=materia_db,
            )

        materia_db.nombre = nombre
        materia_db.categoria = create_form.categoria.data.strip()
        materia_db.unidad_medida = create_form.unidad_medida.data.strip()
        materia_db.stock_actual = create_form.stock_actual.data
        materia_db.stock_minimo = create_form.stock_minimo.data
        materia_db.costo_unit_prom = create_form.costo_unit_prom.data
        materia_db.merma_pct = create_form.merma_pct.data

        db.session.add(materia_db)
        db.session.commit()

        log_event(
            modulo="Inventario",
            accion="Materia prima actualizada",
            detalle=f"Materia prima '{materia_db.nombre}' actualizada",
            severidad="INFO",
        )

        flash("Materia prima actualizada correctamente.", "success")
        return redirect(url_for("operaciones.materia_prima"))

    return render_template(
        "private/materia_prima/materia_prima_update.html",
        form=create_form,
        materia_db=materia_db,
    )


@operaciones.route("/private/materia-prima/delete", methods=["GET", "POST"])
@login_required(["ADMIN"])
def eliminar_materia_prima():
    create_form = forms.MateriaPrimaForm()

    id_materia = request.args.get("id")
    materia_db = (
        db.session.query(MateriaPrima)
        .filter(MateriaPrima.id_materia_prima == id_materia)
        .first()
    )

    if not materia_db:
        flash("Materia prima no encontrada.", "danger")
        return redirect(url_for("operaciones.materia_prima"))

    if request.method == "GET":
        create_form.nombre.data = materia_db.nombre
        create_form.categoria.data = materia_db.categoria
        create_form.unidad_medida.data = materia_db.unidad_medida
        create_form.stock_actual.data = materia_db.stock_actual
        create_form.stock_minimo.data = materia_db.stock_minimo
        create_form.costo_unit_prom.data = materia_db.costo_unit_prom
        create_form.merma_pct.data = materia_db.merma_pct

        return render_template(
            "private/materia_prima/materia_prima_delete.html",
            form=create_form,
            materia_db=materia_db,
        )

    materia_db.activo = 0
    db.session.add(materia_db)
    db.session.commit()

    log_event(
        modulo="Inventario",
        accion="Materia prima desactivada",
        detalle=f"Materia prima '{materia_db.nombre}' marcada como inactiva",
        severidad="WARNING",
    )

    flash("Materia prima desactivada correctamente.", "info")
    return redirect(url_for("operaciones.materia_prima"))


@operaciones.route("/private/materia-prima/movimiento", methods=["POST"])
@login_required(["ADMIN", "EMPLEADO"])
def movimiento_materia_prima():
    id_materia = request.form.get("id")
    tipo = (request.form.get("tipo") or "").strip().upper()
    motivo = (request.form.get("motivo") or "").strip()

    materia_db = (
        db.session.query(MateriaPrima)
        .filter(MateriaPrima.id_materia_prima == id_materia)
        .first()
    )

    if not materia_db:
        flash("Materia prima no encontrada.", "danger")
        return redirect(url_for("operaciones.materia_prima"))

    try:
        cantidad = Decimal(request.form.get("cantidad", "0"))
    except (InvalidOperation, TypeError):
        flash("La cantidad ingresada no es válida.", "danger")
        return redirect(url_for("operaciones.materia_prima"))

    if cantidad <= 0:
        flash("La cantidad debe ser mayor a 0.", "warning")
        return redirect(url_for("operaciones.materia_prima"))

    stock_actual = Decimal(str(materia_db.stock_actual or 0))

    if tipo == "ENTRADA":
        materia_db.stock_actual = stock_actual + cantidad

        log_event(
            modulo="Inventario",
            accion="Entrada de materia prima",
            detalle=(
                f"Entrada de {cantidad} {materia_db.unidad_medida} a "
                f"'{materia_db.nombre}'. Motivo: {motivo or 'Sin motivo'}"
            ),
            severidad="INFO",
        )

    elif tipo == "SALIDA":
        if stock_actual < cantidad:
            flash("No se permite stock negativo.", "danger")
            return redirect(url_for("operaciones.materia_prima"))

        materia_db.stock_actual = stock_actual - cantidad

        log_event(
            modulo="Inventario",
            accion="Salida de materia prima",
            detalle=(
                f"Salida de {cantidad} {materia_db.unidad_medida} de "
                f"'{materia_db.nombre}'. Motivo: {motivo or 'Sin motivo'}"
            ),
            severidad="WARNING",
        )
    else:
        flash("Tipo de movimiento inválido.", "danger")
        return redirect(url_for("operaciones.materia_prima"))

    db.session.add(materia_db)
    db.session.commit()

    flash("Movimiento registrado correctamente.", "success")
    return redirect(url_for("operaciones.materia_prima"))




# RECETAS

def cargar_productos_receta(form):
    productos = Producto.query.filter_by(activo=1).order_by(Producto.nombre.asc()).all()
    form.id_producto.choices = [
        (p.id_producto, p.nombre) for p in productos
    ]


def obtener_materias_primas_activas():
    return MateriaPrima.query.filter_by(activo=1).order_by(MateriaPrima.nombre.asc()).all()


def calcular_costo_receta(receta):
    total = Decimal("0")

    for detalle in receta.detalles:
        if detalle.materia_prima:
            total += Decimal(str(detalle.cantidad or 0)) * Decimal(
                str(detalle.materia_prima.costo_unit_prom or 0)
            )

    receta.costo_estimado = total


def extraer_detalles_receta_desde_form():
    ids_materia = request.form.getlist("id_materia_prima[]")
    cantidades = request.form.getlist("cantidad[]")

    detalles = []
    errores = []

    if not ids_materia or not cantidades or len(ids_materia) != len(cantidades):
        errores.append("Debes capturar al menos un insumo válido.")
        return detalles, errores

    for i, (id_mp, cantidad_raw) in enumerate(zip(ids_materia, cantidades), start=1):
        id_mp = (id_mp or "").strip()
        cantidad_raw = (cantidad_raw or "").strip()

        if not id_mp and not cantidad_raw:
            continue

        if not id_mp:
            errores.append(f"Falta seleccionar materia prima en la fila {i}.")
            continue

        if not cantidad_raw:
            errores.append(f"Falta capturar cantidad en la fila {i}.")
            continue

        try:
            id_materia = int(id_mp)
        except ValueError:
            errores.append(f"La materia prima de la fila {i} no es válida.")
            continue

        try:
            cantidad = Decimal(cantidad_raw)
        except InvalidOperation:
            errores.append(f"La cantidad de la fila {i} no es válida.")
            continue

        if cantidad <= 0:
            errores.append(f"La cantidad de la fila {i} debe ser mayor a 0.")
            continue

        materia = MateriaPrima.query.filter_by(
            id_materia_prima=id_materia,
            activo=1
        ).first()

        if not materia:
            errores.append(f"La materia prima de la fila {i} no existe o está inactiva.")
            continue

        detalles.append({
            "id_materia_prima": id_materia,
            "cantidad": cantidad,
            "materia_nombre": materia.nombre,
            "unidad_medida": materia.unidad_medida,
        })

    if not detalles:
        errores.append("Debes agregar al menos un insumo a la receta.")

    # Evitar materias primas repetidas
    ids_usados = [d["id_materia_prima"] for d in detalles]
    if len(ids_usados) != len(set(ids_usados)):
        errores.append("No puedes repetir la misma materia prima en la receta.")

    return detalles, errores


@operaciones.route("/private/recetas")
@login_required("ADMIN")
def recetas():
    create_form = forms.RecetaForm()
    cargar_productos_receta(create_form)

    search = request.args.get("search", "").strip()

    query = Receta.query.join(Producto)

    if search:
        like_term = f"%{search}%"
        query = query.filter(
            or_(
                Receta.nombre.ilike(like_term),
                Producto.nombre.ilike(like_term),
            )
        )

    recetas_db = query.order_by(Receta.nombre.asc()).all()

    total_recetas = Receta.query.count()
    recetas_activas = Receta.query.filter_by(activo=1).count()
    recetas_inactivas = Receta.query.filter_by(activo=0).count()

    costo_total = sum(float(receta.costo_estimado or 0) for receta in Receta.query.all())

    return render_template(
        "private/recetas/recetas.html",
        form=create_form,
        recetas_db=recetas_db,
        total_recetas=total_recetas,
        recetas_activas=recetas_activas,
        recetas_inactivas=recetas_inactivas,
        costo_total=f"{costo_total:,.2f}",
        search=search,
    )


@operaciones.route("/private/recetas/create", methods=["GET", "POST"])
@login_required("ADMIN")
def crear_receta():
    create_form = forms.RecetaForm()
    cargar_productos_receta(create_form)
    materias_primas = obtener_materias_primas_activas()

    detalles_form = []

    if request.method == "POST":
        detalles_form, errores_detalle = extraer_detalles_receta_desde_form()

        if create_form.validate() and not errores_detalle:
            id_producto = create_form.id_producto.data
            nombre = create_form.nombre.data.strip()

            existe_producto = Receta.query.filter_by(id_producto=id_producto).first()
            if existe_producto:
                flash("Ese producto ya tiene una receta registrada.", "warning")
                return render_template(
                    "private/recetas/recetas_create.html",
                    form=create_form,
                    materias_primas=materias_primas,
                    detalles_form=detalles_form,
                )

            receta = Receta(
                id_producto=id_producto,
                nombre=nombre,
                rendimiento=int(create_form.rendimiento.data),
                costo_estimado=0,
                activo=1,
            )

            db.session.add(receta)
            db.session.flush()

            for detalle in detalles_form:
                nuevo_detalle = RecetaDetalle(
                    id_receta=receta.id_receta,
                    id_materia_prima=detalle["id_materia_prima"],
                    cantidad=detalle["cantidad"],
                )
                db.session.add(nuevo_detalle)

            db.session.flush()
            calcular_costo_receta(receta)
            db.session.commit()

            log_event(
                modulo="Recetas",
                accion="Receta creada",
                detalle=f"Receta '{receta.nombre}' creada con {len(detalles_form)} insumo(s)",
                severidad="INFO",
            )

            flash("Receta creada correctamente.", "success")
            return redirect(url_for("operaciones.recetas"))

        for error in errores_detalle:
            flash(error, "warning")

    return render_template(
        "private/recetas/recetas_create.html",
        form=create_form,
        materias_primas=materias_primas,
        detalles_form=detalles_form,
    )


@operaciones.route("/private/recetas/update", methods=["GET", "POST"])
@login_required("ADMIN")
def actualizar_receta():
    create_form = forms.RecetaForm()
    cargar_productos_receta(create_form)
    materias_primas = obtener_materias_primas_activas()

    id_receta = request.args.get("id")
    receta_db = db.session.query(Receta).filter(Receta.id_receta == id_receta).first()

    if not receta_db:
        flash("Receta no encontrada.", "danger")
        return redirect(url_for("operaciones.recetas"))

    if request.method == "GET":
        create_form.id_producto.data = receta_db.id_producto
        create_form.nombre.data = receta_db.nombre
        create_form.rendimiento.data = receta_db.rendimiento

        detalles_form = [
            {
                "id_materia_prima": detalle.id_materia_prima,
                "cantidad": detalle.cantidad,
                "materia_nombre": detalle.materia_prima.nombre if detalle.materia_prima else "",
                "unidad_medida": detalle.materia_prima.unidad_medida if detalle.materia_prima else "",
            }
            for detalle in receta_db.detalles
        ]

        return render_template(
            "private/recetas/recetas_update.html",
            form=create_form,
            receta_db=receta_db,
            materias_primas=materias_primas,
            detalles_form=detalles_form,
        )

    detalles_form, errores_detalle = extraer_detalles_receta_desde_form()

    if create_form.validate() and not errores_detalle:
        existe_producto = Receta.query.filter(
            Receta.id_producto == create_form.id_producto.data,
            Receta.id_receta != receta_db.id_receta,
        ).first()

        if existe_producto:
            flash("Ese producto ya tiene otra receta registrada.", "warning")
            return render_template(
                "private/recetas/recetas_update.html",
                form=create_form,
                receta_db=receta_db,
                materias_primas=materias_primas,
                detalles_form=detalles_form,
            )

        receta_db.id_producto = create_form.id_producto.data
        receta_db.nombre = create_form.nombre.data.strip()
        receta_db.rendimiento = int(create_form.rendimiento.data)

        RecetaDetalle.query.filter_by(id_receta=receta_db.id_receta).delete()

        for detalle in detalles_form:
            nuevo_detalle = RecetaDetalle(
                id_receta=receta_db.id_receta,
                id_materia_prima=detalle["id_materia_prima"],
                cantidad=detalle["cantidad"],
            )
            db.session.add(nuevo_detalle)

        db.session.flush()
        calcular_costo_receta(receta_db)
        db.session.commit()

        log_event(
            modulo="Recetas",
            accion="Receta actualizada",
            detalle=f"Receta '{receta_db.nombre}' actualizada con {len(detalles_form)} insumo(s)",
            severidad="INFO",
        )

        flash("Receta actualizada correctamente.", "success")
        return redirect(url_for("operaciones.recetas"))

    for error in errores_detalle:
        flash(error, "warning")

    return render_template(
        "private/recetas/recetas_update.html",
        form=create_form,
        receta_db=receta_db,
        materias_primas=materias_primas,
        detalles_form=detalles_form,
    )


@operaciones.route("/private/recetas/delete", methods=["GET", "POST"])
@login_required("ADMIN")
def eliminar_receta():
    create_form = forms.RecetaForm()
    cargar_productos_receta(create_form)

    id_receta = request.args.get("id")
    receta_db = db.session.query(Receta).filter(Receta.id_receta == id_receta).first()

    if not receta_db:
        flash("Receta no encontrada.", "danger")
        return redirect(url_for("operaciones.recetas"))

    if request.method == "GET":
        create_form.id_producto.data = receta_db.id_producto
        create_form.nombre.data = receta_db.nombre
        create_form.rendimiento.data = receta_db.rendimiento

        return render_template(
            "private/recetas/recetas_delete.html",
            form=create_form,
            receta_db=receta_db,
        )

    receta_db.activo = 0
    db.session.add(receta_db)
    db.session.commit()

    log_event(
        modulo="Recetas",
        accion="Receta desactivada",
        detalle=f"Receta '{receta_db.nombre}' marcada como inactiva",
        severidad="WARNING",
    )

    flash("Receta desactivada correctamente.", "info")
    return redirect(url_for("operaciones.recetas"))


# PRODUCCIÓN

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


def obtener_resumen_receta_para_produccion(receta, cantidad_producir):
    resumen = []
    cantidad_producir = Decimal(str(cantidad_producir))
    rendimiento = Decimal(str(receta.rendimiento or 1))

    if rendimiento <= 0:
        rendimiento = Decimal("1")

    factor = cantidad_producir / rendimiento

    for detalle in receta.detalles:
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
            "unidad_medida": detalle.materia_prima.unidad_medida,
            "cantidad_base": cantidad_base,
            "cantidad_requerida": cantidad_requerida,
            "stock_actual": stock_actual,
            "costo_unitario": costo_unitario,
            "subtotal": subtotal,
            "suficiente": stock_actual >= cantidad_requerida,
        })

    return resumen


@operaciones.route("/private/produccion")
@login_required(["ADMIN", "EMPLEADO"])
def produccion():
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


@operaciones.route("/private/produccion/create", methods=["GET", "POST"])
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

            insuficientes = [item for item in resumen_materiales if not item["suficiente"]]

            if insuficientes:
                detalle_error = ", ".join(
                    f"{item['nombre']} (requiere {item['cantidad_requerida']} {item['unidad_medida']}, hay {item['stock_actual']})"
                    for item in insuficientes
                )

                log_event(
                    modulo="Producción",
                    accion="Producción rechazada por stock insuficiente",
                    detalle=f"No fue posible producir '{producto_db.nombre}'. Insumos insuficientes: {detalle_error}",
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

            costo_total = sum(
                (item["subtotal"] for item in resumen_materiales),
                Decimal("0")
            )

            estado_nuevo = create_form.estado.data

            orden = OrdenProduccion(
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

            db.session.add(orden)
            db.session.flush()

            for item in resumen_materiales:
                detalle_orden = OrdenProduccionDetalle(
                    id_orden_produccion=orden.id_orden_produccion,
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
                insuficientes = [item for item in resumen_materiales if not item["suficiente"]]

                if insuficientes:
                    db.session.rollback()

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
                    f"Orden {orden.folio} registrada para '{producto_db.nombre}' "
                    f"con estado {estado_nuevo} y cantidad {cantidad_producir}"
                ),
                severidad="INFO" if estado_nuevo != "CANCELADA" else "WARNING",
            )

            flash("Orden de producción registrada correctamente.", "success")
            return redirect(url_for("operaciones.produccion"))

    return render_template(
        "private/produccion/produccion_create.html",
        form=create_form,
        resumen_materiales=resumen_materiales,
        producto_db=producto_db,
        receta_db=receta_db,
        costo_total=costo_total,
    )


@operaciones.route("/private/produccion/update", methods=["GET", "POST"])
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
        return redirect(url_for("operaciones.produccion"))

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

        # No permitir modificar producto/cantidad si ya está completada o cancelada
        if estado_anterior in ["COMPLETADA", "CANCELADA"]:
            flash("No se puede modificar una orden completada o cancelada.", "danger")
            return redirect(url_for("operaciones.produccion"))

        orden_db.observaciones = (
            create_form.observaciones.data.strip()
            if create_form.observaciones.data
            else None
        )
        orden_db.estado = estado_nuevo

        # Si pasa a completada, ejecutar consumo real
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
        return redirect(url_for("operaciones.produccion"))

    return render_template(
        "private/produccion/produccion_update.html",
        form=create_form,
        orden_db=orden_db,
    )


@operaciones.route("/private/produccion/delete", methods=["GET", "POST"])
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
        return redirect(url_for("operaciones.produccion"))

    if orden_db.estado == "COMPLETADA":
        flash("No se puede cancelar una orden completada.", "danger")
        return redirect(url_for("operaciones.produccion"))

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
    return redirect(url_for("operaciones.produccion"))


@operaciones.route("/private/ventas")
@login_required(["ADMIN", "EMPLEADO"])
def ventas():
    return render_template(
        "private/shared/en_construccion.html",
        titulo="Ventas",
        subtitulo="Pantalla pendiente de integración final.",
    )


@operaciones.route("/private/reportes")
@login_required("ADMIN")
def reportes():
    return render_template(
        "private/shared/en_construccion.html",
        titulo="Reportes",
        subtitulo="Pantalla pendiente de integración final.",
    )