"""Background worker daemon helpers (start / stop / status)."""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
from typing import Any

from vendor.jobs.runtime import WorkerPaths, resolve_worker_paths

logger = logging.getLogger(__name__)


class WorkerError(Exception):
    pass


def read_pid(pid_path: os.PathLike[str] | str) -> int | None:
    path = os.fspath(pid_path)
    if not os.path.isfile(path):
        return None
    try:
        return int(open(path, encoding="utf-8").read().strip())
    except ValueError:
        return None


def is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def write_pid(pid_path: os.PathLike[str] | str) -> None:
    path = os.fspath(pid_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(str(os.getpid()))


def remove_pid(pid_path: os.PathLike[str] | str) -> None:
    path = os.fspath(pid_path)
    if os.path.isfile(path):
        os.unlink(path)


def _configure_logging(log_path: os.PathLike[str] | str, *, foreground: bool) -> None:
    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout if foreground else open(log_path, "a", encoding="utf-8"))
    ]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
        force=True,
    )


def _daemonize(log_path: os.PathLike[str] | str) -> None:
    log = os.fspath(log_path)
    os.makedirs(os.path.dirname(log), exist_ok=True)

    if os.fork() > 0:
        raise SystemExit(0)

    os.setsid()

    if os.fork() > 0:
        raise SystemExit(0)

    with open(log, "a", encoding="utf-8") as log_handle:
        os.dup2(log_handle.fileno(), sys.stdout.fileno())
        os.dup2(log_handle.fileno(), sys.stderr.fileno())

    os.chdir("/")
    os.umask(0o022)


def _run_worker(*, concurrency: int = 1, queues: list[str] | None = None) -> None:
    from vendor.jobs.__main__ import _load_app

    app = _load_app()
    app.run_worker(queues=queues or None, concurrency=concurrency)


def start_worker(
    *,
    foreground: bool = False,
    concurrency: int = 1,
    queues: list[str] | None = None,
) -> None:
    paths = resolve_worker_paths()
    existing_pid = read_pid(paths.pid_path)
    if existing_pid is not None and is_running(existing_pid):
        raise WorkerError(
            f"Jobs worker already running (pid {existing_pid}). "
            "Stop it with: python -m vendor.jobs stop",
        )

    if existing_pid is not None:
        remove_pid(paths.pid_path)

    if not foreground:
        print(f"Starting jobs worker in background (log: {paths.log_path})")
        _daemonize(paths.log_path)

    _configure_logging(paths.log_path, foreground=foreground)
    write_pid(paths.pid_path)

    try:
        logger.info("Jobs worker starting (concurrency=%s)", concurrency)
        _run_worker(concurrency=concurrency, queues=queues)
    finally:
        remove_pid(paths.pid_path)


def stop_worker() -> None:
    paths = resolve_worker_paths()
    pid = read_pid(paths.pid_path)
    if pid is None:
        raise WorkerError("Jobs worker is not running (no pid file)")

    if not is_running(pid):
        remove_pid(paths.pid_path)
        raise WorkerError(f"Jobs worker is not running (stale pid {pid})")

    os.kill(pid, signal.SIGTERM)

    deadline = time.time() + 10
    while time.time() < deadline:
        if not is_running(pid):
            remove_pid(paths.pid_path)
            return
        time.sleep(0.2)

    os.kill(pid, signal.SIGKILL)
    remove_pid(paths.pid_path)


def worker_status() -> dict[str, Any]:
    paths = resolve_worker_paths()
    pid = read_pid(paths.pid_path)
    running = pid is not None and is_running(pid)
    return {
        "running": running,
        "pid": pid if running else None,
        "log_file": str(paths.log_path),
        "state_dir": str(paths.pid_path.parent),
        "jobs_app": os.getenv("JOBS_APP", "tasks.app:app"),
    }
