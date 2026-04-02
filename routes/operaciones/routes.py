from flask import render_template
from utils.auth import login_required
from . import operaciones


@operaciones.route("/private/materia-prima")
@login_required(["ADMIN", "EMPLEADO"])
def materia_prima():
    return render_template(
        "private/shared/en_construccion.html",
        titulo="Inventario de Materia Prima",
        subtitulo="Módulo asignado a Erick. Queda visible sin romper navegación.",
    )


@operaciones.route("/private/produccion")
@login_required(["ADMIN", "EMPLEADO"])
def produccion():
    return render_template(
        "private/shared/en_construccion.html",
        titulo="Producción",
        subtitulo="Módulo asignado a Erick. Queda visible sin romper navegación.",
    )


@operaciones.route("/private/recetas")
@login_required("ADMIN")
def recetas():
    return render_template(
        "private/shared/en_construccion.html",
        titulo="Recetas / BOM",
        subtitulo="Módulo asignado a Erick. Queda visible sin romper navegación.",
    )


@operaciones.route("/private/ventas")
@login_required(["ADMIN", "EMPLEADO"])
def ventas():
    return render_template(
        "private/shared/en_construccion.html",
        titulo="Ventas",
        subtitulo="Pantalla pendiente de integración final.",
    )


@operaciones.route("/private/reportes")
@login_required("ADMIN")
def reportes():
    return render_template(
        "private/shared/en_construccion.html",
        titulo="Reportes",
        subtitulo="Pantalla pendiente de integración final.",
    )