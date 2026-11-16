"""Runtime paths for the jobs worker daemon (portable, no domain imports)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def state_dir() -> Path:
    """Return the directory for worker PID/log files."""
    explicit = os.getenv("JOBS_STATE_DIR")
    if explicit:
        return Path(explicit)
    root = os.getenv("GEOTWIN_ROOT", os.getcwd())
    return Path(root) / ".geotwin"


def pid_file() -> Path:
    return state_dir() / "jobs.pid"


def log_file() -> Path:
    return state_dir() / "jobs.log"


@dataclass(frozen=True, slots=True)
class WorkerPaths:
    pid_path: Path
    log_path: Path


def resolve_worker_paths() -> WorkerPaths:
    directory = state_dir()
    directory.mkdir(parents=True, exist_ok=True)
    return WorkerPaths(pid_path=pid_file(), log_path=log_file())
