"""Portable email types (no domain or IAM imports)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class EmailMessage:
    to_address: str
    subject: str
    body_text: str
    from_address: str | None = None
    to_name: str | None = None
    reply_to: str | None = None
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SendResult:
    ok: bool
    provider: str
    detail: str = ""
    message_id: str | None = None


@dataclass(frozen=True, slots=True)
class ResolvedRecipient:
    email: str
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class EmailDeliveryRequest:
    """Host-agnostic job payload: subject/body plus opaque audience for resolvers."""

    delivery_id: str
    category: str
    subject: str
    body: str
    audience: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EmailDeliveryRequest:
        return cls(
            delivery_id=str(data["delivery_id"]),
            category=str(data.get("category") or ""),
            subject=str(data.get("subject") or ""),
            body=str(data.get("body") or ""),
            audience=dict(data.get("audience") or {}),
            context=dict(data.get("context") or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "delivery_id": self.delivery_id,
            "category": self.category,
            "subject": self.subject,
            "body": self.body,
            "audience": self.audience,
            "context": self.context,
        }


@dataclass(frozen=True, slots=True)
class DeliveryResult:
    delivery_id: str
    sent: int
    failed: int
    skipped: str | None = None