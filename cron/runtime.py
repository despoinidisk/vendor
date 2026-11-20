"""Runtime paths for the cron scheduler daemon (portable, no domain imports)."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from vendor.paths import repo_root


def state_dir() -> Path:
    explicit = os.getenv("CRON_STATE_DIR")
    if explicit:
        return Path(explicit)
    sub = os.getenv("CRON_STATE_SUBDIR", ".vendor-state/cron")
    directory = repo_root(prefix="CRON") / sub
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def poll_interval_seconds() -> float:
    return max(5.0, float(os.getenv("CRON_POLL_SECONDS", "30")))


def timezone_name() -> str:
    return os.getenv("CRON_TZ", "UTC")


@dataclass(frozen=True, slots=True)
class CronPaths:
    root: Path
    python: Path
    pid_path: Path
    log_path: Path


def resolve_cron_paths(python: str | None = None) -> CronPaths:
    root = repo_root(prefix="CRON")
    default_python = root / ".venv" / "bin" / "python"
    interpreter = Path(python) if python else Path(os.environ.get("CRON_PYTHON", default_python))
    if not interpreter.is_file():
        interpreter = Path(sys.executable)

    directory = state_dir()
    return CronPaths(
        root=root,
        python=interpreter,
        pid_path=directory / "cron.pid",
        log_path=directory / "cron.log",
    )