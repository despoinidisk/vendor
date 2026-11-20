from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from vendor.cron.types import ModuleJob, ScriptJob


def module_command(python: Path, job: ModuleJob) -> list[str]:
    return [str(python), "-m", job.module, *job.args]


def script_command(python: Path, job: ScriptJob) -> list[str]:
    return [str(python), *job.argv]


def command_for(job: Any, *, python: Path) -> list[str]:
    if isinstance(job, ModuleJob):
        return module_command(python, job)
    if isinstance(job, ScriptJob):
        return script_command(python, job)
    if hasattr(job, "module"):
        return module_command(
            python,
            ModuleJob(
                job_id=job.job_id,
                schedule=job.schedule,
                module=job.module,
                description=job.description,
                args=tuple(getattr(job, "args", ()) or ()),
                aliases=tuple(getattr(job, "aliases", ()) or ()),
            ),
        )
    if hasattr(job, "argv"):
        return script_command(
            python,
            ScriptJob(
                job_id=job.job_id,
                schedule=job.schedule,
                description=job.description,
                argv=tuple(job.argv),
                aliases=tuple(getattr(job, "aliases", ()) or ()),
            ),
        )
    raise TypeError(
        f"Unsupported job type for {getattr(job, 'job_id', job)!r}. "
        "Use ModuleJob, ScriptJob, or set CRON_COMMAND_BUILDER.",
    )


def load_command_builder(entry: str | None) -> Callable[[Any, Path], list[str]] | None:
    if not entry:
        return None
    module_path, attr = entry.split(":", 1)
    import importlib

    mod = importlib.import_module(module_path)
    builder = getattr(mod, attr)
    if not callable(builder):
        raise TypeError(f"CRON_COMMAND_BUILDER {entry!r} is not callable")

    def _wrap(job: Any, python: Path) -> list[str]:
        result = builder(job, python)
        if not isinstance(result, list):
            raise TypeError(f"Command builder must return list[str], got {type(result)}")
        return result

    return _wrap