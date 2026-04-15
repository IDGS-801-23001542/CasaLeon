import random
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_mail import Message

from extensions import mail


def _serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt=current_app.config["SECURITY_PASSWORD_SALT"],
    )


def generate_email_verification_token(email: str) -> str:
    return _serializer().dumps(email)


def confirm_email_verification_token(token: str, max_age=3600):
    try:
        email = _serializer().loads(token, max_age=max_age)
        return email
    except Exception:
        return None


def generate_email_code(length: int = 6) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def send_code_email(user_email: str, user_name: str, code: str, purpose: str = "login"):
    sender = (current_app.config.get("MAIL_DEFAULT_SENDER") or "").strip()

    if not sender:
        raise RuntimeError("MAIL_DEFAULT_SENDER no está configurado.")

    if purpose == "register":
        subject = "Código de verificación de registro | Casa León"
        intro = "Usa este código para confirmar tu registro en Casa León."
    else:
        subject = "Código de acceso | Casa León"
        intro = "Usa este código para completar tu inicio de sesión en Casa León."

    msg = Message(
        subject=subject,
        recipients=[user_email],
        sender=sender,
    )

    msg.html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;">
      <h2>Hola, {user_name}</h2>
      <p>{intro}</p>
      <div style="margin:24px 0;padding:18px 20px;background:#f5f5f4;border-radius:16px;text-align:center;">
        <p style="margin:0;font-size:13px;color:#57534e;">Tu código es</p>
        <p style="margin:10px 0 0;font-size:32px;font-weight:700;letter-spacing:8px;color:#1c1917;">
          {code}
        </p>
      </div>
      <p>El código expira en 10 minutos.</p>
      <p>Si no solicitaste esto, puedes ignorar este correo.</p>
    </div>
    """

    mail.send(msg)