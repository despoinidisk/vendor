# vendor

Portable, domain-free kits shared across GeoTwin, AquaGuard, and other twins. Copy the whole `vendor/` tree into a new repo and wire product-specific code in `tasks/`, `emails/`, etc.

| Package | Import | CLI |
| --- | --- | --- |
| [`vendor/jobs/`](jobs/) | `vendor.jobs` | `python -m vendor.jobs worker` |
| [`vendor/messaging/`](messaging/) | `vendor.messaging` | (library only) |
| [`vendor/cron/`](cron/) | `vendor.cron` | `python -m vendor.cron start` |

## Repeated modules under `~/work/repos/`

| Pattern | Twins using it | In this repo |
| --- | --- | --- |
| Procrastinate worker kit (`jobs/`) | GeoTwin (`vendor/jobs`), AquaGuard, AI Lift, PerTouriSM, time-machine (`jobs/` at root — migrate to `vendor.jobs`) | [`jobs/`](jobs/) |
| Email kit (`messaging/`) | GeoTwin | [`messaging/`](messaging/) |
| Ingestion cron daemon (`cron/`) | GeoTwin-ELBG, aqua-guard, ai-lift, pertourism | [`cron/`](cron/) |
| `*_paths.py` (`.geotwin/`, `.aquaguard/`, …) | GeoTwin, AquaGuard, AI Lift, PerTouriSM | *product-local* (set `CRON_STATE_NAME` / `CRON_REPO_ROOT`) |

GeoTwin product wiring for email: [`emails/`](../emails/) (Keycloak + notifications).
