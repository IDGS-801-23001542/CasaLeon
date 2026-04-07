from flask import render_template, redirect, url_for, flash, make_response, request, g
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError

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

    if request.method == "POST":
        print("LOGIN request.form =", dict(request.form))
        print("LOGIN form.errors =", form.errors)

        if not form.validate_on_submit():
            print("LOGIN validate_on_submit = False")
            print("LOGIN form.errors after validate =", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", "danger")
            return render_template("auth/login.html", form=form)

        email = (form.email.data or "").strip().lower()
        password = form.password.data or ""
        remember = bool(getattr(form, "remember", None) and form.remember.data)

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

            flash(f"Bienvenido, {u.nombre}.", "success")
            return build_login_response(url_for("auth.post_login"), raw, remember=remember)

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

            flash(f"Bienvenido, {c.nombre}.", "success")
            return build_login_response(url_for("auth.post_login"), raw, remember=remember)

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

    if request.method == "POST":
        print("REGISTER request.form =", dict(request.form))
        print("REGISTER confirm_password raw =", request.form.get("confirm_password"))
        print("REGISTER form.errors before validate =", form.errors)

        if not form.validate_on_submit():
            print("REGISTER validate_on_submit = False")
            print("REGISTER form.errors after validate =", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", "danger")
            return render_template("auth/register.html", form=form)

        email = (form.email.data or "").strip().lower()
        nombre = (form.nombre.data or "").strip()
        telefono = (form.telefono.data or "").strip() or None
        password = form.password.data or ""

        exists_cliente = Cliente.query.filter(db.func.lower(Cliente.email) == email).first()
        exists_usuario = Usuario.query.filter(db.func.lower(Usuario.email) == email).first()

        if exists_cliente or exists_usuario:
            flash("Ese correo ya está registrado.", "warning")
            return render_template("auth/register.html", form=form)

        try:
            cliente = Cliente(
                nombre=nombre,
                email=email,
                telefono=telefono,
                activo=1,
                password_hash=generate_password_hash(password),
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

        except SQLAlchemyError as e:
            db.session.rollback()
            print("REGISTER SQL ERROR =", e)
            flash("Ocurrió un error al crear la cuenta. Intenta nuevamente.", "danger")

        except Exception as e:
            db.session.rollback()
            print("REGISTER GENERAL ERROR =", e)
            flash("Ocurrió un error inesperado al crear la cuenta.", "danger")

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
    resp.delete_cookie(COOKIE_NAME, path="/")
    flash("Sesión cerrada.", "info")
    return resp