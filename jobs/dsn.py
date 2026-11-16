"""Normalise a SQLAlchemy-style PostgreSQL URL to a plain Psycopg DSN."""

from __future__ import annotations


def normalise_dsn(url: str) -> str:
    """Convert ``postgresql+asyncpg://…`` (or ``postgresql+psycopg://…``) to ``postgresql://…``.

    Procrastinate uses Psycopg (psycopg3) under the hood, which expects a plain
    ``postgresql://`` scheme.  The SQLAlchemy ``+driver`` suffix must be stripped.
    """
    for driver in ("+asyncpg", "+psycopg", "+psycopg2", "+aiopg"):
        if url.startswith(f"postgresql{driver}://"):
            return url.replace(f"postgresql{driver}://", "postgresql://", 1)
    return url
