# vendor

Portable kits copied into product repos. Domain code stays in `tasks/`, `cron/schedules.py`, adapters, etc.

| Package | Import | CLI |
| --- | --- | --- |
| [`vendor/jobs/`](jobs/) | `vendor.jobs` | `python -m vendor.jobs worker` |
| [`vendor/messaging/`](messaging/) | `vendor.messaging` | (library only) |
| [`vendor/cron/`](cron/) | `vendor.cron` | `python -m vendor.cron start` |

## Shared conventions

| Variable | Used by | Purpose |
| --- | --- | --- |
| `REPO_ROOT` | jobs, cron | Repository root (overridable via `JOBS_REPO_ROOT` / `CRON_REPO_ROOT`) |
| `JOBS_STATE_DIR` / `CRON_STATE_DIR` | worker, cron | Absolute runtime state (pid, log) |
| `JOBS_STATE_SUBDIR` / `CRON_STATE_SUBDIR` | worker, cron | Default `.vendor-state/…` under repo root |

## Repeated modules under `~/work/repos/`

| Pattern | In this repo | Product owns |
| --- | --- | --- |
| Procrastinate worker | [`jobs/`](jobs/) | `tasks/`, `JOBS_APP` |
| Email transport | [`messaging/`](messaging/) | recipient resolver, templates, defer hook |
| Cron daemon | [`cron/`](cron/) | `cron/schedules.py`, optional `cron/commands.py` |
| `*_paths.py` | — | per-repo state dir names (map via `*_STATE_DIR` env) |

## Legacy twin env (when syncing)

Products that used `.geotwin/` pid files can set without forking vendor:

```bash
export REPO_ROOT=$PWD
export JOBS_STATE_SUBDIR=.geotwin
export CRON_STATE_SUBDIR=.geotwin
```

Ingestion-style cron still needs `CRON_COMMAND_BUILDER=cron.commands:build_command` in the product repo.