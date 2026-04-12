from . import productos
from flask import render_template, request, redirect, url_for, flash
import cloudinary.uploader

import forms
from models import db, Producto, CategoriaProducto, Receta
from utils.auth import login_required
from utils.audit import log_event


ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_image(filename):
    return (
        filename
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def upload_product_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_image(file_storage.filename):
        return "INVALID_EXTENSION"

    result = cloudinary.uploader.upload(
        file_storage,
        folder="assets/productos",
        resource_type="image",
    )

    return result.get("secure_url")


def generar_sku_producto(id_producto):
    return f"PROD{id_producto:04d}"


def cargar_categorias(form):
    categorias = CategoriaProducto.query.order_by(CategoriaProducto.nombre.asc()).all()
    form.id_categoria_producto.choices = [
        (c.id_categoria_producto, c.nombre) for c in categorias
    ]


def cargar_recetas_disponibles(form, producto_id_actual=None):
    total_recetas_activas = Receta.query.filter(Receta.activo == 1).count()

    query = Receta.query.filter(Receta.activo == 1)

    if producto_id_actual:
        query = query.filter(
            db.or_(
                Receta.id_producto.is_(None), Receta.id_producto == producto_id_actual
            )
        )
    else:
        query = query.filter(Receta.id_producto.is_(None))

    recetas = query.order_by(Receta.nombre.asc()).all()
    form.id_receta.choices = [(r.id_receta, r.nombre) for r in recetas]

    if total_recetas_activas == 0:
        mensaje = "No hay recetas activas. Debes crear y activar una receta antes de registrar productos."
    elif len(recetas) == 0:
        mensaje = "Todas las recetas activas ya están asignadas a productos. Debes liberar una receta o crear una nueva."
    else:
        mensaje = None

    return len(recetas) == 0, mensaje


@productos.route("/private/productos", methods=["GET"])
@login_required(["ADMIN", "EMPLEADO"])
def listado_productos():
    create_form = forms.ProductoForm()
    cargar_categorias(create_form)
    cargar_recetas_disponibles(create_form)

    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = Producto.query.join(CategoriaProducto)

    if search:
        like_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Producto.nombre.ilike(like_term),
                Producto.sku.ilike(like_term),
                Producto.descripcion.ilike(like_term),
                CategoriaProducto.nombre.ilike(like_term),
            )
        )

    query = query.order_by(Producto.nombre.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    productos_db = pagination.items

    total_productos = Producto.query.count()
    productos_activos = Producto.query.filter_by(activo=1).count()
    productos_inactivos = Producto.query.filter_by(activo=0).count()

    valor_inventario = sum(
        float(producto.stock_actual or 0) * float(producto.costo_unit_prom or 0)
        for producto in Producto.query.all()
    )

    categorias_db = CategoriaProducto.query.order_by(CategoriaProducto.nombre.asc()).all()
    total_categorias_producto = len(categorias_db)

    return render_template(
        "private/productos/productos.html",
        form=create_form,
        productos_db=productos_db,
        pagination=pagination,
        total_productos=total_productos,
        productos_activos=productos_activos,
        productos_inactivos=productos_inactivos,
        valor_inventario=f"{valor_inventario:,.2f}",
        search=search,
        categorias_db=categorias_db,
        total_categorias_producto=total_categorias_producto,
    )


@productos.route("/private/productos/create", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def crear_producto():
    create_form = forms.ProductoForm()
    cargar_categorias(create_form)
    sin_recetas, mensaje_recetas = cargar_recetas_disponibles(create_form)

    if request.method == "POST":
        if sin_recetas:
            flash(mensaje_recetas, "warning")
            return render_template(
                "private/productos/productos_create.html",
                form=create_form,
                sin_recetas=sin_recetas,
                mensaje_recetas=mensaje_recetas,
            )

        if create_form.validate():
            nombre = create_form.nombre.data.strip()

            existe_nombre = Producto.query.filter(
                db.func.lower(Producto.nombre) == nombre.lower()
            ).first()
            if existe_nombre:
                flash("Ya existe un producto con ese nombre.", "warning")
                return render_template(
                    "private/productos/productos_create.html",
                    form=create_form,
                    sin_recetas=sin_recetas,
                    mensaje_recetas=mensaje_recetas,
                )

            receta_db = Receta.query.filter(
                Receta.id_receta == create_form.id_receta.data, Receta.activo == 1
            ).first()

            if not receta_db:
                flash("La receta seleccionada no es válida.", "warning")
                return render_template(
                    "private/productos/productos_create.html",
                    form=create_form,
                    sin_recetas=sin_recetas,
                    mensaje_recetas=mensaje_recetas,
                )

            if receta_db.id_producto is not None:
                flash(
                    "La receta seleccionada ya está asignada a otro producto.",
                    "warning",
                )
                return render_template(
                    "private/productos/productos_create.html",
                    form=create_form,
                    sin_recetas=sin_recetas,
                    mensaje_recetas=mensaje_recetas,
                )

            image_file = request.files.get("imagen")
            image_url = upload_product_image(image_file)

            if image_url == "INVALID_EXTENSION":
                flash("La imagen debe ser png, jpg, jpeg o webp.", "warning")
                return render_template(
                    "private/productos/productos_create.html",
                    form=create_form,
                    sin_recetas=sin_recetas,
                    mensaje_recetas=mensaje_recetas,
                )

            producto = Producto(
                id_categoria_producto=create_form.id_categoria_producto.data,
                sku=None,
                nombre=nombre,
                descripcion=create_form.descripcion.data.strip()
                if create_form.descripcion.data
                else None,
                imagen=image_url,
                precio_venta=create_form.precio_venta.data,
                stock_actual=0,
                costo_unit_prom=receta_db.costo_estimado or 0,
                activo=1,
            )

            db.session.add(producto)
            db.session.flush()

            producto.sku = generar_sku_producto(producto.id_producto)
            receta_db.id_producto = producto.id_producto

            db.session.add(producto)
            db.session.add(receta_db)
            db.session.commit()

            log_event(
                modulo="Inventario",
                accion="Producto creado",
                detalle=f"Producto '{producto.nombre}' creado con SKU '{producto.sku}', stock inicial 0 y vinculado a receta '{receta_db.nombre}'",
                severidad="INFO",
            )
            flash("Producto creado correctamente.", "success")
            return redirect(url_for("productos.listado_productos"))

    return render_template(
        "private/productos/productos_create.html",
        form=create_form,
        sin_recetas=sin_recetas,
        mensaje_recetas=mensaje_recetas,
    )


@productos.route("/private/productos/update", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def actualizar_producto():
    create_form = forms.ProductoForm()

    id_producto = request.args.get("id")
    producto_db = (
        db.session.query(Producto).filter(Producto.id_producto == id_producto).first()
    )

    if not producto_db:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("productos.listado_productos"))

    receta_actual = Receta.query.filter_by(id_producto=producto_db.id_producto).first()

    cargar_categorias(create_form)
    cargar_recetas_disponibles(create_form, producto_id_actual=producto_db.id_producto)

    if request.method == "GET":
        create_form.id_categoria_producto.data = producto_db.id_categoria_producto
        create_form.nombre.data = producto_db.nombre
        create_form.descripcion.data = producto_db.descripcion
        create_form.precio_venta.data = producto_db.precio_venta
        create_form.id_receta.data = receta_actual.id_receta if receta_actual else None

        return render_template(
            "private/productos/productos_update.html",
            form=create_form,
            producto_db=producto_db,
            receta_actual=receta_actual,
        )

    if create_form.validate():
        nombre = create_form.nombre.data.strip()

        existe_nombre = Producto.query.filter(
            db.func.lower(Producto.nombre) == nombre.lower(),
            Producto.id_producto != producto_db.id_producto,
        ).first()
        if existe_nombre:
            flash("Ya existe otro producto con ese nombre.", "warning")
            return render_template(
                "private/productos/productos_update.html",
                form=create_form,
                producto_db=producto_db,
                receta_actual=receta_actual,
            )

        receta_nueva = Receta.query.filter(
            Receta.id_receta == create_form.id_receta.data, Receta.activo == 1
        ).first()

        if not receta_nueva:
            flash("La receta seleccionada no es válida.", "warning")
            return render_template(
                "private/productos/productos_update.html",
                form=create_form,
                producto_db=producto_db,
                receta_actual=receta_actual,
            )

        if (
            receta_nueva.id_producto is not None
            and receta_nueva.id_producto != producto_db.id_producto
        ):
            flash("La receta seleccionada ya está asignada a otro producto.", "warning")
            return render_template(
                "private/productos/productos_update.html",
                form=create_form,
                producto_db=producto_db,
                receta_actual=receta_actual,
            )

        if receta_actual and receta_actual.id_receta != receta_nueva.id_receta:
            receta_actual.id_producto = None
            db.session.add(receta_actual)

        receta_nueva.id_producto = producto_db.id_producto

        image_file = request.files.get("imagen")
        new_image_url = upload_product_image(image_file)

        if new_image_url == "INVALID_EXTENSION":
            flash("La imagen debe ser png, jpg, jpeg o webp.", "warning")
            return render_template(
                "private/productos/productos_update.html",
                form=create_form,
                producto_db=producto_db,
                receta_actual=receta_actual,
            )

        if new_image_url:
            producto_db.imagen = new_image_url

        producto_db.id_categoria_producto = create_form.id_categoria_producto.data
        producto_db.nombre = nombre
        producto_db.descripcion = (
            create_form.descripcion.data.strip()
            if create_form.descripcion.data
            else None
        )
        producto_db.precio_venta = create_form.precio_venta.data
        producto_db.costo_unit_prom = (
            receta_nueva.costo_estimado or producto_db.costo_unit_prom
        )

        db.session.add(receta_nueva)
        db.session.add(producto_db)
        db.session.commit()

        log_event(
            modulo="Inventario",
            accion="Producto actualizado",
            detalle=f"Producto '{producto_db.nombre}' actualizado sin alterar stock ni SKU",
            severidad="INFO",
        )
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("productos.listado_productos"))

    return render_template(
        "private/productos/productos_update.html",
        form=create_form,
        producto_db=producto_db,
        receta_actual=receta_actual,
    )


@productos.route("/private/productos/delete", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def eliminar_producto():
    create_form = forms.ProductoForm()

    id_producto = request.args.get("id")
    producto_db = (
        db.session.query(Producto).filter(Producto.id_producto == id_producto).first()
    )

    if not producto_db:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("productos.listado_productos"))

    receta_actual = Receta.query.filter_by(id_producto=producto_db.id_producto).first()

    cargar_categorias(create_form)
    cargar_recetas_disponibles(create_form, producto_id_actual=producto_db.id_producto)

    if request.method == "GET":
        create_form.id_categoria_producto.data = producto_db.id_categoria_producto
        create_form.nombre.data = producto_db.nombre
        create_form.descripcion.data = producto_db.descripcion
        create_form.precio_venta.data = producto_db.precio_venta
        create_form.id_receta.data = receta_actual.id_receta if receta_actual else None

        return render_template(
            "private/productos/productos_delete.html",
            form=create_form,
            producto_db=producto_db,
            receta_actual=receta_actual,
        )

    producto_db.activo = 0
    db.session.add(producto_db)
    db.session.commit()

    log_event(
        modulo="Inventario",
        accion="Producto desactivado",
        detalle=f"Producto '{producto_db.nombre}' marcado como inactivo",
        severidad="WARNING",
    )
    flash("Producto desactivado correctamente.", "info")
    return redirect(url_for("productos.listado_productos"))


# =========================
# CATEGORÍAS DE PRODUCTO
# =========================

@productos.route("/private/productos/categorias", methods=["GET"])
@login_required(["ADMIN", "EMPLEADO"])
def listado_categorias_producto():
    search = request.args.get("search", "").strip()

    query = CategoriaProducto.query

    if search:
        like_term = f"%{search}%"
        query = query.filter(CategoriaProducto.nombre.ilike(like_term))

    categorias_db = query.order_by(CategoriaProducto.nombre.asc()).all()

    return render_template(
        "private/productos/categorias_producto.html",
        categorias_db=categorias_db,
        total_categorias_producto=len(categorias_db),
        search=search,
    )


@productos.route("/private/productos/categorias/create", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def crear_categoria_producto():
    create_form = forms.CategoriaProductoForm()

    if request.method == "POST" and create_form.validate():
        nombre = create_form.nombre.data.strip()

        existe = CategoriaProducto.query.filter(
            db.func.lower(CategoriaProducto.nombre) == nombre.lower()
        ).first()

        if existe:
            flash("Ya existe una categoría con ese nombre.", "warning")
            return render_template(
                "private/productos/categorias_producto_create.html",
                form=create_form,
            )

        categoria = CategoriaProducto(nombre=nombre)
        db.session.add(categoria)
        db.session.commit()

        log_event(
            modulo="Inventario",
            accion="Categoría de producto creada",
            detalle=f"Categoría '{categoria.nombre}' creada",
            severidad="INFO",
        )
        flash("Categoría creada correctamente.", "success")
        return redirect(url_for("productos.listado_categorias_producto"))

    return render_template(
        "private/productos/categorias_producto_create.html",
        form=create_form,
    )


@productos.route("/private/productos/categorias/update", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def actualizar_categoria_producto():
    create_form = forms.CategoriaProductoForm()

    id_categoria_producto = request.args.get("id")
    categoria_db = CategoriaProducto.query.filter(
        CategoriaProducto.id_categoria_producto == id_categoria_producto
    ).first()

    if not categoria_db:
        flash("Categoría no encontrada.", "danger")
        return redirect(url_for("productos.listado_categorias_producto"))

    if request.method == "GET":
        create_form.nombre.data = categoria_db.nombre
        return render_template(
            "private/productos/categorias_producto_update.html",
            form=create_form,
            categoria_db=categoria_db,
        )

    if create_form.validate():
        nombre = create_form.nombre.data.strip()

        existe = CategoriaProducto.query.filter(
            db.func.lower(CategoriaProducto.nombre) == nombre.lower(),
            CategoriaProducto.id_categoria_producto != categoria_db.id_categoria_producto,
        ).first()

        if existe:
            flash("Ya existe otra categoría con ese nombre.", "warning")
            return render_template(
                "private/productos/categorias_producto_update.html",
                form=create_form,
                categoria_db=categoria_db,
            )

        categoria_db.nombre = nombre
        db.session.add(categoria_db)
        db.session.commit()

        log_event(
            modulo="Inventario",
            accion="Categoría de producto actualizada",
            detalle=f"Categoría actualizada a '{categoria_db.nombre}'",
            severidad="INFO",
        )
        flash("Categoría actualizada correctamente.", "success")
        return redirect(url_for("productos.listado_categorias_producto"))

    return render_template(
        "private/productos/categorias_producto_update.html",
        form=create_form,
        categoria_db=categoria_db,
    )


@productos.route("/private/productos/categorias/delete", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def eliminar_categoria_producto():
    id_categoria_producto = request.args.get("id")
    categoria_db = CategoriaProducto.query.filter(
        CategoriaProducto.id_categoria_producto == id_categoria_producto
    ).first()

    if not categoria_db:
        flash("Categoría no encontrada.", "danger")
        return redirect(url_for("productos.listado_categorias_producto"))

    productos_asociados = Producto.query.filter(
        Producto.id_categoria_producto == categoria_db.id_categoria_producto
    ).count()

    if request.method == "GET":
        return render_template(
            "private/productos/categorias_producto_delete.html",
            categoria_db=categoria_db,
            productos_asociados=productos_asociados,
        )

    if productos_asociados > 0:
        flash(
            "No se puede eliminar la categoría porque tiene productos asociados.",
            "warning",
        )
        return redirect(url_for("productos.listado_categorias_producto"))

    nombre_categoria = categoria_db.nombre
    db.session.delete(categoria_db)
    db.session.commit()

    log_event(
        modulo="Inventario",
        accion="Categoría de producto eliminada",
        detalle=f"Categoría '{nombre_categoria}' eliminada",
        severidad="WARNING",
    )
    flash("Categoría eliminada correctamente.", "info")
    return redirect(url_for("productos.listado_categorias_producto"))