from datetime import datetime, timedelta

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    make_response,
    request,
    g,
    session,
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError

import forms
from models import db, Usuario, Cliente
from utils.auth import issue_token, revoke_token, build_login_response, COOKIE_NAME
from utils.audit import log_event
from utils.two_factor import (
    user_requires_2fa,
    generate_totp_secret,
    build_totp_uri,
    build_qr_base64,
    verify_totp_code,
)
from utils.email_security import (
    send_code_email,
    generate_email_code,
    confirm_email_verification_token,
)
from . import auth


OTP_MINUTES = 10


def _otp_expiration_iso():
    return (datetime.utcnow() + timedelta(minutes=OTP_MINUTES)).isoformat()


def _otp_is_expired(expires_at: str) -> bool:
    try:
        return datetime.utcnow() > datetime.fromisoformat(expires_at)
    except Exception:
        return True


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm()

    if g.user:
        return redirect(url_for("auth.post_login"))

    if request.method == "POST":
        if not form.validate_on_submit():
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", "danger")
            return render_template("auth/login.html", form=form)

        email = (form.email.data or "").strip().lower()
        password = form.password.data or ""
        remember = bool(getattr(form, "remember", None) and form.remember.data)

        # STAFF
        u = Usuario.query.filter(
            db.func.lower(Usuario.email) == email,
            Usuario.activo == 1,
        ).first()

        if u and check_password_hash(u.password_hash, password):
            requires_2fa = user_requires_2fa(u)

            if requires_2fa:
                session["pre_2fa_user_id"] = u.id_usuario
                session["pre_2fa_remember"] = remember

                if not u.two_factor_enabled or not u.two_factor_secret:
                    return redirect(url_for("auth.setup_2fa"))

                return redirect(url_for("auth.verify_2fa"))

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
            return build_login_response(
                url_for("auth.post_login"),
                raw,
                remember=remember,
            )

        # CLIENTE
        c = Cliente.query.filter(
            db.func.lower(Cliente.email) == email,
            Cliente.activo == 1,
        ).first()

        if c and c.password_hash and check_password_hash(c.password_hash, password):
            if not c.email_verificado:
                flash("Tu cuenta aún no está verificada.", "warning")
                return render_template("auth/login.html", form=form)

            code = generate_email_code()

            session["pending_client_login"] = {
                "id_cliente": c.id_cliente,
                "email": c.email,
                "nombre": c.nombre,
                "remember": remember,
                "code": code,
                "expires_at": _otp_expiration_iso(),
            }
            session.pop("pending_client_register", None)

            try:
                send_code_email(c.email, c.nombre, code, purpose="login")
            except Exception as e:
                print("CLIENT LOGIN CODE MAIL ERROR =", repr(e))
                flash("No se pudo enviar el código de acceso al correo.", "danger")
                return render_template("auth/login.html", form=form)

            flash("Te enviamos un código de verificación a tu correo.", "info")
            return redirect(url_for("auth.verify_otp"))

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
        if not form.validate_on_submit():
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", "danger")
            return render_template("auth/register.html", form=form)

        email = (form.email.data or "").strip().lower()
        nombre = (form.nombre.data or "").strip()
        telefono = (form.telefono.data or "").strip() or None
        password = form.password.data or ""

        exists_cliente = Cliente.query.filter(
            db.func.lower(Cliente.email) == email
        ).first()
        exists_usuario = Usuario.query.filter(
            db.func.lower(Usuario.email) == email
        ).first()

        if exists_cliente or exists_usuario:
            flash("Ese correo ya está registrado.", "warning")
            return render_template("auth/register.html", form=form)

        code = generate_email_code()

        session["pending_client_register"] = {
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
            "password_hash": generate_password_hash(password),
            "code": code,
            "expires_at": _otp_expiration_iso(),
        }
        session.pop("pending_client_login", None)

        try:
            send_code_email(email, nombre, code, purpose="register")
        except Exception as e:
            print("REGISTER CODE MAIL ERROR =", repr(e))
            flash("No se pudo enviar el código de verificación al correo.", "danger")
            return render_template("auth/register.html", form=form)

        flash("Te enviamos un código de verificación a tu correo.", "info")
        return redirect(url_for("auth.verify_otp"))

    return render_template("auth/register.html", form=form)


@auth.route("/verificar-otp", methods=["GET", "POST"])
def verify_otp():
    register_data = session.get("pending_client_register")
    login_data = session.get("pending_client_login")

    if not register_data and not login_data:
        flash("No hay ninguna verificación pendiente.", "warning")
        return redirect(url_for("auth.login"))

    form = forms.TwoFactorCodeForm()

    if register_data:
        destination = register_data.get("email")
        title = "Verifica tu registro"
        subtitle = "Ingresa el código de 6 dígitos que enviamos a tu correo para activar tu cuenta."
    else:
        destination = login_data.get("email")
        title = "Verifica tu acceso"
        subtitle = "Ingresa el código de 6 dígitos que enviamos a tu correo para completar el inicio de sesión."

    if form.validate_on_submit():
        code = (form.code.data or "").strip()

        # VERIFICACIÓN DE REGISTRO
        if register_data:
            if _otp_is_expired(register_data.get("expires_at", "")):
                session.pop("pending_client_register", None)
                flash("El código expiró. Regístrate nuevamente o solicita reenvío.", "warning")
                return redirect(url_for("auth.register"))

            if code != register_data.get("code"):
                flash("Código incorrecto.", "danger")
                return render_template(
                    "auth/verify_otp.html",
                    form=form,
                    destination=destination,
                    title=title,
                    subtitle=subtitle,
                )

            email = register_data.get("email", "").strip().lower()

            exists_cliente = Cliente.query.filter(
                db.func.lower(Cliente.email) == email
            ).first()
            exists_usuario = Usuario.query.filter(
                db.func.lower(Usuario.email) == email
            ).first()

            if exists_cliente or exists_usuario:
                session.pop("pending_client_register", None)
                flash("Ese correo ya está registrado.", "warning")
                return redirect(url_for("auth.register"))

            try:
                cliente = Cliente(
                    nombre=register_data.get("nombre"),
                    email=email,
                    telefono=register_data.get("telefono"),
                    activo=1,
                    email_verificado=1,
                    password_hash=register_data.get("password_hash"),
                )

                db.session.add(cliente)
                db.session.commit()

                log_event(
                    modulo="Usuarios",
                    accion="Cliente registrado",
                    detalle=f"Nuevo cliente '{email}' verificado por código",
                    severidad="INFO",
                    actor_tipo="CLIENTE",
                    actor_id=cliente.id_cliente,
                    actor_nombre=cliente.nombre,
                    actor_email=cliente.email,
                )

                session.pop("pending_client_register", None)

                raw = issue_token("CLIENTE", cliente.id_cliente)

                log_event(
                    modulo="Autenticación",
                    accion="Inicio de sesión después de registro",
                    detalle=f"Cliente '{cliente.email}' completó registro e inició sesión automáticamente",
                    severidad="INFO",
                    actor_tipo="CLIENTE",
                    actor_id=cliente.id_cliente,
                    actor_nombre=cliente.nombre,
                    actor_email=cliente.email,
                )

                flash("Cuenta creada y verificada correctamente. Bienvenido a Casa León.", "success")
                return build_login_response(
                    url_for("auth.post_login"),
                    raw,
                    remember=False,
                )

            except SQLAlchemyError as e:
                db.session.rollback()
                print("VERIFY REGISTER SQL ERROR =", e)
                flash("Ocurrió un error al activar la cuenta.", "danger")
                return render_template(
                    "auth/verify_otp.html",
                    form=form,
                    destination=destination,
                    title=title,
                    subtitle=subtitle,
                )

        # VERIFICACIÓN DE LOGIN
        if login_data:
            if _otp_is_expired(login_data.get("expires_at", "")):
                session.pop("pending_client_login", None)
                flash("El código expiró. Inicia sesión de nuevo.", "warning")
                return redirect(url_for("auth.login"))

            if code != login_data.get("code"):
                flash("Código incorrecto.", "danger")
                return render_template(
                    "auth/verify_otp.html",
                    form=form,
                    destination=destination,
                    title=title,
                    subtitle=subtitle,
                )

            cliente = Cliente.query.filter_by(
                id_cliente=login_data.get("id_cliente"),
                activo=1,
            ).first()

            if not cliente:
                session.pop("pending_client_login", None)
                flash("No se encontró la cuenta asociada.", "danger")
                return redirect(url_for("auth.login"))

            raw = issue_token("CLIENTE", cliente.id_cliente)
            remember = bool(login_data.get("remember"))

            session.pop("pending_client_login", None)

            log_event(
                modulo="Autenticación",
                accion="Inicio de sesión con código",
                detalle=f"Cliente '{cliente.email}' inició sesión con verificación por correo",
                severidad="INFO",
                actor_tipo="CLIENTE",
                actor_id=cliente.id_cliente,
                actor_nombre=cliente.nombre,
                actor_email=cliente.email,
            )

            flash(f"Bienvenido, {cliente.nombre}.", "success")
            return build_login_response(
                url_for("auth.post_login"),
                raw,
                remember=remember,
            )

    return render_template(
        "auth/verify_otp.html",
        form=form,
        destination=destination,
        title=title,
        subtitle=subtitle,
    )


@auth.route("/reenviar-otp", methods=["POST"])
def resend_otp():
    register_data = session.get("pending_client_register")
    login_data = session.get("pending_client_login")

    if not register_data and not login_data:
        flash("No hay ninguna verificación pendiente.", "warning")
        return redirect(url_for("auth.login"))

    if register_data:
        code = generate_email_code()
        register_data["code"] = code
        register_data["expires_at"] = _otp_expiration_iso()
        session["pending_client_register"] = register_data

        try:
            send_code_email(
                register_data["email"],
                register_data["nombre"],
                code,
                purpose="register",
            )
            flash("Te reenviamos el código de verificación.", "info")
        except Exception as e:
            print("RESEND REGISTER CODE ERROR =", repr(e))
            flash("No se pudo reenviar el código.", "danger")

        return redirect(url_for("auth.verify_otp"))

    if login_data:
        code = generate_email_code()
        login_data["code"] = code
        login_data["expires_at"] = _otp_expiration_iso()
        session["pending_client_login"] = login_data

        try:
            send_code_email(
                login_data["email"],
                login_data["nombre"],
                code,
                purpose="login",
            )
            flash("Te reenviamos el código de acceso.", "info")
        except Exception as e:
            print("RESEND LOGIN CODE ERROR =", repr(e))
            flash("No se pudo reenviar el código.", "danger")

        return redirect(url_for("auth.verify_otp"))

    flash("No hay ninguna verificación pendiente.", "warning")
    return redirect(url_for("auth.login"))


@auth.route("/verificar-correo/<token>")
def verify_email(token):
    email = confirm_email_verification_token(token)

    if not email:
        flash("El enlace de verificación es inválido o expiró.", "danger")
        return redirect(url_for("auth.login"))

    cliente = Cliente.query.filter(
        db.func.lower(Cliente.email) == email.lower()
    ).first()

    if not cliente:
        flash("No se encontró la cuenta asociada a este enlace.", "danger")
        return redirect(url_for("auth.register"))

    if cliente.email_verificado:
        flash("Tu correo ya había sido verificado.", "info")
        return redirect(url_for("auth.login"))

    cliente.email_verificado = 1
    db.session.commit()

    log_event(
        modulo="Autenticación",
        accion="Correo verificado",
        detalle=f"Cliente '{cliente.email}' verificó su correo correctamente",
        severidad="INFO",
        actor_tipo="CLIENTE",
        actor_id=cliente.id_cliente,
        actor_nombre=cliente.nombre,
        actor_email=cliente.email,
    )

    flash("Correo verificado correctamente. Ahora ya puedes iniciar sesión.", "success")
    return redirect(url_for("auth.login"))


@auth.route("/2fa/setup", methods=["GET", "POST"])
def setup_2fa():
    user_id = session.get("pre_2fa_user_id")
    if not user_id:
        flash("Tu sesión de verificación expiró. Inicia sesión de nuevo.", "warning")
        return redirect(url_for("auth.login"))

    u = Usuario.query.filter_by(id_usuario=user_id, activo=1).first()
    if not u:
        flash("Usuario no válido.", "danger")
        return redirect(url_for("auth.login"))

    if not user_requires_2fa(u):
        flash("Este usuario no tiene habilitada la configuración de 2FA.", "danger")
        return redirect(url_for("auth.login"))

    form = forms.TwoFactorCodeForm()

    secret = session.get("pending_2fa_secret")
    if not secret:
        secret = generate_totp_secret()
        session["pending_2fa_secret"] = secret

    uri = build_totp_uri(u.email, secret)
    qr_image = build_qr_base64(uri)

    if form.validate_on_submit():
        if not verify_totp_code(secret, form.code.data):
            flash("El código no es válido. Intenta de nuevo.", "danger")
            return render_template(
                "auth/two_factor_setup.html",
                form=form,
                qr_image=qr_image,
                secret=secret,
                user=u,
            )

        u.two_factor_secret = secret
        u.two_factor_enabled = 1
        db.session.commit()

        session.pop("pending_2fa_secret", None)

        raw = issue_token("USUARIO", u.id_usuario)
        remember = bool(session.get("pre_2fa_remember"))

        session.pop("pre_2fa_user_id", None)
        session.pop("pre_2fa_remember", None)

        log_event(
            modulo="Autenticación",
            accion="2FA configurado",
            detalle=f"Usuario '{u.email}' configuró autenticación en dos pasos",
            severidad="INFO",
            actor_tipo="USUARIO",
            actor_id=u.id_usuario,
            actor_nombre=u.nombre,
            actor_email=u.email,
        )

        flash("Verificación en dos pasos configurada correctamente.", "success")
        return build_login_response(
            url_for("auth.post_login"),
            raw,
            remember=remember,
        )

    return render_template(
        "auth/two_factor_setup.html",
        form=form,
        qr_image=qr_image,
        secret=secret,
        user=u,
    )


@auth.route("/2fa/verificar", methods=["GET", "POST"])
def verify_2fa():
    user_id = session.get("pre_2fa_user_id")
    if not user_id:
        flash("Tu sesión de verificación expiró. Inicia sesión de nuevo.", "warning")
        return redirect(url_for("auth.login"))

    u = Usuario.query.filter_by(id_usuario=user_id, activo=1).first()
    if not u or not u.two_factor_enabled or not u.two_factor_secret:
        flash("No se pudo validar la verificación en dos pasos.", "danger")
        return redirect(url_for("auth.login"))

    form = forms.TwoFactorCodeForm()

    if form.validate_on_submit():
        if not verify_totp_code(u.two_factor_secret, form.code.data):
            flash("Código incorrecto. Intenta de nuevo.", "danger")
            return render_template("auth/two_factor_verify.html", form=form, user=u)

        raw = issue_token("USUARIO", u.id_usuario)
        remember = bool(session.get("pre_2fa_remember"))

        session.pop("pre_2fa_user_id", None)
        session.pop("pre_2fa_remember", None)
        session.pop("pending_2fa_secret", None)

        log_event(
            modulo="Autenticación",
            accion="Inicio de sesión con 2FA",
            detalle=f"Usuario '{u.email}' completó autenticación en dos pasos",
            severidad="INFO",
            actor_tipo="USUARIO",
            actor_id=u.id_usuario,
            actor_nombre=u.nombre,
            actor_email=u.email,
        )

        flash(f"Bienvenido, {u.nombre}.", "success")
        return build_login_response(
            url_for("auth.post_login"),
            raw,
            remember=remember,
        )

    return render_template("auth/two_factor_verify.html", form=form, user=u)


@auth.route("/post-login")
def post_login():
    if not g.user:
        return redirect(url_for("auth.login"))

    if g.role == "ADMIN":
        return redirect(url_for("tienda.admin_dashboard"))

    if g.role == "EMPLEADO":
        return redirect(url_for("tienda.vendedor_dashboard"))

    return redirect(url_for("tienda.productos_publico"))


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
    session.pop("pre_2fa_user_id", None)
    session.pop("pre_2fa_remember", None)
    session.pop("pending_2fa_secret", None)
    session.pop("pending_client_register", None)
    session.pop("pending_client_login", None)

    resp = make_response(redirect(url_for("tienda.home")))
    resp.delete_cookie(COOKIE_NAME, path="/")
    flash("Sesión cerrada.", "info")
    return resp