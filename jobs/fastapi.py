"""Async lifespan helper for opening the Procrastinate connector inside FastAPI."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import procrastinate


@asynccontextmanager
async def open_jobs(app: procrastinate.App) -> AsyncGenerator[None, None]:
    """Open the Procrastinate connector for **deferral only** (no worker).

    Usage inside a FastAPI lifespan::

        @asynccontextmanager
        async def lifespan(_: FastAPI):
            from vendor.jobs.fastapi import open_jobs
            async with open_jobs(my_procrastinate_app):
                yield
    """
    async with app.open_async():
        yield
