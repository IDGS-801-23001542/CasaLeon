from decimal import Decimal, InvalidOperation

from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import or_

import forms
from models import db, MateriaPrima, Receta, RecetaDetalle, Producto
from utils.auth import login_required
from utils.audit import log_event
from . import recetas


def cargar_productos_receta(form):
    productos = Producto.query.filter_by(activo=1).order_by(Producto.nombre.asc()).all()
    form.id_producto.choices = [(0, "Sin asignar")] + [
        (p.id_producto, p.nombre) for p in productos
    ]


def obtener_materias_primas_activas():
    return MateriaPrima.query.filter_by(activo=1).order_by(MateriaPrima.nombre.asc()).all()


def calcular_costo_receta(receta_db):
    total = Decimal("0")

    for detalle in receta_db.detalles:
        if detalle.materia_prima:
            total += Decimal(str(detalle.cantidad or 0)) * Decimal(
                str(detalle.materia_prima.costo_unit_prom or 0)
            )

    receta_db.costo_estimado = total


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
            "unidad_medida": materia.unidad_medida_rel.nombre,
        })

    if not detalles:
        errores.append("Debes agregar al menos un insumo a la receta.")

    ids_usados = [d["id_materia_prima"] for d in detalles]
    if len(ids_usados) != len(set(ids_usados)):
        errores.append("No puedes repetir la misma materia prima en la receta.")

    return detalles, errores


@recetas.route("/private/recetas")
@login_required("ADMIN")
def recetas_view():
    create_form = forms.RecetaForm()
    cargar_productos_receta(create_form)

    search = request.args.get("search", "").strip()

    query = Receta.query.outerjoin(Producto)

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


@recetas.route("/private/recetas/create", methods=["GET", "POST"])
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
            if id_producto == 0:
                id_producto = None
            nombre = create_form.nombre.data.strip()

            if id_producto is not None:
                existe_producto = Receta.query.filter_by(id_producto=id_producto).first()
                if existe_producto:
                    flash("Ese producto ya tiene una receta registrada.", "warning")
                    return render_template(
                        "private/recetas/recetas_create.html",
                        form=create_form,
                        materias_primas=materias_primas,
                        detalles_form=detalles_form,
                    )

            receta_db = Receta(
                id_producto=id_producto,
                nombre=nombre,
                rendimiento=int(create_form.rendimiento.data),
                costo_estimado=0,
                activo=1,
            )

            db.session.add(receta_db)
            db.session.flush()

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
                accion="Receta creada",
                detalle=f"Receta '{receta_db.nombre}' creada con {len(detalles_form)} insumo(s)",
                severidad="INFO",
            )

            flash("Receta creada correctamente.", "success")
            return redirect(url_for("recetas.recetas_view"))

        for error in errores_detalle:
            flash(error, "warning")

    return render_template(
        "private/recetas/recetas_create.html",
        form=create_form,
        materias_primas=materias_primas,
        detalles_form=detalles_form,
    )


@recetas.route("/private/recetas/update", methods=["GET", "POST"])
@login_required("ADMIN")
def actualizar_receta():
    create_form = forms.RecetaForm()
    cargar_productos_receta(create_form)
    materias_primas = obtener_materias_primas_activas()

    id_receta = request.args.get("id")
    receta_db = db.session.query(Receta).filter(Receta.id_receta == id_receta).first()

    if not receta_db:
        flash("Receta no encontrada.", "danger")
        return redirect(url_for("recetas.recetas_view"))

    if request.method == "GET":
        create_form.id_producto.data = receta_db.id_producto if receta_db.id_producto else 0
        create_form.nombre.data = receta_db.nombre
        create_form.rendimiento.data = receta_db.rendimiento

        detalles_form = [
            {
                "id_materia_prima": detalle.id_materia_prima,
                "cantidad": detalle.cantidad,
                "materia_nombre": detalle.materia_prima.nombre if detalle.materia_prima else "",
                "unidad_medida": detalle.materia_prima.unidad_medida_rel.nombre if detalle.materia_prima else "",
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
        id_producto = create_form.id_producto.data
        if id_producto == 0:
            id_producto = None

        if id_producto is not None:
            existe_producto = Receta.query.filter(
                Receta.id_producto == id_producto,
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

        receta_db.id_producto = id_producto
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
        return redirect(url_for("recetas.recetas_view"))

    for error in errores_detalle:
        flash(error, "warning")

    return render_template(
        "private/recetas/recetas_update.html",
        form=create_form,
        receta_db=receta_db,
        materias_primas=materias_primas,
        detalles_form=detalles_form,
    )


@recetas.route("/private/recetas/delete", methods=["GET", "POST"])
@login_required("ADMIN")
def eliminar_receta():
    create_form = forms.RecetaForm()
    cargar_productos_receta(create_form)

    id_receta = request.args.get("id")
    receta_db = db.session.query(Receta).filter(Receta.id_receta == id_receta).first()

    if not receta_db:
        flash("Receta no encontrada.", "danger")
        return redirect(url_for("recetas.recetas_view"))

    if request.method == "GET":
        create_form.id_producto.data = receta_db.id_producto if receta_db.id_producto else 0
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
    return redirect(url_for("recetas.recetas_view"))