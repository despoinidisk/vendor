"""Portable email delivery kit (SMTP and pluggable backends)."""

from vendor.messaging.delivery import deliver, deliver_from_dict, schedule_delivery
from vendor.messaging.registry import (
    configure_composer,
    configure_defer_hook,
    configure_recipient_resolver,
    reset_registry,
)
from vendor.messaging.service import get_email_service, reset_email_service_cache, send_email
from vendor.messaging.types import (
    DeliveryResult,
    EmailDeliveryRequest,
    EmailMessage,
    ResolvedRecipient,
    SendResult,
)

__all__ = [
    "DeliveryResult",
    "EmailDeliveryRequest",
    "EmailMessage",
    "ResolvedRecipient",
    "SendResult",
    "configure_composer",
    "configure_defer_hook",
    "configure_recipient_resolver",
    "deliver",
    "deliver_from_dict",
    "get_email_service",
    "reset_email_service_cache",
    "reset_registry",
    "schedule_delivery",
    "send_email",
]