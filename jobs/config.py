"""Resolve the Procrastinate database DSN from environment variables."""

from __future__ import annotations

import os

from vendor.jobs.dsn import normalise_dsn


def get_jobs_dsn() -> str:
    """Return a Psycopg-compatible ``postgresql://…`` connection string.

    Reads ``JOBS_DATABASE_URL`` first; falls back to ``DATABASE_URL``.
    """
    raw = os.getenv("JOBS_DATABASE_URL") or os.getenv("DATABASE_URL", "")
    if not raw:
        raise RuntimeError(
            "Neither JOBS_DATABASE_URL nor DATABASE_URL is set. "
            "Set one of them to a postgresql://… connection string."
        )
    return normalise_dsn(raw)
