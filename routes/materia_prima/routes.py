from decimal import Decimal, InvalidOperation

from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import or_

import forms
from models import (
    db,
    MateriaPrima,
    CategoriaMateriaPrima,
    UnidadMedida,
    Proveedor,
    MovimientoMateriaPrima,
)
from utils.auth import login_required
from utils.audit import log_event
from . import materia_prima


def cargar_catalogos_materia_prima(form):
    categorias = (
        CategoriaMateriaPrima.query
        .filter_by(activo=1)
        .order_by(CategoriaMateriaPrima.nombre.asc())
        .all()
    )
    unidades = (
        UnidadMedida.query
        .filter_by(activo=1)
        .order_by(UnidadMedida.nombre.asc())
        .all()
    )

    form.id_categoria_materia_prima.choices = [
        (c.id_categoria_materia_prima, c.nombre) for c in categorias
    ]
    form.id_unidad_medida.choices = [
        (u.id_unidad_medida, u.nombre) for u in unidades
    ]


def obtener_proveedores_activos():
    return (
        Proveedor.query
        .filter_by(activo=1)
        .order_by(Proveedor.nombre.asc())
        .all()
    )


@materia_prima.route("/private/materia-prima")
@login_required(["ADMIN", "EMPLEADO"])
def materia_prima_view():
    create_form = forms.MateriaPrimaForm()
    cargar_catalogos_materia_prima(create_form)

    proveedores_db = obtener_proveedores_activos()
    search = request.args.get("search", "").strip()

    query = MateriaPrima.query.join(CategoriaMateriaPrima).join(UnidadMedida)

    if search:
        like_term = f"%{search}%"
        query = query.filter(
            or_(
                MateriaPrima.nombre.ilike(like_term),
                CategoriaMateriaPrima.nombre.ilike(like_term),
                UnidadMedida.nombre.ilike(like_term),
            )
        )

    materias_db = query.order_by(MateriaPrima.nombre.asc()).all()

    todas_materias = MateriaPrima.query.all()

    total_materias = len(todas_materias)
    materias_activas = sum(1 for materia in todas_materias if materia.activo == 1)

    stock_bajo = sum(
        1
        for materia in todas_materias
        if float(materia.stock_actual or 0) > 0
        and float(materia.stock_actual or 0) <= float(materia.stock_minimo or 0)
    )

    sin_stock = sum(
        1
        for materia in todas_materias
        if float(materia.stock_actual or 0) == 0
    )

    valor_inventario = sum(
        float(materia.stock_actual or 0) * float(materia.costo_unit_prom or 0)
        for materia in todas_materias
    )

    return render_template(
        "private/materia_prima/materia_prima.html",
        form=create_form,
        materias_db=materias_db,
        proveedores_db=proveedores_db,
        total_materias=total_materias,
        materias_activas=materias_activas,
        stock_bajo=stock_bajo,
        sin_stock=sin_stock,
        valor_inventario=f"{valor_inventario:,.2f}",
        search=search,
    )


@materia_prima.route("/private/materia-prima/create", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def crear_materia_prima():
    create_form = forms.MateriaPrimaForm()
    cargar_catalogos_materia_prima(create_form)

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

            materia_db = MateriaPrima(
                nombre=nombre,
                id_categoria_materia_prima=create_form.id_categoria_materia_prima.data,
                id_unidad_medida=create_form.id_unidad_medida.data,
                stock_actual=create_form.stock_actual.data,
                stock_minimo=create_form.stock_minimo.data,
                costo_unit_prom=create_form.costo_unit_prom.data,
                activo=1,
            )

            db.session.add(materia_db)
            db.session.commit()

            log_event(
                modulo="Inventario",
                accion="Materia prima creada",
                detalle=(
                    f"Materia prima '{materia_db.nombre}' creada con stock "
                    f"{materia_db.stock_actual} "
                    f"{materia_db.unidad_medida_rel.nombre if materia_db.unidad_medida_rel else ''}"
                ),
                severidad="INFO",
            )

            flash("Materia prima creada correctamente.", "success")
            return redirect(url_for("materia_prima.materia_prima_view"))

    return render_template(
        "private/materia_prima/materia_prima_create.html",
        form=create_form,
    )


@materia_prima.route("/private/materia-prima/update", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def actualizar_materia_prima():
    create_form = forms.MateriaPrimaForm()
    cargar_catalogos_materia_prima(create_form)

    id_materia = request.args.get("id")
    materia_db = (
        db.session.query(MateriaPrima)
        .filter(MateriaPrima.id_materia_prima == id_materia)
        .first()
    )

    if not materia_db:
        flash("Materia prima no encontrada.", "danger")
        return redirect(url_for("materia_prima.materia_prima_view"))

    if request.method == "GET":
        create_form.nombre.data = materia_db.nombre
        create_form.id_categoria_materia_prima.data = materia_db.id_categoria_materia_prima
        create_form.id_unidad_medida.data = materia_db.id_unidad_medida
        create_form.stock_actual.data = materia_db.stock_actual
        create_form.stock_minimo.data = materia_db.stock_minimo
        create_form.costo_unit_prom.data = materia_db.costo_unit_prom

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
        materia_db.id_categoria_materia_prima = create_form.id_categoria_materia_prima.data
        materia_db.id_unidad_medida = create_form.id_unidad_medida.data
        materia_db.stock_actual = create_form.stock_actual.data
        materia_db.stock_minimo = create_form.stock_minimo.data
        materia_db.costo_unit_prom = create_form.costo_unit_prom.data

        db.session.add(materia_db)
        db.session.commit()

        log_event(
            modulo="Inventario",
            accion="Materia prima actualizada",
            detalle=f"Materia prima '{materia_db.nombre}' actualizada",
            severidad="INFO",
        )

        flash("Materia prima actualizada correctamente.", "success")
        return redirect(url_for("materia_prima.materia_prima_view"))

    return render_template(
        "private/materia_prima/materia_prima_update.html",
        form=create_form,
        materia_db=materia_db,
    )


@materia_prima.route("/private/materia-prima/delete", methods=["GET", "POST"])
@login_required(["ADMIN"])
def eliminar_materia_prima():
    create_form = forms.MateriaPrimaForm()
    cargar_catalogos_materia_prima(create_form)

    id_materia = request.args.get("id")
    materia_db = (
        db.session.query(MateriaPrima)
        .filter(MateriaPrima.id_materia_prima == id_materia)
        .first()
    )

    if not materia_db:
        flash("Materia prima no encontrada.", "danger")
        return redirect(url_for("materia_prima.materia_prima_view"))

    if request.method == "GET":
        create_form.nombre.data = materia_db.nombre
        create_form.id_categoria_materia_prima.data = materia_db.id_categoria_materia_prima
        create_form.id_unidad_medida.data = materia_db.id_unidad_medida
        create_form.stock_actual.data = materia_db.stock_actual
        create_form.stock_minimo.data = materia_db.stock_minimo
        create_form.costo_unit_prom.data = materia_db.costo_unit_prom

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
    return redirect(url_for("materia_prima.materia_prima_view"))


@materia_prima.route("/private/materia-prima/movimiento", methods=["POST"])
@login_required(["ADMIN", "EMPLEADO"])
def movimiento_materia_prima():
    id_materia = request.form.get("id")
    tipo = (request.form.get("tipo") or "").strip().upper()
    motivo = (request.form.get("motivo") or "").strip()
    id_proveedor = request.form.get("id_proveedor")

    materia_db = (
        db.session.query(MateriaPrima)
        .filter(MateriaPrima.id_materia_prima == id_materia)
        .first()
    )

    if not materia_db:
        flash("Materia prima no encontrada.", "danger")
        return redirect(url_for("materia_prima.materia_prima_view"))

    try:
        cantidad = Decimal(request.form.get("cantidad", "0"))
    except (InvalidOperation, TypeError):
        flash("La cantidad ingresada no es válida.", "danger")
        return redirect(url_for("materia_prima.materia_prima_view"))

    if cantidad <= 0:
        flash("La cantidad debe ser mayor a 0.", "warning")
        return redirect(url_for("materia_prima.materia_prima_view"))

    stock_actual = Decimal(str(materia_db.stock_actual or 0))
    unidad_nombre = (
        materia_db.unidad_medida_rel.nombre
        if materia_db.unidad_medida_rel else ""
    )

    proveedor_db = None

    if tipo == "ENTRADA":
        if not id_proveedor:
            flash("Debes seleccionar un proveedor para registrar una entrada.", "warning")
            return redirect(url_for("materia_prima.materia_prima_view"))

        proveedor_db = (
            Proveedor.query
            .filter_by(id_proveedor=id_proveedor, activo=1)
            .first()
        )

        if not proveedor_db:
            flash("El proveedor seleccionado no es válido.", "danger")
            return redirect(url_for("materia_prima.materia_prima_view"))

        materia_db.stock_actual = stock_actual + cantidad

        movimiento = MovimientoMateriaPrima(
            id_materia_prima=materia_db.id_materia_prima,
            id_proveedor=proveedor_db.id_proveedor,
            tipo="ENTRADA",
            cantidad=cantidad,
            motivo=motivo,
        )
        db.session.add(movimiento)

        log_event(
            modulo="Inventario",
            accion="Entrada de materia prima",
            detalle=(
                f"Entrada de {cantidad} {unidad_nombre} a '{materia_db.nombre}' "
                f"desde proveedor '{proveedor_db.nombre}'. "
                f"Motivo: {motivo or 'Sin motivo'}"
            ),
            severidad="INFO",
        )

    elif tipo == "SALIDA":
        if stock_actual < cantidad:
            flash("No se permite stock negativo.", "danger")
            return redirect(url_for("materia_prima.materia_prima_view"))

        materia_db.stock_actual = stock_actual - cantidad

        movimiento = MovimientoMateriaPrima(
            id_materia_prima=materia_db.id_materia_prima,
            id_proveedor=None,
            tipo="SALIDA",
            cantidad=cantidad,
            motivo=motivo,
        )
        db.session.add(movimiento)

        log_event(
            modulo="Inventario",
            accion="Salida de materia prima",
            detalle=(
                f"Salida de {cantidad} {unidad_nombre} de '{materia_db.nombre}'. "
                f"Motivo: {motivo or 'Sin motivo'}"
            ),
            severidad="WARNING",
        )
    else:
        flash("Tipo de movimiento inválido.", "danger")
        return redirect(url_for("materia_prima.materia_prima_view"))

    db.session.add(materia_db)
    db.session.commit()

    flash("Movimiento registrado correctamente.", "success")
    return redirect(url_for("materia_prima.materia_prima_view"))