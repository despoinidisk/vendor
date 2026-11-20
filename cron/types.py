from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModuleJob:
    """Run ``python -m <module> [args…]`` on schedule (UTC cron syntax)."""

    job_id: str
    schedule: str
    module: str
    description: str
    args: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ScriptJob:
    """Run ``python`` with a fixed argv tail (script path and CLI flags)."""

    job_id: str
    schedule: str
    description: str
    argv: tuple[str, ...]
    aliases: tuple[str, ...] = ()