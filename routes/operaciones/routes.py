from decimal import Decimal, InvalidOperation
import datetime

from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import or_

import forms
from models import (
    db,
    MateriaPrima,
    Receta,
    RecetaDetalle,
    Producto,
    AuditoriaLog,
    OrdenProduccion,
    OrdenProduccionDetalle,
)
from utils.auth import login_required
from utils.audit import log_event
from . import operaciones


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