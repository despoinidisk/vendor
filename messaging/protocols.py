"""Backend and resolver interfaces."""

from __future__ import annotations

from typing import Any, Protocol

from vendor.messaging.types import EmailDeliveryRequest, EmailMessage, ResolvedRecipient, SendResult


class EmailBackend(Protocol):
    """Send a single email message via a concrete provider."""

    provider_name: str

    def send(self, message: EmailMessage) -> SendResult:
        """Deliver one message. Implementations must not raise for expected failures."""
        ...


class RecipientResolver(Protocol):
    """Resolve opaque audience dicts to deliverable addresses (provided by the host app)."""

    def resolve(self, audience: dict[str, Any]) -> list[ResolvedRecipient]:
        ...


class EmailComposer(Protocol):
    """Build provider-ready messages from a delivery request and one recipient."""

    def compose(
        self,
        request: EmailDeliveryRequest,
        recipient: ResolvedRecipient,
    ) -> EmailMessage:
        ...