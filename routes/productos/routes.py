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


def cargar_categorias(form):
    categorias = CategoriaProducto.query.order_by(CategoriaProducto.nombre.asc()).all()
    form.id_categoria_producto.choices = [
        (c.id_categoria_producto, c.nombre) for c in categorias
    ]


def cargar_recetas_disponibles(form, producto_id_actual=None):
    query = Receta.query.filter_by(activo=1)

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
    )


@productos.route("/private/productos/create", methods=["GET", "POST"])
@login_required(["ADMIN", "EMPLEADO"])
def crear_producto():
    create_form = forms.ProductoForm()
    cargar_categorias(create_form)
    cargar_recetas_disponibles(create_form)

    if request.method == "POST":
        if create_form.validate():
            sku = create_form.sku.data.strip().upper() if create_form.sku.data else None
            nombre = create_form.nombre.data.strip()

            existe_nombre = Producto.query.filter(
                db.func.lower(Producto.nombre) == nombre.lower()
            ).first()
            if existe_nombre:
                flash("Ya existe un producto con ese nombre.", "warning")
                return render_template(
                    "private/productos/productos_create.html", form=create_form
                )

            if sku:
                existe_sku = Producto.query.filter(
                    db.func.upper(Producto.sku) == sku
                ).first()
                if existe_sku:
                    flash("Ya existe un producto con ese SKU.", "warning")
                    return render_template(
                        "private/productos/productos_create.html", form=create_form
                    )

            receta_db = Receta.query.filter(
                Receta.id_receta == create_form.id_receta.data, Receta.activo == 1
            ).first()

            if not receta_db:
                flash("La receta seleccionada no es válida.", "warning")
                return render_template(
                    "private/productos/productos_create.html", form=create_form
                )

            if receta_db.id_producto is not None:
                flash(
                    "La receta seleccionada ya está asignada a otro producto.",
                    "warning",
                )
                return render_template(
                    "private/productos/productos_create.html", form=create_form
                )

            image_file = request.files.get("imagen")
            image_url = upload_product_image(image_file)

            if image_url == "INVALID_EXTENSION":
                flash("La imagen debe ser png, jpg, jpeg o webp.", "warning")
                return render_template(
                    "private/productos/productos_create.html", form=create_form
                )

            producto = Producto(
                id_categoria_producto=create_form.id_categoria_producto.data,
                sku=sku,
                nombre=nombre,
                descripcion=create_form.descripcion.data.strip()
                if create_form.descripcion.data
                else None,
                imagen=image_url,
                precio_venta=create_form.precio_venta.data,
                stock_actual=create_form.stock_actual.data,
                costo_unit_prom=receta_db.costo_estimado or 0,
                activo=1,
            )

            db.session.add(producto)
            db.session.flush()

            receta_db.id_producto = producto.id_producto

            db.session.add(receta_db)
            db.session.commit()

            log_event(
                modulo="Inventario",
                accion="Producto creado",
                detalle=f"Producto '{producto.nombre}' creado y vinculado a receta '{receta_db.nombre}'",
                severidad="INFO",
            )
            flash("Producto creado correctamente.", "success")
            return redirect(url_for("productos.listado_productos"))

    return render_template("private/productos/productos_create.html", form=create_form)


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
        create_form.sku.data = producto_db.sku
        create_form.nombre.data = producto_db.nombre
        create_form.descripcion.data = producto_db.descripcion
        create_form.precio_venta.data = producto_db.precio_venta
        create_form.stock_actual.data = producto_db.stock_actual
        create_form.id_receta.data = receta_actual.id_receta if receta_actual else None

        return render_template(
            "private/productos/productos_update.html",
            form=create_form,
            producto_db=producto_db,
            receta_actual=receta_actual,
        )

    if create_form.validate():
        sku = create_form.sku.data.strip().upper() if create_form.sku.data else None
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

        if sku:
            existe_sku = Producto.query.filter(
                db.func.upper(Producto.sku) == sku,
                Producto.id_producto != producto_db.id_producto,
            ).first()
            if existe_sku:
                flash("Ya existe otro producto con ese SKU.", "warning")
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
        producto_db.sku = sku
        producto_db.nombre = nombre
        producto_db.descripcion = (
            create_form.descripcion.data.strip()
            if create_form.descripcion.data
            else None
        )
        producto_db.precio_venta = create_form.precio_venta.data
        producto_db.stock_actual = create_form.stock_actual.data
        producto_db.costo_unit_prom = (
            receta_nueva.costo_estimado or producto_db.costo_unit_prom
        )

        db.session.add(receta_nueva)
        db.session.add(producto_db)
        db.session.commit()

        log_event(
            modulo="Inventario",
            accion="Producto actualizado",
            detalle=f"Producto '{producto_db.nombre}' actualizado",
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
        create_form.sku.data = producto_db.sku
        create_form.nombre.data = producto_db.nombre
        create_form.descripcion.data = producto_db.descripcion
        create_form.precio_venta.data = producto_db.precio_venta
        create_form.stock_actual.data = producto_db.stock_actual
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
