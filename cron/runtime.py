"""Runtime paths for the cron scheduler daemon (portable, no domain imports)."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


def repo_root() -> Path:
    for key in (
        "CRON_REPO_ROOT",
        "GEOTWIN_ROOT",
        "AQUAGUARD_ROOT",
        "AILIFT_ROOT",
        "PERTOURISM_ROOT",
    ):
        value = os.getenv(key)
        if value:
            return Path(value)
    return Path.cwd()


def state_dir() -> Path:
    explicit = os.getenv("CRON_STATE_DIR")
    if explicit:
        return Path(explicit)
    name = os.getenv("CRON_STATE_NAME", ".geotwin")
    directory = repo_root() / name
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def pid_file() -> Path:
    return state_dir() / "cron.pid"


def log_file() -> Path:
    return state_dir() / "cron.log"


def poll_interval_seconds() -> float:
    raw = os.getenv("CRON_POLL_SECONDS", os.getenv("GEOTWIN_CRON_POLL_SECONDS", "30"))
    return max(5.0, float(raw))


def timezone_name() -> str:
    return os.getenv("CRON_TZ", os.getenv("GEOTWIN_CRON_TZ", "UTC"))


@dataclass(frozen=True, slots=True)
class CronPaths:
    root: Path
    python: Path
    pid_path: Path
    log_path: Path


def resolve_cron_paths(python: str | None = None) -> CronPaths:
    root = repo_root()
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