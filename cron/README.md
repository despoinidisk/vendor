# vendor.cron

Portable UTC cron scheduler: polls expressions, runs twin-defined jobs as subprocesses. No imports from `rest`, `ml`, `pipelines`, etc.

## Install

```bash
echo "-r vendor/cron/requirements.txt" >> requirements.txt
```

## Configure (per twin)

| Variable | Default | Purpose |
| --- | --- | --- |
| `CRON_JOBS` | *(auto)* | `module:ATTR` tuple of jobs — e.g. `cron.schedules:SCHEDULED_JOBS` |
| `CRON_INGESTION_JOBS` | `cron.schedules:INGESTION_JOBS` | GeoTwin-style fallback |
| `CRON_GDPR_JOBS` | `cron.schedules:GDPR_JOBS` | Optional GDPR retention jobs |
| `CRON_GDPR_SCRIPT` | `cron/gdpr_retention.py` | Script path for `GdprJob` |
| `CRON_COMMAND_BUILDER` | *(built-in)* | `module:fn(job, python, gdpr_path) -> list[str]` |
| `CRON_STATE_DIR` | — | Override pid/log directory |
| `CRON_STATE_NAME` | `.geotwin` | State dir under repo root when `CRON_STATE_DIR` unset |
| `CRON_PYTHONPATH_EXTRA` | — | Extra `PYTHONPATH` segments (`:`-separated) |
| `CRON_ROOT_ENV_VAR` | — | e.g. `GEOTWIN_ROOT` set in subprocess env |
| `CRON_BANNER` | `cron` | Label in start message |

## Product wiring

Keep **schedules** in the twin repo (`cron/schedules.py`). Either:

1. **Module jobs** (AI Lift): define `SCHEDULED_JOBS` as `vendor.cron.types.ModuleJob` rows.
2. **Ingestion + GDPR** (GeoTwin / AquaGuard): define `INGESTION_JOBS` / `GDPR_JOBS` using `IngestionJob` / `GdprJob` from `vendor.cron.types`, and re-export `is_due` / `next_run` from `vendor.cron.timing` if the REST API still imports `cron.schedules`.

Thin wrapper so existing `python -m cron` keeps working:

```python
# cron/__main__.py
from vendor.cron.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
```

CLI:

```bash
python -m vendor.cron start
python -m vendor.cron status
python -m vendor.cron run-now JOB_ID
```

## Boundaries

`vendor/cron/` must **not** import product packages. Job commands are built via types + optional `CRON_COMMAND_BUILDER`.