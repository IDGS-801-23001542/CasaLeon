import csv
from io import StringIO

from flask import render_template, request, make_response
from models import AuditoriaLog
from utils.auth import login_required
from . import auditoria


@auditoria.route("/private/admin/auditoria")
@login_required("ADMIN")
def listado_auditoria():
    q = request.args.get("q", "").strip()
    modulo = request.args.get("modulo", "").strip()
    severidad = request.args.get("severidad", "").strip()

    query = AuditoriaLog.query

    if q:
        like_term = f"%{q}%"
        query = query.filter(
            (AuditoriaLog.accion.ilike(like_term)) |
            (AuditoriaLog.detalle.ilike(like_term)) |
            (AuditoriaLog.actor_nombre.ilike(like_term)) |
            (AuditoriaLog.actor_email.ilike(like_term))
        )

    if modulo and modulo != "Todos":
        query = query.filter(AuditoriaLog.modulo == modulo)

    if severidad and severidad != "Todas":
        query = query.filter(AuditoriaLog.severidad == severidad)

    logs = query.order_by(AuditoriaLog.creado_en.desc()).all()

    modulos = [m[0] for m in AuditoriaLog.query.with_entities(AuditoriaLog.modulo).distinct().order_by(AuditoriaLog.modulo).all()]
    severidades = [s[0] for s in AuditoriaLog.query.with_entities(AuditoriaLog.severidad).distinct().order_by(AuditoriaLog.severidad).all()]

    total_logs = AuditoriaLog.query.count()
    eventos_criticos = AuditoriaLog.query.filter(AuditoriaLog.severidad.in_(["ERROR", "CRITICAL"])).count()
    cambios_usuario = AuditoriaLog.query.filter(AuditoriaLog.modulo == "Usuarios").count()
    modulos_activos = len(modulos)

    return render_template(
        "private/auditoria/auditoria.html",
        logs=logs,
        modulos=modulos,
        severidades=severidades,
        total_logs=total_logs,
        eventos_criticos=eventos_criticos,
        cambios_usuario=cambios_usuario,
        modulos_activos=modulos_activos,
        q=q,
        modulo=modulo,
        severidad=severidad,
    )


@auditoria.route("/private/admin/auditoria/export")
@login_required("ADMIN")
def exportar_auditoria():
    q = request.args.get("q", "").strip()
    modulo = request.args.get("modulo", "").strip()
    severidad = request.args.get("severidad", "").strip()

    query = AuditoriaLog.query

    if q:
        like_term = f"%{q}%"
        query = query.filter(
            (AuditoriaLog.accion.ilike(like_term)) |
            (AuditoriaLog.detalle.ilike(like_term)) |
            (AuditoriaLog.actor_nombre.ilike(like_term)) |
            (AuditoriaLog.actor_email.ilike(like_term))
        )

    if modulo and modulo != "Todos":
        query = query.filter(AuditoriaLog.modulo == modulo)

    if severidad and severidad != "Todas":
        query = query.filter(AuditoriaLog.severidad == severidad)

    logs = query.order_by(AuditoriaLog.creado_en.desc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Modulo", "Accion", "Detalle", "Severidad", "Actor", "Email", "IP", "Fecha"
    ])

    for log in logs:
        writer.writerow([
            log.id_log,
            log.modulo,
            log.accion,
            log.detalle,
            log.severidad,
            log.actor_nombre or "",
            log.actor_email or "",
            log.ip_addr or "",
            log.creado_en.strftime("%d/%m/%Y %H:%M:%S") if log.creado_en else "",
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=auditoria_logs.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response