from flask import render_template, request, redirect, url_for, flash, g
from werkzeug.security import generate_password_hash

import forms
from models import db, Usuario, Rol
from utils.auth import login_required
from . import usuarios


def cargar_roles(form):
    roles = Rol.query.order_by(Rol.descripcion.asc()).all()
    form.rol.choices = [(r.id_rol, r.descripcion) for r in roles]


@usuarios.route("/private/admin/usuarios")
@login_required("ADMIN")
def listado_usuarios():
    create_form = forms.UsuarioForm()
    cargar_roles(create_form)

    usuarios_db = Usuario.query.join(Rol).order_by(Usuario.nombre.asc()).all()

    return render_template(
        "private/usuarios/usuarios.html",
        form=create_form,
        usuarios_db=usuarios_db,
        roles=Rol.query.order_by(Rol.descripcion.asc()).all()
    )


@usuarios.route("/private/admin/usuarios/create", methods=["GET", "POST"])
@login_required("ADMIN")
def crear_usuario():
    create_form = forms.UsuarioForm()
    cargar_roles(create_form)

    if request.method == "POST":
        if create_form.validate():
            email = create_form.email.data.strip().lower()

            existe = Usuario.query.filter(
                db.func.lower(Usuario.email) == email
            ).first()

            if existe:
                flash("Ese correo ya está registrado.", "warning")
                return render_template(
                    "private/usuarios/usuarios_create.html",
                    form=create_form
                )

            if not create_form.password.data or not create_form.password.data.strip():
                flash("La contraseña es obligatoria.", "warning")
                return render_template(
                    "private/usuarios/usuarios_create.html",
                    form=create_form
                )

            usuario = Usuario(
                id_rol=create_form.rol.data,
                nombre=create_form.nombre.data.strip(),
                email=email,
                password_hash=generate_password_hash(create_form.password.data),
                activo=1,
            )

            db.session.add(usuario)
            db.session.commit()

            flash("Usuario creado correctamente.", "success")
            return redirect(url_for("usuarios.listado_usuarios"))

    return render_template(
        "private/usuarios/usuarios_create.html",
        form=create_form
    )


@usuarios.route("/private/admin/usuarios/update", methods=["GET", "POST"])
@login_required("ADMIN")
def actualizar_usuario():
    create_form = forms.UsuarioForm()
    cargar_roles(create_form)

    if request.method == "GET":
        id_usuario = request.args.get("id")
        usuario_db = db.session.query(Usuario).filter(
            Usuario.id_usuario == id_usuario
        ).first()

        if not usuario_db:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for("usuarios.listado_usuarios"))

        create_form.nombre.data = usuario_db.nombre
        create_form.email.data = usuario_db.email
        create_form.rol.data = usuario_db.id_rol
        create_form.activo.data = usuario_db.activo

        return render_template(
            "private/usuarios/usuarios_update.html",
            form=create_form,
            usuario_db=usuario_db
        )

    if request.method == "POST":
        id_usuario = request.args.get("id")
        usuario_db = db.session.query(Usuario).filter(
            Usuario.id_usuario == id_usuario
        ).first()

        if not usuario_db:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for("usuarios.listado_usuarios"))

        if create_form.validate():
            email = create_form.email.data.strip().lower()

            existe = Usuario.query.filter(
                db.func.lower(Usuario.email) == email,
                Usuario.id_usuario != usuario_db.id_usuario
            ).first()

            if existe:
                flash("Ya existe otro usuario con ese correo.", "warning")
                return render_template(
                    "private/usuarios/usuarios_update.html",
                    form=create_form,
                    usuario_db=usuario_db
                )

            usuario_db.nombre = create_form.nombre.data.strip()
            usuario_db.email = email
            usuario_db.id_rol = create_form.rol.data
            usuario_db.activo = 1

            if create_form.password.data and create_form.password.data.strip():
                if not g.user or g.user.id_usuario != usuario_db.id_usuario:
                    flash("Solo puedes cambiar tu propia contraseña.", "warning")
                    return render_template(
                        "private/usuarios/usuarios_update.html",
                        form=create_form,
                        usuario_db=usuario_db
                    )

                usuario_db.password_hash = generate_password_hash(create_form.password.data)

            db.session.add(usuario_db)
            db.session.commit()

            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for("usuarios.listado_usuarios"))

        return render_template(
            "private/usuarios/usuarios_update.html",
            form=create_form,
            usuario_db=usuario_db
        )


@usuarios.route("/private/admin/usuarios/delete", methods=["GET", "POST"])
@login_required("ADMIN")
def eliminar_usuario():
    create_form = forms.UsuarioForm()
    cargar_roles(create_form)

    if request.method == "GET":
        id_usuario = request.args.get("id")
        usuario_db = db.session.query(Usuario).filter(
            Usuario.id_usuario == id_usuario
        ).first()

        if not usuario_db:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for("usuarios.listado_usuarios"))

        create_form.nombre.data = usuario_db.nombre
        create_form.email.data = usuario_db.email
        create_form.rol.data = usuario_db.id_rol
        create_form.activo.data = usuario_db.activo

        return render_template(
            "private/usuarios/usuarios_delete.html",
            form=create_form,
            usuario_db=usuario_db
        )

    if request.method == "POST":
        id_usuario = request.args.get("id")
        usuario_db = db.session.query(Usuario).filter(
            Usuario.id_usuario == id_usuario
        ).first()

        if not usuario_db:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for("usuarios.listado_usuarios"))

        usuario_db.activo = 0
        db.session.add(usuario_db)
        db.session.commit()

        flash("Usuario desactivado correctamente.", "info")
        return redirect(url_for("usuarios.listado_usuarios"))