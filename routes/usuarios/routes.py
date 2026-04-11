from flask import render_template, request, redirect, url_for, flash, g
from werkzeug.security import generate_password_hash
import forms
from models import db, Usuario, Rol
from utils.auth import login_required
from utils.audit import log_event
from . import usuarios


def cargar_roles(form):
    roles = Rol.query.order_by(Rol.descripcion.asc()).all()
    form.rol.choices = [(r.id_rol, r.descripcion) for r in roles]


@usuarios.route("/private/admin/usuarios")
@login_required("ADMIN")
def listado_usuarios():
    create_form = forms.UsuarioForm()
    cargar_roles(create_form)

    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = Usuario.query.join(Rol)

    if search:
        like_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Usuario.nombre.ilike(like_term),
                Usuario.email.ilike(like_term),
                Usuario.telefono.ilike(like_term),
                Rol.descripcion.ilike(like_term),
                Rol.codigo.ilike(like_term),
            )
        )

    query = query.order_by(Usuario.nombre.asc())

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    usuarios_db = pagination.items

    total_usuarios = Usuario.query.count()
    usuarios_activos = Usuario.query.filter_by(activo=1).count()
    usuarios_inactivos = Usuario.query.filter_by(activo=0).count()
    roles = Rol.query.order_by(Rol.descripcion.asc()).all()

    return render_template(
        "private/usuarios/usuarios.html",
        form=create_form,
        usuarios_db=usuarios_db,
        pagination=pagination,
        total_usuarios=total_usuarios,
        usuarios_activos=usuarios_activos,
        usuarios_inactivos=usuarios_inactivos,
        roles=roles,
        search=search,
    )


@usuarios.route("/private/admin/usuarios/create", methods=["GET", "POST"])
@login_required("ADMIN")
def crear_usuario():
    create_form = forms.UsuarioForm()
    cargar_roles(create_form)

    if request.method == "POST" and create_form.validate():
        email = create_form.email.data.strip().lower()
        telefono = create_form.telefono.data.strip()

        existe = Usuario.query.filter(db.func.lower(Usuario.email) == email).first()
        if existe:
            flash("Ese correo ya está registrado.", "warning")
            return render_template("private/usuarios/usuarios_create.html", form=create_form)

        existe_telefono = Usuario.query.filter(Usuario.telefono == telefono).first()
        if existe_telefono:
            flash("Ese teléfono ya está registrado.", "warning")
            return render_template("private/usuarios/usuarios_create.html", form=create_form)

        if not create_form.password.data or not create_form.password.data.strip():
            flash("La contraseña es obligatoria.", "warning")
            return render_template("private/usuarios/usuarios_create.html", form=create_form)

        usuario = Usuario(
            id_rol=create_form.rol.data,
            nombre=create_form.nombre.data.strip(),
            email=email,
            telefono=telefono,
            password_hash=generate_password_hash(create_form.password.data.strip()),
            activo=create_form.activo.data,
        )
        db.session.add(usuario)
        db.session.commit()

        log_event(
            modulo="Usuarios",
            accion="Usuario creado",
            detalle=f"Usuario '{usuario.email}' creado con teléfono '{usuario.telefono}' y estado {'Activo' if usuario.activo == 1 else 'Inactivo'}",
            severidad="INFO",
        )
        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("usuarios.listado_usuarios"))

    return render_template("private/usuarios/usuarios_create.html", form=create_form)


@usuarios.route("/private/admin/usuarios/update", methods=["GET", "POST"])
@login_required("ADMIN")
def actualizar_usuario():
    create_form = forms.UsuarioForm()
    cargar_roles(create_form)
    id_usuario = request.args.get("id")

    usuario_db = Usuario.query.filter(Usuario.id_usuario == id_usuario).first()
    if not usuario_db:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("usuarios.listado_usuarios"))

    if request.method == "GET":
        create_form.nombre.data = usuario_db.nombre
        create_form.email.data = usuario_db.email
        create_form.telefono.data = usuario_db.telefono
        create_form.rol.data = usuario_db.id_rol
        create_form.activo.data = usuario_db.activo
        return render_template(
            "private/usuarios/usuarios_update.html",
            form=create_form,
            usuario_db=usuario_db,
        )

    if create_form.validate():
        email = create_form.email.data.strip().lower()
        telefono = create_form.telefono.data.strip()

        existe = Usuario.query.filter(
            db.func.lower(Usuario.email) == email,
            Usuario.id_usuario != usuario_db.id_usuario,
        ).first()
        if existe:
            flash("Ya existe otro usuario con ese correo.", "warning")
            return render_template(
                "private/usuarios/usuarios_update.html",
                form=create_form,
                usuario_db=usuario_db,
            )

        existe_telefono = Usuario.query.filter(
            Usuario.telefono == telefono,
            Usuario.id_usuario != usuario_db.id_usuario,
        ).first()
        if existe_telefono:
            flash("Ya existe otro usuario con ese teléfono.", "warning")
            return render_template(
                "private/usuarios/usuarios_update.html",
                form=create_form,
                usuario_db=usuario_db,
            )

        usuario_db.nombre = create_form.nombre.data.strip()
        usuario_db.email = email
        usuario_db.telefono = telefono
        usuario_db.id_rol = create_form.rol.data
        usuario_db.activo = create_form.activo.data

        if create_form.password.data and create_form.password.data.strip():
            usuario_db.password_hash = generate_password_hash(create_form.password.data.strip())

        db.session.add(usuario_db)
        db.session.commit()

        log_event(
            modulo="Usuarios",
            accion="Usuario actualizado",
            detalle=f"Usuario '{usuario_db.email}' actualizado. Teléfono: '{usuario_db.telefono}'. Estado: {'Activo' if usuario_db.activo == 1 else 'Inactivo'}",
            severidad="INFO",
        )
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("usuarios.listado_usuarios"))

    return render_template(
        "private/usuarios/usuarios_update.html",
        form=create_form,
        usuario_db=usuario_db,
    )


@usuarios.route("/private/admin/usuarios/delete", methods=["GET", "POST"])
@login_required("ADMIN")
def eliminar_usuario():
    create_form = forms.UsuarioForm()
    cargar_roles(create_form)
    id_usuario = request.args.get("id")

    usuario_db = Usuario.query.filter(Usuario.id_usuario == id_usuario).first()
    if not usuario_db:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("usuarios.listado_usuarios"))

    if not g.user or g.user.id_usuario == usuario_db.id_usuario:
        flash("No puedes desactivar tu propio usuario.", "warning")
        return redirect(url_for("usuarios.listado_usuarios"))

    if request.method == "GET":
        create_form.nombre.data = usuario_db.nombre
        create_form.email.data = usuario_db.email
        create_form.telefono.data = usuario_db.telefono
        create_form.rol.data = usuario_db.id_rol
        create_form.activo.data = usuario_db.activo
        return render_template(
            "private/usuarios/usuarios_delete.html",
            form=create_form,
            usuario_db=usuario_db,
        )

    usuario_db.activo = 0
    db.session.add(usuario_db)
    db.session.commit()

    log_event(
        modulo="Usuarios",
        accion="Usuario desactivado",
        detalle=f"Usuario '{usuario_db.email}' marcado como inactivo",
        severidad="WARNING",
    )
    flash("Usuario desactivado correctamente.", "info")
    return redirect(url_for("usuarios.listado_usuarios"))