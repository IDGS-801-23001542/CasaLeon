import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    current_app,
    request,
    g,
    flash,
    redirect,
    url_for,
    make_response,
)
from models import db, AuthToken


COOKIE_NAME = "cl_token"


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def issue_token(subject_type: str, subject_id: int) -> str:
    raw = secrets.token_urlsafe(48)
    token_hash = hash_token(raw)

    expires = datetime.utcnow() + timedelta(
        minutes=int(current_app.config.get("TOKEN_EXPIRES_MINUTES", 10))
    )

    token = AuthToken(
        subject_type=subject_type,
        subject_id=subject_id,
        token_hash=token_hash,
        expires_at=expires,
        revoked=0,
        user_agent=(request.headers.get("User-Agent", "")[:255]),
        ip_addr=request.remote_addr,
    )
    db.session.add(token)
    db.session.commit()
    return raw


def revoke_token(raw: str | None):
    if not raw:
        return

    token_hash = hash_token(raw)
    token = AuthToken.query.filter_by(token_hash=token_hash, revoked=0).first()
    if token:
        token.revoked = 1
        db.session.commit()


def get_identity():
    raw = request.cookies.get(COOKIE_NAME)
    if not raw:
        return None

    token_hash = hash_token(raw)
    token = AuthToken.query.filter_by(token_hash=token_hash, revoked=0).first()
    if not token:
        return None

    if token.expires_at < datetime.utcnow():
        token.revoked = 1
        db.session.commit()
        return None

    return {"raw": raw, "type": token.subject_type, "id": token.subject_id}


def build_login_response(redirect_to: str, raw_token: str):
    resp = make_response(redirect(redirect_to))
    resp.set_cookie(
        COOKIE_NAME,
        raw_token,
        httponly=True,
        samesite="Lax",
        secure=bool(current_app.config.get("SESSION_COOKIE_SECURE", False)),
        max_age=int(current_app.config.get("TOKEN_EXPIRES_MINUTES", 10)) * 60,
    )
    return resp


def login_required(roles=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not g.user:
                flash("Primero inicia sesión.", "warning")
                return redirect(url_for("auth.login"))

            if roles:
                allowed = roles if isinstance(roles, (list, tuple, set)) else [roles]
                if g.role not in allowed:
                    flash("No tienes permisos para entrar aquí.", "danger")
                    return redirect(url_for("auth.post_login"))

            return fn(*args, **kwargs)

        return wrapper

    return decorator