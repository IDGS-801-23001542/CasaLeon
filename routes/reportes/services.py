import hashlib
import json
from datetime import datetime, timedelta

from models import db, Pedido, PedidoDetalle
from mongo import get_mongo_db


# =========================
# HELPERS
# =========================


def _normalize_date(fecha):
    if isinstance(fecha, str):
        return datetime.strptime(fecha, "%Y-%m-%d").date()
    return fecha


def _date_range(fecha):
    start = datetime.combine(fecha, datetime.min.time())
    end = datetime.combine(fecha, datetime.max.time())
    return start, end


def _normalize_range(start_date, end_date):
    start_date = _normalize_date(start_date)
    end_date = _normalize_date(end_date)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    return start_date, end_date


# =========================
# QUERY SQL
# =========================


def get_sales_data_by_day(fecha):
    fecha = _normalize_date(fecha)
    start, end = _date_range(fecha)

    query = (
        db.session.query(
            Pedido.id_pedido,
            Pedido.total,
            Pedido.creado_en,
            PedidoDetalle.id_producto,
            PedidoDetalle.producto_nombre,
            PedidoDetalle.cantidad,
            PedidoDetalle.precio_unitario,
            PedidoDetalle.subtotal,
        )
        .join(PedidoDetalle, Pedido.id_pedido == PedidoDetalle.id_pedido)
        .filter(Pedido.estado == "Entregado")
        .filter(Pedido.creado_en >= start)
        .filter(Pedido.creado_en <= end)
    )

    return query.all()


# =========================
# CÁLCULOS
# =========================


def build_snapshot_structure(rows, fecha):
    total_sales = 0
    pedidos_ids = set()
    productos = {}

    for r in rows:
        pedidos_ids.add(r.id_pedido)
        total_sales += float(r.subtotal or 0)

        key = r.id_producto

        if key not in productos:
            productos[key] = {
                "id_producto": r.id_producto,
                "nombre": r.producto_nombre,
                "cantidad_vendida": 0,
                "monto_vendido": 0,
            }

        productos[key]["cantidad_vendida"] += float(r.cantidad or 0)
        productos[key]["monto_vendido"] += float(r.subtotal or 0)

    top_productos = sorted(
        productos.values(),
        key=lambda x: (x["cantidad_vendida"], x["monto_vendido"]),
        reverse=True,
    )[:5]

    return {
        "report_date": fecha.strftime("%Y-%m-%d"),
        "summary": {
            "total_sales": round(total_sales, 2),
            "total_orders": len(pedidos_ids),
        },
        "top_products": top_productos,
        "generated_at": datetime.utcnow().isoformat(),
    }


# =========================
# HASH
# =========================


def generate_hash(snapshot_data):
    data_string = json.dumps(snapshot_data, sort_keys=True)
    return hashlib.sha256(data_string.encode()).hexdigest()


# =========================
# MONGO
# =========================


def get_collection():
    db = get_mongo_db()
    return db["daily_sales_reports"]


def get_existing_snapshot(fecha):
    col = get_collection()
    return col.find_one({"report_date": fecha})


def save_snapshot(fecha, snapshot, hash_value):
    col = get_collection()

    snapshot["hash"] = hash_value

    col.replace_one({"report_date": fecha}, snapshot, upsert=True)


def get_snapshots_by_range(start_date, end_date):
    start_date, end_date = _normalize_range(start_date, end_date)

    col = get_collection()

    docs = list(
        col.find(
            {
                "report_date": {
                    "$gte": start_date.strftime("%Y-%m-%d"),
                    "$lte": end_date.strftime("%Y-%m-%d"),
                }
            },
            {
                "_id": 0,
                "report_date": 1,
                "summary.total_sales": 1,
                "summary.total_orders": 1,
            },
        ).sort("report_date", 1)
    )

    return docs


# =========================
# ORQUESTADOR
# =========================


def generate_daily_snapshot(fecha):
    fecha = _normalize_date(fecha)
    fecha_str = fecha.strftime("%Y-%m-%d")

    rows = get_sales_data_by_day(fecha)

    snapshot = build_snapshot_structure(rows, fecha)

    hash_value = generate_hash(snapshot)

    existing = get_existing_snapshot(fecha_str)

    if not existing:
        save_snapshot(fecha_str, snapshot, hash_value)
        return {"updated": True, "reason": "created", "snapshot": snapshot}

    if existing.get("hash") == hash_value:
        return {"updated": False, "reason": "no_changes", "snapshot": existing}

    save_snapshot(fecha_str, snapshot, hash_value)

    return {"updated": True, "reason": "hash_changed", "snapshot": snapshot}


def get_daily_snapshot(fecha):
    fecha = _normalize_date(fecha)
    fecha_str = fecha.strftime("%Y-%m-%d")

    snapshot = get_existing_snapshot(fecha_str)

    if not snapshot:
        return {"exists": False, "message": "No hay snapshot para esta fecha"}

    return {"exists": True, "snapshot": snapshot}


# =========================
# GRÁFICA DE LÍNEA
# =========================


def build_line_chart_data(start_date, end_date):
    start_date, end_date = _normalize_range(start_date, end_date)
    snapshots = get_snapshots_by_range(start_date, end_date)

    if not snapshots:
        return {
            "points": [],
            "polyline_points": "",
            "max_sales": 0,
            "has_data": False,
        }

    width = 640
    height = 260
    padding_x = 40
    padding_y = 30

    total_days = (end_date - start_date).days + 1

    snapshot_map = {
        item["report_date"]: float(item.get("summary", {}).get("total_sales", 0) or 0)
        for item in snapshots
    }

    full_series = []
    current = start_date
    while current <= end_date:
        key = current.strftime("%Y-%m-%d")
        full_series.append(
            {
                "date": key,
                "label": current.strftime("%d/%m"),
                "total_sales": snapshot_map.get(key, 0.0),
            }
        )
        current += timedelta(days=1)

    max_sales = max((item["total_sales"] for item in full_series), default=0)

    if total_days == 1:
        step_x = 0
    else:
        step_x = (width - (padding_x * 2)) / (total_days - 1)

    points = []
    polyline_parts = []

    for index, item in enumerate(full_series):
        x = padding_x + (index * step_x)

        if max_sales > 0:
            y = (
                height
                - padding_y
                - ((item["total_sales"] / max_sales) * (height - (padding_y * 2)))
            )
        else:
            y = height - padding_y

        point = {
            "date": item["date"],
            "label": item["label"],
            "total_sales": item["total_sales"],
            "x": round(x, 2),
            "y": round(y, 2),
        }
        points.append(point)
        polyline_parts.append(f"{round(x, 2)},{round(y, 2)}")

    return {
        "points": points,
        "polyline_points": " ".join(polyline_parts),
        "max_sales": max_sales,
        "has_data": True,
        "width": width,
        "height": height,
        "padding_x": padding_x,
        "padding_y": padding_y,
    }
