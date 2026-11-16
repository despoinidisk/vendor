"""No-op backend when email is disabled."""

from __future__ import annotations

import logging

from vendor.messaging.types import EmailMessage, SendResult

logger = logging.getLogger(__name__)


class NoopBackend:
    provider_name = "noop"

    def send(self, message: EmailMessage) -> SendResult:
        logger.debug(
            "Noop email (not sent): to=%s subject=%s",
            message.to_address,
            message.subject,
        )
        return SendResult(ok=True, provider=self.provider_name, detail="skipped")