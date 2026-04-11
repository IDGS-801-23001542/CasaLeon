from datetime import datetime
from decimal import Decimal

from flask import render_template, request, redirect, url_for, flash

from models import (
    Producto,
    MateriaPrima,
    OrdenProduccion,
    Venta,
    Pedido,
    Merma,
)
from utils.auth import login_required
from .services import generate_daily_snapshot, get_daily_snapshot
from . import reportes


def money(value):
    return f"{float(value or 0):,.2f}"


@reportes.route("/private/reportes", methods=["GET"])
@login_required("ADMIN")
def vista_reportes():
    snapshot_date = request.args.get("snapshot_date", "").strip()

    if not snapshot_date:
        snapshot_date = datetime.now().strftime("%Y-%m-%d")

    snapshot_result = get_daily_snapshot(snapshot_date)
    sales_snapshot = snapshot_result.get("snapshot") if snapshot_result.get("exists") else None
    sales_snapshot_exists = snapshot_result.get("exists", False)
    sales_snapshot_message = snapshot_result.get("message", "")
    sales_snapshot_status = request.args.get("snapshot_status", "").strip()

    # Inventario PT
    productos_db = Producto.query.order_by(Producto.nombre.asc()).all()
    total_productos = len(productos_db)
    valor_pt = sum(
        float(p.stock_actual or 0) * float(p.costo_unit_prom or 0)
        for p in productos_db
    )
    productos_sin_stock = sum(1 for p in productos_db if float(p.stock_actual or 0) <= 0)

    # Inventario MP
    materias_db = MateriaPrima.query.order_by(MateriaPrima.nombre.asc()).all()
    total_materias = len(materias_db)
    valor_mp = sum(
        float(m.stock_actual or 0) * float(m.costo_unit_prom or 0)
        for m in materias_db
    )
    materias_stock_bajo = sum(
        1 for m in materias_db
        if float(m.stock_actual or 0) <= float(m.stock_minimo or 0)
    )

    # Producción
    producciones_db = OrdenProduccion.query.order_by(
        OrdenProduccion.id_orden_produccion.desc()
    ).all()
    producciones_completadas = sum(1 for o in producciones_db if o.estado == "COMPLETADA")
    producciones_pendientes = sum(
        1 for o in producciones_db if o.estado in ["PENDIENTE", "EN_PROCESO"]
    )
    costo_produccion = sum(float(o.costo_estimado or 0) for o in producciones_db)

    # Ventas POS
    ventas_db = Venta.query.order_by(Venta.id_venta.desc()).all()
    total_ventas = len(ventas_db)
    ingresos_ventas = sum(float(v.total or 0) for v in ventas_db)

    top_productos = {}
    for venta in ventas_db:
        for detalle in venta.detalles:
            nombre = detalle.producto_nombre
            top_productos[nombre] = top_productos.get(nombre, 0) + float(detalle.cantidad or 0)

    top_productos_lista = sorted(
        [{"nombre": k, "cantidad": v} for k, v in top_productos.items()],
        key=lambda x: x["cantidad"],
        reverse=True,
    )[:5]

    # Pedidos tienda
    pedidos_db = Pedido.query.order_by(Pedido.id_pedido.desc()).all()
    total_pedidos = len(pedidos_db)
    pedidos_pendientes = sum(
        1 for p in pedidos_db if str(p.estado).lower() in ["pendiente", "preparando"]
    )
    ingresos_pedidos = sum(float(p.total or 0) for p in pedidos_db)

    # Merma
    mermas_db = Merma.query.order_by(Merma.id_merma.desc()).all()
    total_mermas = len(mermas_db)
    merma_recuperable = sum(1 for m in mermas_db if m.tipo == "RECUPERABLE")
    merma_no_recuperable = sum(1 for m in mermas_db if m.tipo == "NO_RECUPERABLE")

    valor_merma = Decimal("0")
    for merma in mermas_db:
        for det in merma.detalles:
            valor_merma += Decimal(str(det.valor_estimado_total or 0))

    return render_template(
        "private/reportes/reportes.html",
        productos_db=productos_db,
        materias_db=materias_db,
        producciones_db=producciones_db,
        ventas_db=ventas_db,
        pedidos_db=pedidos_db,
        top_productos_lista=top_productos_lista,

        total_productos=total_productos,
        valor_pt=money(valor_pt),
        productos_sin_stock=productos_sin_stock,

        total_materias=total_materias,
        valor_mp=money(valor_mp),
        materias_stock_bajo=materias_stock_bajo,

        producciones_completadas=producciones_completadas,
        producciones_pendientes=producciones_pendientes,
        costo_produccion=money(costo_produccion),

        total_ventas=total_ventas,
        ingresos_ventas=money(ingresos_ventas),

        total_pedidos=total_pedidos,
        pedidos_pendientes=pedidos_pendientes,
        ingresos_pedidos=money(ingresos_pedidos),

        total_mermas=total_mermas,
        merma_recuperable=merma_recuperable,
        merma_no_recuperable=merma_no_recuperable,
        valor_merma=money(valor_merma),

        snapshot_date=snapshot_date,
        sales_snapshot=sales_snapshot,
        sales_snapshot_exists=sales_snapshot_exists,
        sales_snapshot_message=sales_snapshot_message,
        sales_snapshot_status=sales_snapshot_status,
    )


@reportes.route("/private/reportes/generar-snapshot", methods=["POST"])
@login_required("ADMIN")
def generar_snapshot_desde_vista():
    snapshot_date = request.form.get("snapshot_date", "").strip()

    if not snapshot_date:
        flash("Debes seleccionar una fecha para generar el snapshot.", "warning")
        return redirect(url_for("reportes.vista_reportes"))

    result = generate_daily_snapshot(snapshot_date)
    reason = result.get("reason", "")

    if reason == "created":
        flash("Snapshot creado correctamente.", "success")
    elif reason == "hash_changed":
        flash("El snapshot fue actualizado porque hubo cambios.", "success")
    elif reason == "no_changes":
        flash("No hubo cambios. Se conserva el snapshot existente.", "info")
    else:
        flash("El snapshot se procesó correctamente.", "info")

    return redirect(
        url_for(
            "reportes.vista_reportes",
            snapshot_date=snapshot_date,
            snapshot_status=reason,
        )
    )