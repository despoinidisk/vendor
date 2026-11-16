# jobs — portable Procrastinate job-queue kit

Zero-domain-imports package that wraps [Procrastinate](https://procrastinate.readthedocs.io/) for Postgres-backed async job deferral. Copy `vendor/jobs/` with the rest of `vendor/` into any FastAPI twin repo (e.g. Aquaguard).

## Quick start (vendor)

```bash
# 1. Copy vendor/ into your twin repo root
cp -r /path/to/GeoTwin-ELBG/vendor ./vendor

# 2. Add dependencies
echo "-r vendor/jobs/requirements.txt" >> requirements.txt

# 3. Create your tasks/ package (see tasks/README or tasks/ in GeoTwin)
export JOBS_APP=tasks.app:app

# 4. Apply schema once
python -m vendor.jobs schema
# or via make migrate (Alembic revision applies Procrastinate DDL)

# 5. Open connector in FastAPI lifespan
from vendor.jobs.fastapi import open_jobs
from vendor.jobs.factory import create_app

# 6. Start the worker host process
python -m vendor.jobs start          # background (pid/log under .geotwin/)
python -m vendor.jobs worker         # foreground
python -m vendor.jobs status         # JSON status
```

## Package layout

| File | Role |
|------|------|
| `config.py` | Read `JOBS_DATABASE_URL` or fall back to `DATABASE_URL` |
| `dsn.py` | Normalize `postgresql+asyncpg://…` → `postgresql://…` for Psycopg |
| `factory.py` | `create_app(*, blueprints=(), import_paths=(), connector=None) -> App` |
| `fastapi.py` | Async lifespan helper: `async with app.open_async(): yield` (defer only) |
| `schema.py` | `apply_schema(app)` wrapping Procrastinate schema apply for migrations/CLI |
| `__main__.py` | Thin CLI: `python -m vendor.jobs worker` / `start` / `stop` / `status` / `schema` |
| `requirements.txt` | `procrastinate` + `psycopg[binary]` |

## Hard rule

`vendor/jobs/` must **not** import `ml`, `rest`, `broker`, `db` models, or any twin domain code.

## Transfer checklist

1. Copy `vendor/` into Aquaguard repo root.
2. Add `-r vendor/jobs/requirements.txt` to Aquaguard's install path.
3. Create Aquaguard `tasks/` with its blueprints; set `JOBS_APP=tasks.app:app`.
4. Apply schema once (`make migrate` or `python -m vendor.jobs schema`).
5. Open app in FastAPI lifespan; run `python -m vendor.jobs worker` as a host process.
6. Defer only serializable args; keep domain persistence in Aquaguard's own tables.