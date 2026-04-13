from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
import tempfile
import subprocess
import shutil
import os

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    current_app,
    after_this_request,
)

from utils.auth import login_required
from .services import (
    generate_daily_snapshot,
    build_line_chart_data,
    get_sales_summary_by_range,
    get_top_products_by_range,
)
from . import reportes


def money(value):
    return f"{float(value or 0):,.2f}"


@reportes.route("/private/reportes", methods=["GET"])
@login_required("ADMIN")
def vista_reportes():
    range_start_date = request.args.get("start_date", "").strip()
    range_end_date = request.args.get("end_date", "").strip()

    today_str = datetime.now().strftime("%Y-%m-%d")

    if not range_start_date:
        range_start_date = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")

    if not range_end_date:
        range_end_date = today_str

    summary = get_sales_summary_by_range(range_start_date, range_end_date)
    top_products = get_top_products_by_range(range_start_date, range_end_date)
    top_product = top_products[0] if top_products else None
    line_chart = build_line_chart_data(range_start_date, range_end_date)

    return render_template(
        "private/reportes/reportes.html",
        range_start_date=range_start_date,
        range_end_date=range_end_date,
        total_sales=money(summary.get("total_sales", 0)),
        total_orders=summary.get("total_orders", 0),
        top_products=top_products,
        top_product=top_product,
        line_chart=line_chart,
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
            start_date=request.form.get("start_date", "").strip(),
            end_date=request.form.get("end_date", "").strip(),
        )
    )


@reportes.route("/private/reportes/export/mysql", methods=["GET"])
@login_required("ADMIN")
def exportar_respaldo_mysql():
    database_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "").strip()

    if not database_uri:
        flash("No se encontró la configuración de la base de datos.", "danger")
        return redirect(url_for("reportes.vista_reportes"))

    parsed = urlparse(database_uri)

    if not parsed.scheme.startswith("mysql"):
        flash("La exportación solo está implementada para MySQL.", "warning")
        return redirect(url_for("reportes.vista_reportes"))

    mysqldump_path = current_app.config.get("MYSQLDUMP_PATH") or shutil.which(
        "mysqldump"
    )

    if not mysqldump_path:
        flash(
            "No se encontró 'mysqldump'. Agrégalo al PATH o configura MYSQLDUMP_PATH.",
            "danger",
        )
        return redirect(url_for("reportes.vista_reportes"))

    host = parsed.hostname or "localhost"
    port = str(parsed.port or 3306)
    user = parsed.username or ""
    password = parsed.password or ""
    db_name = (parsed.path or "").lstrip("/")

    if not db_name:
        flash("No se pudo identificar el nombre de la base de datos.", "danger")
        return redirect(url_for("reportes.vista_reportes"))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"casaleon_mysql_backup_{timestamp}.sql"

    temp_dir = tempfile.gettempdir()
    backup_path = Path(temp_dir) / backup_name

    command = [
        mysqldump_path,
        f"--host={host}",
        f"--port={port}",
        f"--user={user}",
        "--single-transaction",
        "--routines",
        "--triggers",
        "--databases",
        db_name,
    ]

    env = os.environ.copy()
    if password:
        env["MYSQL_PWD"] = password

    try:
        with open(backup_path, "wb") as output_file:
            result = subprocess.run(
                command,
                stdout=output_file,
                stderr=subprocess.PIPE,
                env=env,
                check=False,
            )

        if result.returncode != 0:
            error_text = result.stderr.decode("utf-8", errors="replace").strip()
            if backup_path.exists():
                backup_path.unlink(missing_ok=True)

            flash(
                f"No se pudo exportar la base de datos. Detalle: {error_text or 'Error desconocido.'}",
                "danger",
            )
            return redirect(url_for("reportes.vista_reportes"))

        @after_this_request
        def remove_file(response):
            try:
                if backup_path.exists():
                    backup_path.unlink(missing_ok=True)
            except Exception:
                pass
            return response

        return send_file(
            backup_path,
            as_attachment=True,
            download_name=backup_name,
            mimetype="application/sql",
        )

    except Exception as e:
        if backup_path.exists():
            backup_path.unlink(missing_ok=True)

        flash(f"Ocurrió un error al exportar la base de datos: {e}", "danger")
        return redirect(url_for("reportes.vista_reportes"))
