from flask import g, request
from models import db, AuditoriaLog


def log_event(
    modulo: str,
    accion: str,
    detalle: str,
    severidad: str = "INFO",
    actor_tipo: str | None = None,
    actor_id: int | None = None,
    actor_nombre: str | None = None,
    actor_email: str | None = None,
):
    try:
        if g.get("user") is not None:
            if not actor_tipo:
                actor_tipo = "CLIENTE" if g.get("role") == "CLIENTE" else "USUARIO"

            if actor_id is None:
                actor_id = getattr(g.user, "id_cliente", None) or getattr(g.user, "id_usuario", None)

            if not actor_nombre:
                actor_nombre = getattr(g.user, "nombre", None)

            if not actor_email:
                actor_email = getattr(g.user, "email", None)
    except Exception:
        pass

    log = AuditoriaLog(
        modulo=modulo,
        accion=accion,
        detalle=detalle,
        severidad=severidad.upper(),
        actor_tipo=actor_tipo,
        actor_id=actor_id,
        actor_nombre=actor_nombre,
        actor_email=actor_email,
        ip_addr=request.remote_addr,
        user_agent=(request.headers.get("User-Agent", "")[:255]),
    )
    db.session.add(log)
    db.session.commit()