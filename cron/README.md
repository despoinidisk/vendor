# vendor.cron

Portable UTC cron scheduler: polls expressions, runs product-defined jobs as subprocesses. No domain package imports.

## Install

```bash
echo "-r vendor/cron/requirements.txt" >> requirements.txt
```

## Configure

| Variable | Default | Purpose |
| --- | --- | --- |
| `CRON_JOBS` | `cron.schedules:JOBS` | `module:ATTR` tuple of job rows |
| `CRON_EXTRA_JOBS` | — | Second `module:ATTR` merged into the schedule |
| `CRON_COMMAND_BUILDER` | — | `module:fn(job, python) -> list[str]` for custom job types |
| `CRON_REPO_ROOT` / `REPO_ROOT` | `cwd` | Repository root for subprocess `cwd` |
| `CRON_STATE_DIR` | — | Absolute pid/log directory |
| `CRON_STATE_SUBDIR` | `.vendor-state/cron` | Relative to repo root when `CRON_STATE_DIR` unset |
| `CRON_PYTHONPATH_EXTRA` | — | Extra `PYTHONPATH` segments (`:`-separated) |
| `CRON_REPO_ENV_KEY` | — | Optional env var name set to repo root in subprocesses |
| `CRON_ENV_SUBSTRING_REWRITES` | — | Comma-separated `needle>>replacement` applied to env values |
| `CRON_RUNTIME_ENV_HOOK` | — | `module:fn(env)` called after base env is built |
| `CRON_POLL_SECONDS` | `30` | Scheduler poll interval |
| `CRON_TZ` | `UTC` | Reported timezone label |
| `CRON_BANNER` | `cron` | Label in start message |

## Job types (built-in)

- **`ModuleJob`** — `python -m <module> [args…]`
- **`ScriptJob`** — `python <argv…]` (script path and flags in `argv`)

Custom dataclasses: set `CRON_COMMAND_BUILDER` or give jobs `module` / `argv` attributes.

## Product wiring

Define `JOBS` or `SCHEDULED_JOBS` in `cron/schedules.py`, point `CRON_JOBS` at it if needed.

Thin wrapper for `python -m cron`:

```python
from vendor.cron.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
```

Legacy twins (ingestion graphs, GDPR scripts) keep command logic in **product** `cron/commands.py`:

```python
def build_command(job, python: Path) -> list[str]:
    ...
```

```bash
export CRON_COMMAND_BUILDER=cron.commands:build_command
export CRON_JOBS=cron.schedules:INGESTION_JOBS
export CRON_EXTRA_JOBS=cron.schedules:GDPR_JOBS
```

## Boundaries

`vendor/cron/` must not import product packages. Schedules and argv building live in the host repo.