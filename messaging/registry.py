"""Host-provided resolver, composer, and async defer hooks."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vendor.messaging.protocols import EmailComposer, RecipientResolver

_resolver: RecipientResolver | None = None
_composer: EmailComposer | None = None
_defer_hook: Callable[..., None] | None = None


def configure_recipient_resolver(resolver: RecipientResolver) -> None:
    global _resolver  # noqa: PLW0603
    _resolver = resolver


def configure_composer(composer: EmailComposer) -> None:
    global _composer  # noqa: PLW0603
    _composer = composer


def configure_defer_hook(hook: Callable[..., None]) -> None:
    """Register how queued deliveries are enqueued (e.g. Procrastinate ``task.defer``)."""
    global _defer_hook  # noqa: PLW0603
    _defer_hook = hook


def get_recipient_resolver() -> RecipientResolver:
    if _resolver is None:
        raise RuntimeError(
            "Recipient resolver not configured. "
            "Call messaging.registry.configure_recipient_resolver() at worker startup.",
        )
    return _resolver


def get_composer() -> EmailComposer:
    if _composer is None:
        from vendor.messaging.composer import PlainTextComposer

        return PlainTextComposer()
    return _composer


def get_defer_hook() -> Callable[..., None] | None:
    return _defer_hook


def reset_registry() -> None:
    """Clear hooks (tests)."""
    global _resolver, _composer, _defer_hook  # noqa: PLW0603
    _resolver = None
    _composer = None
    _defer_hook = None