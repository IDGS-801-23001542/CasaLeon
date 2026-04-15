import base64
from io import BytesIO

import pyotp
import qrcode
from flask import current_app


def user_requires_2fa(user) -> bool:
    if not user:
        return False

    rol_codigo = None
    if getattr(user, "rol", None):
        rol_codigo = getattr(user.rol, "codigo", None)

    if rol_codigo in ("ADMIN", "EMPLEADO"):
        return True

    return bool(getattr(user, "two_factor_required", 0) == 1)


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def build_totp_uri(email: str, secret: str) -> str:
    issuer = current_app.config.get("TOTP_ISSUER", "Casa Leon")
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def verify_totp_code(secret: str, code: str) -> bool:
    if not secret or not code:
        return False

    totp = pyotp.TOTP(secret)
    return totp.verify((code or "").strip(), valid_window=1)


def build_qr_base64(uri: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{encoded}"