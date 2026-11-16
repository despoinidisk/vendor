from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from vendor.cron.types import GdprJob, IngestionJob, ModuleJob


def module_command(python: Path, job: ModuleJob) -> list[str]:
    return [str(python), "-m", job.module, *job.args]


def ingestion_command(python: Path, job: IngestionJob) -> list[str]:
    if job.runner == "ml":
        return [str(python), "-m", "ml", job.graph, *job.args]
    if job.runner == "report":
        return [str(python), "-m", "reports", job.graph, *job.args]
    return [str(python), "-m", "pipelines.run", job.graph]


def gdpr_command(python: Path, job: GdprJob, *, script: Path) -> list[str]:
    return [str(python), str(script)]


def command_for(job: Any, *, python: Path, gdpr_script: Path | None = None) -> list[str]:
    if isinstance(job, ModuleJob):
        return module_command(python, job)
    if isinstance(job, IngestionJob):
        return ingestion_command(python, job)
    if isinstance(job, GdprJob):
        if gdpr_script is None:
            raise ValueError(f"GdprJob {job.job_id} requires gdpr_script")
        return gdpr_command(python, job, script=gdpr_script)
    if hasattr(job, "module"):
        return module_command(
            python,
            ModuleJob(
                job_id=job.job_id,
                schedule=job.schedule,
                module=job.module,
                description=job.description,
                args=tuple(getattr(job, "args", ()) or ()),
            ),
        )
    if hasattr(job, "graph"):
        return ingestion_command(python, job)
    raise TypeError(f"Do not know how to build a command for job {getattr(job, 'job_id', job)!r}")


def load_command_builder(entry: str | None) -> Callable[[Any, Path, Path | None], list[str]] | None:
    if not entry:
        return None
    module_path, attr = entry.split(":", 1)
    import importlib

    mod = importlib.import_module(module_path)
    builder = getattr(mod, attr)
    if not callable(builder):
        raise TypeError(f"CRON_COMMAND_BUILDER {entry!r} is not callable")

    def _wrap(job: Any, python: Path, gdpr_script: Path | None) -> list[str]:
        result = builder(job, python, gdpr_script)
        if not isinstance(result, list):
            raise TypeError(f"Command builder must return list[str], got {type(result)}")
        return result

    return _wrap