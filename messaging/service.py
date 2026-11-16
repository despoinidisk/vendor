"""Email service factory and send entrypoint."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from vendor.messaging.backends.noop import NoopBackend
from vendor.messaging.backends.smtp import SmtpBackend
from vendor.messaging.config import get_messaging_settings
from vendor.messaging.types import EmailMessage, SendResult

if TYPE_CHECKING:
    from vendor.messaging.protocols import EmailBackend


@lru_cache
def get_email_service() -> EmailBackend:
    settings = get_messaging_settings()
    if not settings.email_enabled:
        return NoopBackend()
    provider = settings.email_provider.strip().lower()
    if provider == "smtp":
        return SmtpBackend(settings)
    if provider == "noop":
        return NoopBackend()
    raise ValueError(f"Unknown EMAIL_PROVIDER: {settings.email_provider!r}")


def send_email(message: EmailMessage) -> SendResult:
    return get_email_service().send(message)


def reset_email_service_cache() -> None:
    get_email_service.cache_clear()
    get_messaging_settings.cache_clear()