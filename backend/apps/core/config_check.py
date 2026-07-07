"""Integration configuration validation (no secrets exposed)."""

from django.conf import settings


def _is_placeholder(value: str, *markers: str) -> bool:
    if not value or not value.strip():
        return True
    lowered = value.strip().lower()
    return any(marker in lowered for marker in markers)


def check_mpesa_config() -> dict:
    missing = []
    if _is_placeholder(settings.MPESA_CONSUMER_KEY, "your-"):
        missing.append("MPESA_CONSUMER_KEY")
    if _is_placeholder(settings.MPESA_CONSUMER_SECRET, "your-"):
        missing.append("MPESA_CONSUMER_SECRET")
    if _is_placeholder(settings.MPESA_PASSKEY, "your-"):
        missing.append("MPESA_PASSKEY")
    if _is_placeholder(settings.MPESA_CALLBACK_URL, "your-domain.com"):
        missing.append("MPESA_CALLBACK_URL")

    return {
        "configured": not missing,
        "missing": missing,
        "env": settings.MPESA_ENV,
        "shortcode": settings.MPESA_SHORTCODE,
        "callback_url": settings.MPESA_CALLBACK_URL,
    }


def check_stron_config() -> dict:
    missing = []
    if _is_placeholder(settings.STRON_COMPANY_NAME, "your-"):
        missing.append("STRON_COMPANY_NAME")
    if _is_placeholder(settings.STRON_USERNAME, "your-"):
        missing.append("STRON_USERNAME")
    if _is_placeholder(settings.STRON_PASSWORD, "your-"):
        missing.append("STRON_PASSWORD")

    return {
        "configured": not missing,
        "missing": missing,
        "base_url": settings.STRON_BASE_URL,
        "vend_by_unit": settings.STRON_VEND_BY_UNIT,
    }


def integration_status() -> dict:
    mpesa = check_mpesa_config()
    stron = check_stron_config()
    return {
        "mpesa": mpesa,
        "stron": stron,
        "ready_for_purchase": mpesa["configured"] and stron["configured"],
    }


def mpesa_config_error() -> str | None:
    status = check_mpesa_config()
    if status["configured"]:
        return None
    fields = ", ".join(status["missing"])
    return (
        f"M-Pesa is not configured. Set {fields} in backend/.env on the server, "
        "then restart the backend and celery containers."
    )


def stron_config_error() -> str | None:
    status = check_stron_config()
    if status["configured"]:
        return None
    fields = ", ".join(status["missing"])
    return (
        f"Stron Power API is not configured. Set {fields} in backend/.env on the server, "
        "then restart the backend and celery containers."
    )
