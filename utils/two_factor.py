from twilio.rest import Client
from flask import current_app


def is_two_factor_enabled() -> bool:
    return bool(current_app.config.get("TWO_FA_ENABLED", False))


def _get_twilio_client():
    account_sid = current_app.config.get("TWILIO_ACCOUNT_SID")
    auth_token = current_app.config.get("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        raise ValueError("Faltan credenciales de Twilio en la configuración.")

    return Client(account_sid, auth_token)


def _get_verify_service_sid() -> str:
    service_sid = current_app.config.get("TWILIO_VERIFY_SERVICE_SID")
    if not service_sid:
        raise ValueError("Falta TWILIO_VERIFY_SERVICE_SID en la configuración.")
    return service_sid


def normalize_phone_mx(phone: str) -> str:
    """
    Normaliza un número mexicano al formato E.164.
    Ejemplos:
      4771234567      -> +524771234567
      52 477 123 4567 -> +524771234567
      +524771234567   -> +524771234567
    """
    raw = (phone or "").strip()
    if not raw:
        raise ValueError("El número telefónico está vacío.")

    if raw.startswith("+"):
        digits = "+" + "".join(ch for ch in raw if ch.isdigit())
        if len(digits) < 12 or len(digits) > 16:
            raise ValueError("Número telefónico inválido.")
        return digits

    only_digits = "".join(ch for ch in raw if ch.isdigit())

    if len(only_digits) == 10:
        return f"+52{only_digits}"

    if len(only_digits) == 12 and only_digits.startswith("52"):
        return f"+{only_digits}"

    raise ValueError("Número telefónico inválido para México.")


def send_sms_verification(phone: str) -> str:
    client = _get_twilio_client()
    service_sid = _get_verify_service_sid()
    phone_e164 = normalize_phone_mx(phone)

    verification = client.verify.v2.services(service_sid).verifications.create(
        to=phone_e164,
        channel="sms",
    )
    return verification.status


def check_sms_verification(phone: str, code: str) -> bool:
    client = _get_twilio_client()
    service_sid = _get_verify_service_sid()
    phone_e164 = normalize_phone_mx(phone)

    result = client.verify.v2.services(service_sid).verification_checks.create(
        to=phone_e164,
        code=(code or "").strip(),
    )
    return result.status == "approved"