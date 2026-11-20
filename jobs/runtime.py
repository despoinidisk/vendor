"""Runtime paths for the jobs worker daemon (portable, no domain imports)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from vendor.paths import repo_root


def state_dir() -> Path:
    """Return the directory for worker PID/log files."""
    explicit = os.getenv("JOBS_STATE_DIR")
    if explicit:
        return Path(explicit)
    sub = os.getenv("JOBS_STATE_SUBDIR", ".vendor-state/jobs")
    directory = repo_root(prefix="JOBS") / sub
    directory.mkdir(parents=True, exist_ok=True)
    return directory


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
    return WorkerPaths(pid_path=directory / "jobs.pid", log_path=directory / "jobs.log")