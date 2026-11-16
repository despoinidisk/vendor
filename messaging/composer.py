"""Default plain-text composer (override via registry)."""

from __future__ import annotations

from vendor.messaging.config import get_messaging_settings
from vendor.messaging.types import EmailDeliveryRequest, EmailMessage, ResolvedRecipient


def _action_url(request: EmailDeliveryRequest) -> str | None:
    explicit = request.context.get("action_url")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    path = request.context.get("action_path")
    if isinstance(path, str) and path.strip():
        base = get_messaging_settings().app_public_url.rstrip("/")
        return f"{base}/{path.lstrip('/')}"
    return None


class PlainTextComposer:
    def compose(
        self,
        request: EmailDeliveryRequest,
        recipient: ResolvedRecipient,
    ) -> EmailMessage:
        settings = get_messaging_settings()
        link = _action_url(request)
        category_line = f"Category: {request.category}" if request.category else ""
        scope = request.context.get("scope_label")
        scope_line = f"Scope: {scope}" if isinstance(scope, str) and scope.strip() else ""

        body_parts = [
            request.body.strip() or "(no details)",
            "",
            "---",
            category_line,
            scope_line,
        ]
        body_parts = [part for part in body_parts if part]
        if link:
            product = settings.email_product_name
            body_parts.extend(["", f"Open in {product}: {link}"])
        footer = settings.email_footer
        if footer:
            body_parts.extend(["", footer])

        return EmailMessage(
            to_address=recipient.email,
            to_name=recipient.display_name,
            subject=request.subject,
            body_text="\n".join(body_parts) + "\n",
            from_address=settings.email_from,
        )