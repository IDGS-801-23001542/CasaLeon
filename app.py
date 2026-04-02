import hashlib
import secrets
from datetime import datetime, timedelta
from decimal import Decimal
from functools import wraps

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    make_response,
    g,
    session,
    abort,
)
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

from config import DevelopmentConfig
import forms
from models import (
    db,
    Rol,
    Usuario,
    Cliente,
    AuthToken,
    Producto,
    CategoriaProducto,
    Pedido,
    PedidoDetalle
)

from routes.usuarios.routes import usuarios
from routes.proveedores.routes import proveedores
from routes.productos.routes import productos


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

app.register_blueprint(usuarios)
app.register_blueprint(proveedores)
app.register_blueprint(productos)

db.init_app(app)
migrate = Migrate(app, db)

TOKEN_EXPIRES_HOURS = int(app.config.get("TOKEN_EXPIRES_HOURS", 8))
COOKIE_NAME = "cl_token"


# =========================
# HELPERS TOKENS
# =========================
def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _issue_token(subject_type: str, subject_id: int) -> str:
    raw = secrets.token_urlsafe(48)
    token_hash = _hash_token(raw)
    expires = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRES_HOURS)

    token = AuthToken(
        subject_type=subject_type,
        subject_id=subject_id,
        token_hash=token_hash,
        expires_at=expires,
        revoked=0,
        user_agent=(request.headers.get("User-Agent", "")[:255]),
        ip_addr=request.remote_addr,
    )
    db.session.add(token)
    db.session.commit()
    return raw


def _revoke_token(raw: str | None):
    if not raw:
        return

    token_hash = _hash_token(raw)
    token = AuthToken.query.filter_by(token_hash=token_hash, revoked=0).first()
    if token:
        token.revoked = 1
        db.session.commit()


def _get_identity():
    raw = request.cookies.get(COOKIE_NAME)
    if not raw:
        return None

    token_hash = _hash_token(raw)
    token = AuthToken.query.filter_by(token_hash=token_hash, revoked=0).first()
    if not token:
        return None

    if token.expires_at < datetime.utcnow():
        token.revoked = 1
        db.session.commit()
        return None

    return {"raw": raw, "type": token.subject_type, "id": token.subject_id}


# =========================
# HELPERS CARRITO
# =========================
def _cart():
    return session.setdefault("cart", {})


def _save_cart():
    session.modified = True


def _cart_items():
    items = list(session.get("cart", {}).values())
    total = sum(Decimal(str(item["precio"])) * item["cantidad"] for item in items)
    return items, total


def _producto_to_cart_item(producto):
    return {
        "id_producto": producto.id_producto,
        "nombre": producto.nombre,
        "precio": float(producto.precio_venta),
        "imagen": producto.imagen,
        "stock": int(float(producto.stock_actual)),
        "cantidad": 1,
    }


def _next_folio():
    base = datetime.utcnow().strftime("PED%Y%m%d")
    count = Pedido.query.count() + 1
    return f"{base}-{count:04d}"


def _query_productos_publicos(busqueda="", categoria_id="", limit=None):
    query = db.session.query(
        Producto.id_producto,
        Producto.nombre,
        Producto.descripcion,
        Producto.precio_venta,
        Producto.stock_actual,
        Producto.imagen,
        CategoriaProducto.nombre.label("categoria"),
        CategoriaProducto.id_categoria_producto.label("categoria_id")
    ).join(
        CategoriaProducto,
        Producto.id_categoria_producto == CategoriaProducto.id_categoria_producto
    ).filter(
        Producto.activo == 1
    )

    if busqueda:
        query = query.filter(Producto.nombre.ilike(f"%{busqueda}%"))

    if str(categoria_id).isdigit():
        query = query.filter(Producto.id_categoria_producto == int(categoria_id))

    query = query.order_by(Producto.nombre.asc())

    if limit:
        query = query.limit(limit)

    return query.all()


# =========================
# CONTEXTO GLOBAL
# =========================
@app.before_request
def load_identity():
    g.user = None
    g.role = None
    g.identity = None
    g.cart_count = sum(item["cantidad"] for item in session.get("cart", {}).values()) if session.get("cart") else 0

    ident = _get_identity()
    if not ident:
        return

    g.identity = ident

    if ident["type"] == "USUARIO":
        u = Usuario.query.filter_by(id_usuario=ident["id"], activo=1).first()
        if u:
            g.user = u
            g.role = u.rol.codigo if u.rol else None
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
                flash("Primero inicia sesión.", "warning")
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
    productos_destacados = _query_productos_publicos(limit=6)
    categorias = CategoriaProducto.query.order_by(CategoriaProducto.nombre.asc()).all()

    return render_template(
        "tienda/home.html",
        productos=productos_destacados,
        categorias=categorias
    )


@app.route("/productos")
def productos_publico():
    busqueda = request.args.get("q", "").strip()
    categoria_id = request.args.get("categoria", "").strip()

    productos = _query_productos_publicos(
        busqueda=busqueda,
        categoria_id=categoria_id
    )
    categorias = CategoriaProducto.query.order_by(CategoriaProducto.nombre.asc()).all()

    return render_template(
        "tienda/productos.html",
        productos=productos,
        categorias=categorias,
        busqueda=busqueda,
        categoria_id=categoria_id
    )


@app.route("/nosotros")
def nosotros():
    return render_template("tienda/nosotros.html")


@app.route("/contacto")
def contacto():
    return render_template("tienda/contacto.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm()

    if g.user:
        return redirect(url_for("post_login"))

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        # STAFF
        u = Usuario.query.filter(
            db.func.lower(Usuario.email) == email,
            Usuario.activo == 1
        ).first()

        if u and check_password_hash(u.password_hash, password):
            raw = _issue_token("USUARIO", u.id_usuario)
            resp = make_response(redirect(url_for("post_login")))
            resp.set_cookie(
                COOKIE_NAME,
                raw,
                httponly=True,
                samesite="Lax",
                secure=bool(app.config.get("SESSION_COOKIE_SECURE", False)),
                max_age=TOKEN_EXPIRES_HOURS * 3600,
            )
            flash(f"Bienvenido, {u.nombre}.", "success")
            return resp

        # CLIENTE
        c = Cliente.query.filter(
            db.func.lower(Cliente.email) == email,
            Cliente.activo == 1
        ).first()

        if c and c.password_hash and check_password_hash(c.password_hash, password):
            raw = _issue_token("CLIENTE", c.id_cliente)
            resp = make_response(redirect(url_for("post_login")))
            resp.set_cookie(
                COOKIE_NAME,
                raw,
                httponly=True,
                samesite="Lax",
                secure=bool(app.config.get("SESSION_COOKIE_SECURE", False)),
                max_age=TOKEN_EXPIRES_HOURS * 3600,
            )
            flash(f"Bienvenido, {c.nombre}.", "success")
            return resp

        flash("Credenciales inválidas.", "danger")

    return render_template("auth/login.html", form=form)


@app.route("/registro", methods=["GET", "POST"])
def register():
    form = forms.RegisterClienteForm()

    if g.user:
        return redirect(url_for("post_login"))

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
            creado_en=datetime.utcnow(),
        )
        db.session.add(cliente)
        db.session.commit()

        flash("Cuenta creada correctamente. Ahora inicia sesión.", "success")
        return redirect(url_for("login"))

    return render_template("auth/register.html", form=form)


@app.route("/post-login")
def post_login():
    if not g.user:
        return redirect(url_for("login"))

    if g.role == "ADMIN":
        return redirect(url_for("admin_dashboard"))

    if g.role == "EMPLEADO":
        return redirect(url_for("vendedor_dashboard"))

    return redirect(url_for("cliente_dashboard"))


@app.route("/logout")
def logout():
    raw = request.cookies.get(COOKIE_NAME)
    _revoke_token(raw)
    resp = make_response(redirect(url_for("home")))
    resp.delete_cookie(COOKIE_NAME)
    flash("Sesión cerrada.", "info")
    return resp


# =========================
# CARRITO
# =========================
@app.route("/carrito")
def carrito():
    items, total = _cart_items()
    return render_template("tienda/carrito.html", items=items, total=total)


@app.route("/carrito/agregar/<int:id_producto>", methods=["POST"])
def agregar_carrito(id_producto):
    producto = Producto.query.filter_by(id_producto=id_producto, activo=1).first_or_404()

    max_stock = int(float(producto.stock_actual))
    if max_stock <= 0:
        flash("Este producto no tiene stock disponible.", "warning")
        return redirect(request.referrer or url_for("productos_publico"))

    cart = _cart()
    key = str(id_producto)

    if key in cart:
        cart[key]["cantidad"] += 1
    else:
        cart[key] = _producto_to_cart_item(producto)

    if cart[key]["cantidad"] > max_stock:
        cart[key]["cantidad"] = max_stock
        flash("Se ajustó la cantidad al stock disponible.", "warning")
    else:
        flash(f"{producto.nombre} agregado al carrito.", "success")

    _save_cart()
    return redirect(request.referrer or url_for("productos_publico"))


@app.route("/carrito/actualizar/<int:id_producto>", methods=["POST"])
def actualizar_carrito(id_producto):
    cart = _cart()
    key = str(id_producto)

    if key not in cart:
        return redirect(url_for("carrito"))

    try:
        cantidad = int(request.form.get("cantidad", 1))
    except (ValueError, TypeError):
        cantidad = 1

    if cantidad <= 0:
        cart.pop(key, None)
        flash("Producto eliminado del carrito.", "info")
    else:
        producto = Producto.query.get_or_404(id_producto)
        max_stock = int(float(producto.stock_actual))
        cart[key]["cantidad"] = min(cantidad, max_stock)
        flash("Cantidad actualizada.", "success")

    _save_cart()
    return redirect(url_for("carrito"))


@app.route("/carrito/eliminar/<int:id_producto>", methods=["POST"])
def eliminar_carrito(id_producto):
    cart = _cart()
    cart.pop(str(id_producto), None)
    _save_cart()
    flash("Producto eliminado del carrito.", "info")
    return redirect(url_for("carrito"))


# =========================
# CLIENTE
# =========================
@app.route("/cliente")
@login_required("CLIENTE")
def cliente_dashboard():
    pedidos = Pedido.query.filter_by(id_cliente=g.user.id_cliente).order_by(Pedido.creado_en.desc()).limit(3).all()
    items, total_carrito = _cart_items()
    return render_template(
        "tienda/cliente_dashboard.html",
        pedidos=pedidos,
        cart_items=items,
        total_carrito=total_carrito
    )


@app.route("/tienda")
def tienda():
    return redirect(url_for("productos_publico"))


@app.route("/checkout", methods=["GET", "POST"])
@login_required("CLIENTE")
def checkout():
    items, total = _cart_items()

    if not items:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for("carrito"))

    form = forms.CheckoutForm()

    if request.method == "GET":
        form.nombre.data = g.user.nombre
        form.telefono.data = g.user.telefono
        form.calle.data = g.user.calle
        form.numero.data = g.user.numero
        form.colonia.data = g.user.colonia
        form.ciudad.data = g.user.ciudad
        form.estado.data = g.user.estado
        form.pais.data = g.user.pais or "México"
        form.cp.data = g.user.cp

    if form.validate_on_submit():
        pedido = Pedido(
            id_cliente=g.user.id_cliente,
            folio=_next_folio(),
            estado="Pendiente",
            total=total,
            nombre_envio=form.nombre.data.strip(),
            telefono_envio=form.telefono.data.strip() if form.telefono.data else None,
            calle_envio=form.calle.data.strip(),
            numero_envio=form.numero.data.strip(),
            colonia_envio=form.colonia.data.strip(),
            ciudad_envio=form.ciudad.data.strip(),
            estado_envio=form.estado.data.strip(),
            pais_envio=form.pais.data.strip(),
            cp_envio=form.cp.data.strip(),
            notas=form.notas.data.strip() if form.notas.data else None,
            creado_en=datetime.utcnow(),
        )
        db.session.add(pedido)
        db.session.flush()

        for item in items:
            subtotal = Decimal(str(item["precio"])) * item["cantidad"]
            detalle = PedidoDetalle(
                id_pedido=pedido.id_pedido,
                id_producto=item["id_producto"],
                producto_nombre=item["nombre"],
                precio_unitario=Decimal(str(item["precio"])),
                cantidad=item["cantidad"],
                subtotal=subtotal
            )
            db.session.add(detalle)

        g.user.nombre = form.nombre.data.strip()
        g.user.telefono = form.telefono.data.strip() if form.telefono.data else None
        g.user.calle = form.calle.data.strip()
        g.user.numero = form.numero.data.strip()
        g.user.colonia = form.colonia.data.strip()
        g.user.ciudad = form.ciudad.data.strip()
        g.user.estado = form.estado.data.strip()
        g.user.pais = form.pais.data.strip()
        g.user.cp = form.cp.data.strip()

        db.session.commit()
        session["cart"] = {}
        flash("Compra simulada realizada correctamente. Tu pedido fue registrado.", "success")
        return redirect(url_for("pedido_detalle", id_pedido=pedido.id_pedido))

    return render_template("tienda/checkout.html", form=form, items=items, total=total)


@app.route("/mis-pedidos")
@login_required("CLIENTE")
def mis_pedidos():
    pedidos = Pedido.query.filter_by(id_cliente=g.user.id_cliente).order_by(Pedido.creado_en.desc()).all()
    return render_template("tienda/mis_pedidos.html", pedidos=pedidos)


@app.route("/pedido/<int:id_pedido>")
@login_required("CLIENTE")
def pedido_detalle(id_pedido):
    pedido = Pedido.query.filter_by(id_pedido=id_pedido, id_cliente=g.user.id_cliente).first()
    if not pedido:
        abort(404)
    return render_template("tienda/pedido_detalle.html", pedido=pedido)


@app.route("/mi-cuenta", methods=["GET", "POST"])
@login_required("CLIENTE")
def mi_cuenta():
    form = forms.UpdateClienteForm(obj=g.user)

    if form.validate_on_submit():
        g.user.nombre = form.nombre.data.strip()
        g.user.telefono = form.telefono.data.strip() if form.telefono.data else None
        g.user.calle = form.calle.data.strip() if form.calle.data else None
        g.user.numero = form.numero.data.strip() if form.numero.data else None
        g.user.colonia = form.colonia.data.strip() if form.colonia.data else None
        g.user.ciudad = form.ciudad.data.strip() if form.ciudad.data else None
        g.user.estado = form.estado.data.strip() if form.estado.data else None
        g.user.pais = form.pais.data.strip() if form.pais.data else None
        g.user.cp = form.cp.data.strip() if form.cp.data else None

        db.session.commit()
        flash("Tu perfil fue actualizado.", "success")
        return redirect(url_for("mi_cuenta"))

    return render_template("tienda/mi_cuenta.html", form=form)


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
    form = forms.CreateStaffForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        exists = Usuario.query.filter(db.func.lower(Usuario.email) == email).first()
        if exists:
            flash("Ese email ya existe en usuarios.", "warning")
            return render_template("app/admin_create_staff.html", form=form)

        rol = Rol.query.filter_by(codigo=form.rol.data).first()
        if not rol:
            flash("Rol inválido.", "danger")
            return render_template("app/admin_create_staff.html", form=form)

        u = Usuario(
            id_rol=rol.id_rol,
            nombre=form.nombre.data.strip(),
            email=email,
            password_hash=generate_password_hash(form.password.data),
            activo=1,
            creado_en=datetime.utcnow(),
        )
        db.session.add(u)
        db.session.commit()
        flash("Usuario staff creado ✅", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("app/admin_create_staff.html", form=form)


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)