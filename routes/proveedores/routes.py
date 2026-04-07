from . import proveedores
from flask import render_template, request, redirect, url_for, flash
import forms
from models import db, Proveedor
from utils.auth import login_required
from utils.audit import log_event


@proveedores.route("/private/admin/proveedores")
@login_required("ADMIN")
def listado_proveedores():
    create_form = forms.ProveedorForm()
    search = request.args.get("search", "").strip()

    query = Proveedor.query
    if search:
        like_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Proveedor.nombre.ilike(like_term),
                Proveedor.rfc.ilike(like_term),
                Proveedor.email.ilike(like_term),
                Proveedor.telefono.ilike(like_term),
                Proveedor.ciudad.ilike(like_term),
                Proveedor.estado.ilike(like_term),
                Proveedor.pais.ilike(like_term),
            )
        )

    proveedores_db = query.order_by(Proveedor.nombre.asc()).all()
    total_proveedores = Proveedor.query.count()
    proveedores_activos = Proveedor.query.filter_by(activo=1).count()
    proveedores_inactivos = Proveedor.query.filter_by(activo=0).count()

    return render_template(
        "private/proveedores/proveedores.html",
        form=create_form,
        proveedores_db=proveedores_db,
        total_proveedores=total_proveedores,
        proveedores_activos=proveedores_activos,
        proveedores_inactivos=proveedores_inactivos,
        search=search,
    )


@proveedores.route("/private/admin/proveedores/create", methods=["GET", "POST"])
@login_required("ADMIN")
def crear_proveedor():
    create_form = forms.ProveedorForm()

    if request.method == "POST" and create_form.validate():
        rfc = create_form.rfc.data.strip().upper() if create_form.rfc.data else None
        email = create_form.email.data.strip().lower() if create_form.email.data else None

        if rfc:
            existe_rfc = Proveedor.query.filter(db.func.upper(Proveedor.rfc) == rfc).first()
            if existe_rfc:
                flash("Ya existe un proveedor con ese RFC.", "warning")
                return render_template("private/proveedores/proveedores_create.html", form=create_form)

        proveedor = Proveedor(
            nombre=create_form.nombre.data.strip(),
            rfc=rfc,
            email=email,
            telefono=create_form.telefono.data.strip() if create_form.telefono.data else None,
            calle=create_form.calle.data.strip() if create_form.calle.data else None,
            numero=create_form.numero.data.strip() if create_form.numero.data else None,
            colonia=create_form.colonia.data.strip() if create_form.colonia.data else None,
            ciudad=create_form.ciudad.data.strip() if create_form.ciudad.data else None,
            estado=create_form.estado.data.strip() if create_form.estado.data else None,
            pais=create_form.pais.data.strip() if create_form.pais.data else None,
            cp=create_form.cp.data.strip() if create_form.cp.data else None,
            activo=create_form.activo.data,
        )
        db.session.add(proveedor)
        db.session.commit()

        log_event(
            modulo="Proveedores",
            accion="Proveedor creado",
            detalle=f"Proveedor '{proveedor.nombre}' creado con estado {'Activo' if proveedor.activo == 1 else 'Inactivo'}",
            severidad="INFO",
        )
        flash("Proveedor creado correctamente.", "success")
        return redirect(url_for("proveedores.listado_proveedores"))

    return render_template("private/proveedores/proveedores_create.html", form=create_form)


@proveedores.route("/private/admin/proveedores/update", methods=["GET", "POST"])
@login_required("ADMIN")
def actualizar_proveedor():
    create_form = forms.ProveedorForm()
    id_proveedor = request.args.get("id")

    proveedor_db = Proveedor.query.filter(Proveedor.id_proveedor == id_proveedor).first()
    if not proveedor_db:
        flash("Proveedor no encontrado.", "danger")
        return redirect(url_for("proveedores.listado_proveedores"))

    if request.method == "GET":
        create_form.nombre.data = proveedor_db.nombre
        create_form.rfc.data = proveedor_db.rfc
        create_form.email.data = proveedor_db.email
        create_form.telefono.data = proveedor_db.telefono
        create_form.calle.data = proveedor_db.calle
        create_form.numero.data = proveedor_db.numero
        create_form.colonia.data = proveedor_db.colonia
        create_form.ciudad.data = proveedor_db.ciudad
        create_form.estado.data = proveedor_db.estado
        create_form.pais.data = proveedor_db.pais
        create_form.cp.data = proveedor_db.cp
        create_form.activo.data = proveedor_db.activo

        return render_template(
            "private/proveedores/proveedores_update.html",
            form=create_form,
            proveedor_db=proveedor_db,
        )

    if create_form.validate():
        rfc = create_form.rfc.data.strip().upper() if create_form.rfc.data else None
        email = create_form.email.data.strip().lower() if create_form.email.data else None

        if rfc:
            existe_rfc = Proveedor.query.filter(
                db.func.upper(Proveedor.rfc) == rfc,
                Proveedor.id_proveedor != proveedor_db.id_proveedor,
            ).first()
            if existe_rfc:
                flash("Ya existe otro proveedor con ese RFC.", "warning")
                return render_template(
                    "private/proveedores/proveedores_update.html",
                    form=create_form,
                    proveedor_db=proveedor_db,
                )

        proveedor_db.nombre = create_form.nombre.data.strip()
        proveedor_db.rfc = rfc
        proveedor_db.email = email
        proveedor_db.telefono = create_form.telefono.data.strip() if create_form.telefono.data else None
        proveedor_db.calle = create_form.calle.data.strip() if create_form.calle.data else None
        proveedor_db.numero = create_form.numero.data.strip() if create_form.numero.data else None
        proveedor_db.colonia = create_form.colonia.data.strip() if create_form.colonia.data else None
        proveedor_db.ciudad = create_form.ciudad.data.strip() if create_form.ciudad.data else None
        proveedor_db.estado = create_form.estado.data.strip() if create_form.estado.data else None
        proveedor_db.pais = create_form.pais.data.strip() if create_form.pais.data else None
        proveedor_db.cp = create_form.cp.data.strip() if create_form.cp.data else None
        proveedor_db.activo = create_form.activo.data

        db.session.add(proveedor_db)
        db.session.commit()

        log_event(
            modulo="Proveedores",
            accion="Proveedor actualizado",
            detalle=f"Proveedor '{proveedor_db.nombre}' actualizado. Estado: {'Activo' if proveedor_db.activo == 1 else 'Inactivo'}",
            severidad="INFO",
        )
        flash("Proveedor actualizado correctamente.", "success")
        return redirect(url_for("proveedores.listado_proveedores"))

    return render_template(
        "private/proveedores/proveedores_update.html",
        form=create_form,
        proveedor_db=proveedor_db,
    )


@proveedores.route("/private/admin/proveedores/delete", methods=["GET", "POST"])
@login_required("ADMIN")
def eliminar_proveedor():
    create_form = forms.ProveedorForm()
    id_proveedor = request.args.get("id")

    proveedor_db = Proveedor.query.filter(Proveedor.id_proveedor == id_proveedor).first()
    if not proveedor_db:
        flash("Proveedor no encontrado.", "danger")
        return redirect(url_for("proveedores.listado_proveedores"))

    if request.method == "GET":
        create_form.nombre.data = proveedor_db.nombre
        create_form.rfc.data = proveedor_db.rfc
        create_form.email.data = proveedor_db.email
        create_form.telefono.data = proveedor_db.telefono
        create_form.calle.data = proveedor_db.calle
        create_form.numero.data = proveedor_db.numero
        create_form.colonia.data = proveedor_db.colonia
        create_form.ciudad.data = proveedor_db.ciudad
        create_form.estado.data = proveedor_db.estado
        create_form.pais.data = proveedor_db.pais
        create_form.cp.data = proveedor_db.cp
        create_form.activo.data = proveedor_db.activo

        return render_template(
            "private/proveedores/proveedores_delete.html",
            form=create_form,
            proveedor_db=proveedor_db,
        )

    proveedor_db.activo = 0
    db.session.add(proveedor_db)
    db.session.commit()

    log_event(
        modulo="Proveedores",
        accion="Proveedor desactivado",
        detalle=f"Proveedor '{proveedor_db.nombre}' marcado como inactivo",
        severidad="WARNING",
    )
    flash("Proveedor desactivado correctamente.", "info")
    return redirect(url_for("proveedores.listado_proveedores"))