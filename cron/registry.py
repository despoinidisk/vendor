from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from typing import Any

from vendor.cron.commands import command_for, load_command_builder


@dataclass(frozen=True, slots=True)
class CronRegistry:
    jobs: tuple[Any, ...]


def _load_attr(entry: str) -> Any:
    module_path, attr = entry.split(":", 1)
    mod = importlib.import_module(module_path)
    return getattr(mod, attr)


def _try_load_tuple(entry: str) -> tuple[Any, ...]:
    try:
        return tuple(_load_attr(entry))
    except (AttributeError, ModuleNotFoundError, ValueError):
        return ()


def load_registry() -> CronRegistry:
    """Load the job tuple from ``CRON_JOBS`` (``module:ATTR``)."""
    entry = os.getenv("CRON_JOBS", "cron.schedules:JOBS")
    jobs = _try_load_tuple(entry)
    if not jobs and entry == "cron.schedules:JOBS":
        jobs = _try_load_tuple("cron.schedules:SCHEDULED_JOBS")

    extra = os.getenv("CRON_EXTRA_JOBS")
    if extra:
        jobs = jobs + _try_load_tuple(extra)

    return CronRegistry(jobs=jobs)


def resolve_command(
    job: Any,
    *,
    python,
    custom_builder,
) -> list[str]:
    if custom_builder is not None:
        return custom_builder(job, python)
    return command_for(job, python=python)


def find_job(registry: CronRegistry, target: str) -> Any | None:
    for job in registry.jobs:
        if job.job_id == target:
            return job
        aliases = getattr(job, "aliases", ()) or ()
        if target in aliases:
            return job
        for attr in ("module", "graph", "name"):
            if getattr(job, attr, None) == target:
                return job
    return None


def all_jobs(registry: CronRegistry) -> tuple[Any, ...]:
    return registry.jobs


def load_command_builder_from_env():
    return load_command_builder(os.getenv("CRON_COMMAND_BUILDER"))