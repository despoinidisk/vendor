# messaging — portable email kit

Provider-agnostic email sending with pluggable SMTP (or custom) backends. Lives under `vendor/messaging/`; **do not** import domain packages from here.

## Quick start (vendor)

```bash
cp -r /path/to/GeoTwin-ELBG/vendor ./vendor
echo "-r vendor/messaging/requirements.txt" >> requirements.txt
```

```python
from vendor.messaging import (
    configure_recipient_resolver,
    configure_defer_hook,
    deliver,
    schedule_delivery,
    send_email,
)
from vendor.messaging.types import EmailDeliveryRequest, EmailMessage
```

1. Implement or reuse a `RecipientResolver` (maps opaque `audience` dicts to emails).
2. Optionally `configure_composer()` (default: `PlainTextComposer`).
3. Optionally `configure_defer_hook(fn)` where `fn(payload=dict)` enqueues background work.
4. Call `deliver(request)` synchronously or `schedule_delivery(request)` when a hook is set.

## Layout

| Path | Role |
|------|------|
| `protocols.py` | `EmailBackend`, `RecipientResolver`, `EmailComposer` |
| `types.py` | `EmailMessage`, `EmailDeliveryRequest`, `DeliveryResult` |
| `config.py` | `EMAIL_*`, `SMTP_*`, `APP_PUBLIC_URL`, `EMAIL_PRODUCT_NAME` |
| `backends/smtp.py` | Generic SMTP (Mailtrap, SES SMTP, etc.) |
| `backends/noop.py` | Default when `EMAIL_ENABLED=false` |
| `registry.py` | Host hooks: resolver, composer, defer |
| `delivery.py` | `deliver()` / `schedule_delivery()` |
| `composer.py` | Default plain-text template |

## Hard rule

`vendor/messaging/` must **not** import `auth`, `tasks`, `db`, `rest`, or other product code. GeoTwin wires Keycloak in [`emails/`](../../emails/).

## Mailtrap (SMTP)

```bash
EMAIL_ENABLED=true
EMAIL_PROVIDER=smtp
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=...
SMTP_PASSWORD=...
```

## New backend

1. Add `backends/your_provider.py` implementing `EmailBackend`.
2. Register in `service.py`.
3. Set `EMAIL_PROVIDER=your_provider`.