# jobs — portable Procrastinate job-queue kit

Zero-domain-imports package that wraps [Procrastinate](https://procrastinate.readthedocs.io/) for Postgres-backed async job deferral. Copy `vendor/` into any repo with a `tasks/` (or similar) app.

## Quick start

```bash
echo "-r vendor/jobs/requirements.txt" >> requirements.txt
export JOBS_APP=tasks.app:app
export REPO_ROOT=/path/to/repo   # optional; defaults to cwd

python -m vendor.jobs schema
python -m vendor.jobs start      # background
python -m vendor.jobs worker     # foreground
python -m vendor.jobs status
```

## Runtime paths

| Variable | Default |
| --- | --- |
| `JOBS_STATE_DIR` | — (absolute override) |
| `JOBS_STATE_SUBDIR` | `.vendor-state/jobs` under repo root |
| `JOBS_REPO_ROOT` / `REPO_ROOT` | `cwd` |

## Package layout

| File | Role |
|------|------|
| `config.py` | Read `JOBS_DATABASE_URL` or fall back to `DATABASE_URL` |
| `dsn.py` | Normalize `postgresql+asyncpg://…` → `postgresql://…` for Psycopg |
| `factory.py` | `create_app(*, blueprints=(), import_paths=(), connector=None) -> App` |
| `fastapi.py` | Async lifespan helper: `async with app.open_async(): yield` (defer only) |
| `schema.py` | `apply_schema(app)` wrapping Procrastinate schema apply |
| `__main__.py` | CLI: `worker` / `start` / `stop` / `status` / `schema` |

## Hard rule

`vendor/jobs/` must **not** import application domain code (`rest`, `db` models, etc.).