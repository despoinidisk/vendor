"""Apply the Procrastinate schema to the target database."""

from __future__ import annotations

import procrastinate
from procrastinate.schema import SchemaManager


def apply_schema(app: procrastinate.App | None = None) -> str:
    """Create Procrastinate's tables (``procrastinate_*``) if they do not exist.

    Uses Procrastinate's connector so multi-statement schema SQL is applied
    safely (unlike a single ``op.execute()`` under asyncpg).
    """
    sql = SchemaManager.get_schema()
    if app is not None:
        with app.open():
            SchemaManager(app.connector).apply_schema()
    return sql
