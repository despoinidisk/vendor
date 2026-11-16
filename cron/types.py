from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Schedulable(Protocol):
    job_id: str
    schedule: str
    description: str


@dataclass(frozen=True, slots=True)
class ModuleJob:
    """Run ``python -m <module> [args…]`` on schedule (UTC cron syntax)."""

    job_id: str
    schedule: str
    module: str
    description: str
    args: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class IngestionJob:
    """Bonobo / twin ingestion graph (GeoTwin-style twins)."""

    job_id: str
    graph: str
    schedule: str
    source: str
    description: str
    runner: str = "pipeline"
    args: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GdprJob:
    job_id: str
    schedule: str
    description: str