# vendor

Portable, domain-free kits shared across GeoTwin, AquaGuard, and other twins. Copy the whole `vendor/` tree into a new repo and wire product-specific code in `tasks/`, `emails/`, etc.

| Package | Import | CLI |
| --- | --- | --- |
| [`vendor/jobs/`](jobs/) | `vendor.jobs` | `python -m vendor.jobs worker` |
| [`vendor/messaging/`](messaging/) | `vendor.messaging` | (library only) |

GeoTwin product wiring for email: [`emails/`](../emails/) (Keycloak + notifications).
