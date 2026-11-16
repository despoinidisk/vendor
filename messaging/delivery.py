"""Deliver and schedule email jobs."""

from __future__ import annotations

import logging
from typing import Any

from vendor.messaging.config import get_messaging_settings
from vendor.messaging.registry import get_composer, get_defer_hook, get_recipient_resolver
from vendor.messaging.service import send_email
from vendor.messaging.types import DeliveryResult, EmailDeliveryRequest

logger = logging.getLogger(__name__)


def deliver(request: EmailDeliveryRequest) -> DeliveryResult:
    """Resolve audience, compose, and send (synchronous)."""
    resolver = get_recipient_resolver()
    composer = get_composer()
    recipients = resolver.resolve(request.audience)
    if not recipients:
        return DeliveryResult(
            delivery_id=request.delivery_id,
            sent=0,
            failed=0,
            skipped="no_recipients",
        )

    sent = 0
    failed = 0
    for recipient in recipients:
        message = composer.compose(request, recipient)
        result = send_email(message)
        if result.ok:
            sent += 1
        else:
            failed += 1
            logger.warning(
                "Email failed delivery=%s to=%s: %s",
                request.delivery_id,
                recipient.email,
                result.detail,
            )

    if failed and not sent:
        raise RuntimeError(f"All email sends failed for delivery {request.delivery_id}")

    return DeliveryResult(
        delivery_id=request.delivery_id,
        sent=sent,
        failed=failed,
    )


def deliver_from_dict(payload: dict[str, Any]) -> dict[str, Any]:
    result = deliver(EmailDeliveryRequest.from_dict(payload))
    return {
        "delivery_id": result.delivery_id,
        "sent": result.sent,
        "failed": result.failed,
        "skipped": result.skipped,
    }


def schedule_delivery(request: EmailDeliveryRequest) -> None:
    """Enqueue delivery when email is enabled and a defer hook is registered."""
    settings = get_messaging_settings()
    if not settings.email_enabled:
        return
    hook = get_defer_hook()
    if hook is None:
        logger.debug(
            "Email defer hook not set; skipping async delivery %s",
            request.delivery_id,
        )
        return
    try:
        hook(payload=request.to_dict())
    except Exception as exc:
        logger.warning(
            "Failed to enqueue email delivery %s: %s",
            request.delivery_id,
            exc,
        )