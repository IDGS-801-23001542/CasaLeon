import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import current_app, request, g, redirect, url_for, flash, make_response

from models import db, AuthToken


COOKIE_NAME = "casaleon_session"


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def issue_token(subject_type: str, subject_id: int) -> str:
    raw = secrets.token_urlsafe(48)
    token_hash = _hash_token(raw)

    expires_at = datetime.utcnow() + timedelta(
        days=current_app.config.get("REMEMBER_COOKIE_DAYS", 7)
    )

    token = AuthToken(
        subject_type=subject_type,
        subject_id=subject_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=0,
        user_agent=(request.headers.get("User-Agent") or "")[:255],
        ip_addr=(request.remote_addr or "")[:45],
    )

    db.session.add(token)
    db.session.commit()

    return raw


def revoke_token(raw: str | None):
    if not raw:
        return

    token_hash = _hash_token(raw)
    token = AuthToken.query.filter_by(token_hash=token_hash, revoked=0).first()

    if token:
        token.revoked = 1
        db.session.add(token)
        db.session.commit()


def get_identity():
    raw = request.cookies.get(COOKIE_NAME)
    if not raw:
        return None

    token_hash = _hash_token(raw)

    token = AuthToken.query.filter_by(
        token_hash=token_hash,
        revoked=0,
    ).first()

    if not token:
        return None

    if token.expires_at and token.expires_at < datetime.utcnow():
        token.revoked = 1
        db.session.add(token)
        db.session.commit()
        return None

    return {
        "type": token.subject_type,
        "id": token.subject_id,
    }


def build_login_response(target_url: str, raw_token: str, remember: bool = False):
    resp = make_response(redirect(target_url))

    max_age = None
    expires = None

    if remember:
        days = int(current_app.config.get("REMEMBER_COOKIE_DAYS", 7))
        max_age = days * 24 * 60 * 60
        expires = datetime.utcnow() + timedelta(days=days)

    resp.set_cookie(
        COOKIE_NAME,
        raw_token,
        max_age=max_age,
        expires=expires,
        httponly=True,
        secure=bool(current_app.config.get("SESSION_COOKIE_SECURE", False)),
        samesite=current_app.config.get("SESSION_COOKIE_SAMESITE", "Lax"),
        path="/",
    )
    return resp


def login_required(*roles):
    normalized_roles = []

    for role in roles:
        if isinstance(role, (list, tuple, set)):
            normalized_roles.extend(role)
        else:
            normalized_roles.append(role)

    normalized_roles = tuple(normalized_roles)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not g.user:
                flash("Debes iniciar sesión para continuar.", "warning")
                return redirect(url_for("auth.login"))

            if normalized_roles and g.role not in normalized_roles:
                flash("No tienes permisos para acceder a esta sección.", "danger")
                return redirect(url_for("auth.post_login"))

            return fn(*args, **kwargs)

        return wrapper

    return decorator