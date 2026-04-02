from flask import render_template, redirect, url_for, flash, make_response, request, g
from werkzeug.security import generate_password_hash, check_password_hash

import forms
from models import db, Usuario, Cliente
from utils.auth import issue_token, revoke_token, build_login_response, COOKIE_NAME
from utils.audit import log_event
from . import auth


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm()

    if g.user:
        return redirect(url_for("auth.post_login"))

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        u = Usuario.query.filter(
            db.func.lower(Usuario.email) == email,
            Usuario.activo == 1,
        ).first()

        if u and check_password_hash(u.password_hash, password):
            raw = issue_token("USUARIO", u.id_usuario)
            log_event(
                modulo="Autenticación",
                accion="Inicio de sesión",
                detalle=f"Usuario '{u.email}' inició sesión exitosamente",
                severidad="INFO",
                actor_tipo="USUARIO",
                actor_id=u.id_usuario,
                actor_nombre=u.nombre,
                actor_email=u.email,
            )
            resp = build_login_response(url_for("auth.post_login"), raw)
            flash(f"Bienvenido, {u.nombre}.", "success")
            return resp

        c = Cliente.query.filter(
            db.func.lower(Cliente.email) == email,
            Cliente.activo == 1,
        ).first()

        if c and c.password_hash and check_password_hash(c.password_hash, password):
            raw = issue_token("CLIENTE", c.id_cliente)
            log_event(
                modulo="Autenticación",
                accion="Inicio de sesión",
                detalle=f"Cliente '{c.email}' inició sesión exitosamente",
                severidad="INFO",
                actor_tipo="CLIENTE",
                actor_id=c.id_cliente,
                actor_nombre=c.nombre,
                actor_email=c.email,
            )
            resp = build_login_response(url_for("auth.post_login"), raw)
            flash(f"Bienvenido, {c.nombre}.", "success")
            return resp

        log_event(
            modulo="Autenticación",
            accion="Acceso denegado",
            detalle=f"Intento de inicio de sesión fallido para '{email}'",
            severidad="WARNING",
            actor_email=email,
        )
        flash("Credenciales inválidas.", "danger")

    return render_template("auth/login.html", form=form)


@auth.route("/registro", methods=["GET", "POST"])
def register():
    form = forms.RegisterClienteForm()

    if g.user:
        return redirect(url_for("auth.post_login"))

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        exists_cliente = Cliente.query.filter(db.func.lower(Cliente.email) == email).first()
        exists_usuario = Usuario.query.filter(db.func.lower(Usuario.email) == email).first()

        if exists_cliente or exists_usuario:
            flash("Ese correo ya está registrado.", "warning")
            return render_template("auth/register.html", form=form)

        cliente = Cliente(
            nombre=form.nombre.data.strip(),
            email=email,
            telefono=form.telefono.data or None,
            activo=1,
            password_hash=generate_password_hash(form.password.data),
        )
        db.session.add(cliente)
        db.session.commit()

        log_event(
            modulo="Usuarios",
            accion="Cliente registrado",
            detalle=f"Nuevo cliente '{email}' creado desde registro público",
            severidad="INFO",
            actor_tipo="CLIENTE",
            actor_id=cliente.id_cliente,
            actor_nombre=cliente.nombre,
            actor_email=cliente.email,
        )

        flash("Cuenta creada correctamente. Ahora inicia sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth.route("/post-login")
def post_login():
    if not g.user:
        return redirect(url_for("auth.login"))

    if g.role == "ADMIN":
        return redirect(url_for("tienda.admin_dashboard"))

    if g.role == "EMPLEADO":
        return redirect(url_for("tienda.vendedor_dashboard"))

    return redirect(url_for("tienda.cliente_dashboard"))


@auth.route("/logout")
def logout():
    raw = request.cookies.get(COOKIE_NAME)

    if g.user:
        log_event(
            modulo="Autenticación",
            accion="Cierre de sesión",
            detalle=f"Sesión cerrada por '{getattr(g.user, 'email', 'sin-email')}'",
            severidad="INFO",
        )

    revoke_token(raw)
    resp = make_response(redirect(url_for("tienda.home")))
    resp.delete_cookie(COOKIE_NAME)
    flash("Sesión cerrada.", "info")
    return resp