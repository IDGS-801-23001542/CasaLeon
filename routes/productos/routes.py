from . import productos

from flask import render_template, request, redirect, url_for, flash
import forms
from models import db, Producto, CategoriaProducto


def cargar_categorias(form):
    categorias = CategoriaProducto.query.order_by(CategoriaProducto.nombre.asc()).all()
    form.id_categoria_producto.choices = [
        (c.id_categoria_producto, c.nombre) for c in categorias
    ]


@productos.route("/private/productos")
def listado_productos():
    create_form = forms.ProductoForm()
    cargar_categorias(create_form)

    search = request.args.get("search", "").strip()

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

    productos_db = query.order_by(Producto.nombre.asc()).all()

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
        total_productos=total_productos,
        productos_activos=productos_activos,
        productos_inactivos=productos_inactivos,
        valor_inventario=f"{valor_inventario:,.2f}",
        search=search,
    )


@productos.route("/private/productos/create", methods=["GET", "POST"])
def crear_producto():
    create_form = forms.ProductoForm()
    cargar_categorias(create_form)

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

            producto = Producto(
                id_categoria_producto=create_form.id_categoria_producto.data,
                sku=sku,
                nombre=nombre,
                descripcion=create_form.descripcion.data.strip()
                if create_form.descripcion.data
                else None,
                precio_venta=create_form.precio_venta.data,
                stock_actual=create_form.stock_actual.data,
                costo_unit_prom=create_form.costo_unit_prom.data,
                activo=1,
            )

            db.session.add(producto)
            db.session.commit()

            flash("Producto creado correctamente.", "success")
            return redirect(url_for("productos.listado_productos"))

    return render_template("private/productos/productos_create.html", form=create_form)


@productos.route("/private/productos/update", methods=["GET", "POST"])
def actualizar_producto():
    create_form = forms.ProductoForm()
    cargar_categorias(create_form)

    if request.method == "GET":
        id_producto = request.args.get("id")
        producto_db = (
            db.session.query(Producto)
            .filter(Producto.id_producto == id_producto)
            .first()
        )

        if not producto_db:
            flash("Producto no encontrado.", "danger")
            return redirect(url_for("productos.listado_productos"))

        create_form.id_categoria_producto.data = producto_db.id_categoria_producto
        create_form.sku.data = producto_db.sku
        create_form.nombre.data = producto_db.nombre
        create_form.descripcion.data = producto_db.descripcion
        create_form.precio_venta.data = producto_db.precio_venta
        create_form.stock_actual.data = producto_db.stock_actual
        create_form.costo_unit_prom.data = producto_db.costo_unit_prom

        return render_template(
            "private/productos/productos_update.html",
            form=create_form,
            producto_db=producto_db,
        )

    if request.method == "POST":
        id_producto = request.args.get("id")
        producto_db = (
            db.session.query(Producto)
            .filter(Producto.id_producto == id_producto)
            .first()
        )

        if not producto_db:
            flash("Producto no encontrado.", "danger")
            return redirect(url_for("productos.listado_productos"))

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
                    )

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
            producto_db.costo_unit_prom = create_form.costo_unit_prom.data
            producto_db.activo = 1

            db.session.add(producto_db)
            db.session.commit()

            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for("productos.listado_productos"))

        return render_template(
            "private/productos/productos_update.html",
            form=create_form,
            producto_db=producto_db,
        )


@productos.route("/private/productos/delete", methods=["GET", "POST"])
def eliminar_producto():
    create_form = forms.ProductoForm()
    cargar_categorias(create_form)

    if request.method == "GET":
        id_producto = request.args.get("id")
        producto_db = (
            db.session.query(Producto)
            .filter(Producto.id_producto == id_producto)
            .first()
        )

        if not producto_db:
            flash("Producto no encontrado.", "danger")
            return redirect(url_for("productos.listado_productos"))

        create_form.id_categoria_producto.data = producto_db.id_categoria_producto
        create_form.sku.data = producto_db.sku
        create_form.nombre.data = producto_db.nombre
        create_form.descripcion.data = producto_db.descripcion
        create_form.precio_venta.data = producto_db.precio_venta
        create_form.stock_actual.data = producto_db.stock_actual
        create_form.costo_unit_prom.data = producto_db.costo_unit_prom

        return render_template(
            "private/productos/productos_delete.html",
            form=create_form,
            producto_db=producto_db,
        )

    if request.method == "POST":
        id_producto = request.args.get("id")
        producto_db = (
            db.session.query(Producto)
            .filter(Producto.id_producto == id_producto)
            .first()
        )

        if not producto_db:
            flash("Producto no encontrado.", "danger")
            return redirect(url_for("productos.listado_productos"))

        producto_db.activo = 0
        db.session.add(producto_db)
        db.session.commit()

        flash("Producto desactivado correctamente.", "info")
        return redirect(url_for("productos.listado_productos"))
