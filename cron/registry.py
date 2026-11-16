from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vendor.cron.commands import command_for, load_command_builder
from vendor.cron.runtime import repo_root
from vendor.cron.types import IngestionJob


@dataclass(frozen=True, slots=True)
class CronRegistry:
    jobs: tuple[Any, ...]
    gdpr_jobs: tuple[Any, ...]
    gdpr_script: str | None


def _load_attr(entry: str) -> Any:
    module_path, attr = entry.split(":", 1)
    mod = importlib.import_module(module_path)
    return getattr(mod, attr)


def _try_load_tuple(entry: str) -> tuple[Any, ...]:
    try:
        return tuple(_load_attr(entry))
    except (AttributeError, ModuleNotFoundError):
        return ()


def load_registry() -> CronRegistry:
    """Load job tuples from env (``CRON_JOBS``, or twin-style ingestion + GDPR lists)."""
    jobs_entry = os.getenv("CRON_JOBS")
    if jobs_entry:
        jobs = _try_load_tuple(jobs_entry)
    else:
        jobs = _try_load_tuple("cron.schedules:SCHEDULED_JOBS")
        if not jobs:
            ingestion_entry = os.getenv("CRON_INGESTION_JOBS", "cron.schedules:INGESTION_JOBS")
            jobs = _try_load_tuple(ingestion_entry)

    gdpr_entry = os.getenv("CRON_GDPR_JOBS")
    if gdpr_entry:
        gdpr_jobs = _try_load_tuple(gdpr_entry)
    else:
        gdpr_jobs = _try_load_tuple("cron.schedules:GDPR_JOBS")

    gdpr_script = os.getenv("CRON_GDPR_SCRIPT", "cron/gdpr_retention.py")
    return CronRegistry(jobs=jobs, gdpr_jobs=gdpr_jobs, gdpr_script=gdpr_script)


def gdpr_script_path(registry: CronRegistry) -> Path | None:
    if not registry.gdpr_script:
        return None
    path = Path(registry.gdpr_script)
    if path.is_absolute():
        return path
    return repo_root() / path


def resolve_command(
    job: Any,
    *,
    python: Path,
    registry: CronRegistry,
    custom_builder,
) -> list[str]:
    gdpr_path = gdpr_script_path(registry)
    if custom_builder is not None:
        return custom_builder(job, python, gdpr_path)
    if job in registry.gdpr_jobs:
        if gdpr_path is None:
            raise ValueError(f"GdprJob {job.job_id} requires CRON_GDPR_SCRIPT")
        from vendor.cron.commands import gdpr_command

        return gdpr_command(python, job, script=gdpr_path)
    return command_for(job, python=python, gdpr_script=gdpr_path)


def find_job(registry: CronRegistry, target: str) -> Any | None:
    for job in registry.jobs:
        if job.job_id == target:
            return job
        if isinstance(job, IngestionJob) and job.graph == target:
            return job
        if getattr(job, "module", None) == target:
            return job
    for job in registry.gdpr_jobs:
        if job.job_id == target:
            return job
    return None


def all_jobs(registry: CronRegistry) -> tuple[Any, ...]:
    return registry.jobs + registry.gdpr_jobs


def load_command_builder_from_env() -> Any:
    return load_command_builder(os.getenv("CRON_COMMAND_BUILDER"))