import os
import subprocess
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, redirect, url_for, request
from flask import flash, make_response, g

from werkzeug.security import generate_password_hash, check_password_hash

from config import DevelopmentConfig
import forms
from models import db, Rol, Usuario, Cliente, AuthToken


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

db.init_app(app)
TOKEN_EXPIRES_HOURS = int(app.config.get("TOKEN_EXPIRES_HOURS", 8))


# =========================
# Tailwind build (SIN 2da terminal)
# =========================
def build_tailwind_once():
    """
    Compila Tailwind a static/css/output.css al arrancar Flask.
    No watch. No segunda terminal.
    """
    cmd = [
        "npx", "@tailwindcss/cli",
        "-i", "./static/src/input.css",
        "-o", "./static/css/output.css",
        "--minify"
    ]
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Tailwind build falló:")
            print(result.stdout)
            print(result.stderr)
        else:
            print("✅ Tailwind build OK -> static/css/output.css")
    except Exception as e:
        print("❌ No pude ejecutar Tailwind build:", e)


# =========================
# MODELOS (mapeo exacto a tu BD)
# =========================


# =========================
# HELPERS TOKENS
# =========================
COOKIE_NAME = "cl_token"


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _issue_token(subject_type: str, subject_id: int) -> str:
    raw = secrets.token_urlsafe(48)
    token_hash = _hash_token(raw)

    expires = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRES_HOURS)

    t = AuthToken(
        subject_type=subject_type,
        subject_id=subject_id,
        token_hash=token_hash,
        expires_at=expires,
        revoked=0,
        user_agent=(request.headers.get("User-Agent", "")[:255]),
        ip_addr=(request.remote_addr),
    )
    db.session.add(t)
    db.session.commit()
    return raw


def _revoke_token(raw: str | None):
    if not raw:
        return
    token_hash = _hash_token(raw)
    t = AuthToken.query.filter_by(token_hash=token_hash, revoked=0).first()
    if t:
        t.revoked = 1
        db.session.commit()


def _get_identity():
    raw = request.cookies.get(COOKIE_NAME)
    if not raw:
        return None

    token_hash = _hash_token(raw)
    t = AuthToken.query.filter_by(token_hash=token_hash, revoked=0).first()
    if not t:
        return None

    if t.expires_at < datetime.utcnow():
        t.revoked = 1
        db.session.commit()
        return None

    return {"raw": raw, "type": t.subject_type, "id": t.subject_id}


@app.before_request
def load_identity():
    g.user = None
    g.role = None
    g.identity = None

    ident = _get_identity()
    if not ident:
        return

    g.identity = ident

    if ident["type"] == "USUARIO":
        u = Usuario.query.filter_by(id_usuario=ident["id"], activo=1).first()
        if u:
            g.user = u
            g.role = u.rol.codigo if u.rol else None  # ADMIN / EMPLEADO
    else:
        c = Cliente.query.filter_by(id_cliente=ident["id"], activo=1).first()
        if c:
            g.user = c
            g.role = "CLIENTE"


def login_required(roles=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not g.user:
                return redirect(url_for("login"))

            if roles:
                allowed = roles if isinstance(roles, (list, tuple, set)) else [roles]
                if g.role not in allowed:
                    flash("No tienes permisos para entrar aquí.", "danger")
                    return redirect(url_for("post_login"))

            return fn(*args, **kwargs)
        return wrapper
    return decorator


# =========================
# PÚBLICO
# =========================
@app.route("/")
def home():
    # Página pública (empresa + productos preview). Por ahora placeholder bonito.
    return render_template("tienda/home.html", public=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    create_form = forms.LoginForm(request.form)
    if g.user:
        return redirect(url_for("post_login"))

    

    if create_form.validate_on_submit():
        email = create_form.email.data.strip().lower()
        password = create_form.password.data

        # 1) STAFF
        u = Usuario.query.filter(db.func.lower(Usuario.email) == email, Usuario.activo == 1).first()
        if u and check_password_hash(u.password_hash, password):
            raw = _issue_token("USUARIO", u.id_usuario)
            resp = make_response(redirect(url_for("post_login")))
            resp.set_cookie(
                COOKIE_NAME, raw,
                httponly=True, samesite="Lax",
                secure=bool(app.config.get("SESSION_COOKIE_SECURE", False)),
                max_age=TOKEN_EXPIRES_HOURS * 3600,
            )
            flash(f"Bienvenido, {u.nombre}.", "success")
            return resp

        # 2) CLIENTE
        c = Cliente.query.filter(db.func.lower(Cliente.email) == email, Cliente.activo == 1).first()
        if c and c.password_hash and check_password_hash(c.password_hash, password):
            raw = _issue_token("CLIENTE", c.id_cliente)
            resp = make_response(redirect(url_for("post_login")))
            resp.set_cookie(
                COOKIE_NAME, raw,
                httponly=True, samesite="Lax",
                secure=bool(app.config.get("SESSION_COOKIE_SECURE", False)),
                max_age=TOKEN_EXPIRES_HOURS * 3600,
            )
            flash(f"Bienvenido, {c.nombre}.", "success")
            return resp

        flash("Credenciales inválidas.", "danger")

    return render_template("auth/login.html", form=create_form)


@app.route("/post-login")
def post_login():
    if not g.user:
        return redirect(url_for("login"))

    if g.role == "ADMIN":
        return redirect(url_for("admin_dashboard"))

    if g.role == "EMPLEADO":
        return redirect(url_for("vendedor_dashboard"))

    return redirect(url_for("tienda"))


@app.route("/logout")
def logout():
    raw = request.cookies.get(COOKIE_NAME)
    _revoke_token(raw)
    resp = make_response(redirect(url_for("home")))
    resp.delete_cookie(COOKIE_NAME)
    flash("Sesión cerrada.", "info")
    return resp


@app.route("/registro", methods=["GET", "POST"])
def register():
    create_form = forms.RegisterClienteForm(request.form)
    if g.user:
        return redirect(url_for("post_login"))

    if create_form.validate_on_submit():
        email = create_form.email.data.strip().lower()
        exists = Cliente.query.filter(db.func.lower(Cliente.email) == email).first()
        if exists:
            flash("Ese email ya está registrado.", "warning")
            return render_template("auth/register.html", form=create_form)

        c = Cliente(
            nombre=create_form.nombre.data.strip(),
            email=email,
            telefono=(create_form.telefono.data.strip() if create_form.telefono.data else None),
            activo=1,
            password_hash=generate_password_hash(create_form.password.data),
            creado_en=datetime.utcnow(),
        )
        db.session.add(c)
        db.session.commit()
        flash("Cuenta creada. Ahora inicia sesión.", "success")
        return redirect(url_for("login"))

    return render_template("auth/register.html", form=create_form)


# =========================
# CLIENTE
# =========================
@app.route("/tienda")
@login_required("CLIENTE")
def tienda():
    return render_template("tienda/cliente_dashboard.html")


# =========================
# STAFF
# =========================
@app.route("/app/admin/dashboard")
@login_required("ADMIN")
def admin_dashboard():
    return render_template("app/admin_dashboard.html")


@app.route("/app/vendedor/dashboard")
@login_required("EMPLEADO")
def vendedor_dashboard():
    return render_template("app/vendedor_dashboard.html")


@app.route("/app/admin/usuarios/nuevo", methods=["GET", "POST"])
@login_required("ADMIN")
def crear_usuario_staff():
    create_form = forms.CreateStaffForm(request.form)

    if create_form.validate_on_submit():
        email = create_form.email.data.strip().lower()

        exists = Usuario.query.filter(db.func.lower(Usuario.email) == email).first()
        if exists:
            flash("Ese email ya existe en usuarios.", "warning")
            return render_template("app/admin_create_staff.html", form=create_form)

        rol = Rol.query.filter_by(codigo=create_form.rol.data).first()
        if not rol:
            flash("Rol inválido.", "danger")
            return render_template("app/admin_create_staff.html", form=create_form)

        u = Usuario(
            id_rol=rol.id_rol,
            nombre=create_form.nombre.data.strip(),
            email=email,
            password_hash=generate_password_hash(create_form.password.data),
            activo=1,
            creado_en=datetime.utcnow(),
        )
        db.session.add(u)
        db.session.commit()
        flash("Usuario staff creado ✅", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("app/admin_create_staff.html", form=create_form)


if __name__ == "__main__":
    build_tailwind_once()
    with app.app_context():
        db.create_all()
    app.run()