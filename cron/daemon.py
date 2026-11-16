from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from vendor.cron.env import runtime_env
from vendor.cron.registry import CronRegistry, all_jobs, resolve_command
from vendor.cron.runtime import CronPaths, poll_interval_seconds, resolve_cron_paths, state_dir
from vendor.cron.timing import is_due, next_run

logger = logging.getLogger(__name__)


class SchedulerError(Exception):
    pass


def read_pid(pid_path: Path) -> int | None:
    if not pid_path.is_file():
        return None
    try:
        return int(pid_path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def write_pid(pid_path: Path) -> None:
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    pid_path.write_text(str(os.getpid()), encoding="utf-8")


def remove_pid(pid_path: Path) -> None:
    if pid_path.is_file():
        pid_path.unlink()


def _configure_logging(log_path: Path, *, foreground: bool) -> None:
    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout if foreground else open(log_path, "a", encoding="utf-8")),
    ]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
        force=True,
    )


def daemonize(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if os.fork() > 0:
        raise SystemExit(0)

    os.setsid()

    if os.fork() > 0:
        raise SystemExit(0)

    with open(log_path, "a", encoding="utf-8") as log_handle:
        os.dup2(log_handle.fileno(), sys.stdout.fileno())
        os.dup2(log_handle.fileno(), sys.stderr.fileno())

    os.chdir("/")
    os.umask(0o022)


def build_runtime_env(paths: CronPaths) -> dict[str, str]:
    extra = os.getenv("CRON_PYTHONPATH_EXTRA", "")
    extra_parts = [part for part in extra.split(":") if part]
    root_var = os.getenv("CRON_ROOT_ENV_VAR")
    return runtime_env(
        paths.root,
        extra_pythonpath=extra_parts,
        root_env_var=root_var,
    )


class SubprocessScheduler:
    def __init__(
        self,
        paths: CronPaths,
        registry: CronRegistry,
        *,
        command_builder: Callable[[Any, Path, Path | None], list[str]] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        self.paths = paths
        self.registry = registry
        self.command_builder = command_builder
        self.env = env or build_runtime_env(paths)
        self.last_run: dict[str, datetime] = {}
        self.running: dict[str, subprocess.Popen[bytes]] = {}
        self._initialized = False

    def _init_last_run(self, now: datetime) -> None:
        if self._initialized:
            return
        for job in all_jobs(self.registry):
            self.last_run[job.job_id] = now
        self._initialized = True
        logger.info("Scheduler armed; next runs will follow cron expressions (UTC)")

    def _reap_finished(self) -> None:
        finished: list[str] = []
        for job_id, process in self.running.items():
            code = process.poll()
            if code is None:
                continue
            finished.append(job_id)
            if code == 0:
                logger.info("Job %s finished successfully", job_id)
            else:
                logger.error("Job %s failed with exit code %s", job_id, code)

        for job_id in finished:
            self.running.pop(job_id, None)

    def _command(self, job: Any) -> list[str]:
        return resolve_command(
            job,
            python=self.paths.python,
            registry=self.registry,
            custom_builder=self.command_builder,
        )

    def _start(self, job: Any) -> None:
        job_id = job.job_id
        if job_id in self.running:
            logger.warning("Skipping %s — previous run still in progress", job_id)
            return

        logger.info("Starting job %s", job_id)
        log_handle = open(self.paths.log_path, "a", encoding="utf-8")
        process = subprocess.Popen(
            self._command(job),
            cwd=self.paths.root,
            env=self.env,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
        )
        self.running[job_id] = process
        self.last_run[job_id] = datetime.now(UTC)

    def tick(self, now: datetime | None = None) -> None:
        current = now or datetime.now(UTC)
        self._init_last_run(current)
        self._reap_finished()

        for job in all_jobs(self.registry):
            last = self.last_run.get(job.job_id)
            if last is None or not is_due(job.schedule, now=current, last_run=last):
                continue
            self._start(job)

    def run_once(self, job: Any) -> int:
        logger.info("Running job once: %s", job.job_id)
        completed = subprocess.run(
            self._command(job),
            cwd=self.paths.root,
            env=self.env,
            check=False,
        )
        return completed.returncode

    def run_forever(self) -> None:
        jobs = all_jobs(self.registry)
        logger.info(
            "Cron scheduler started (poll=%ss, jobs=%s)",
            poll_interval_seconds(),
            len(jobs),
        )
        for job in jobs:
            logger.info(
                "  %-16s %-18s — %s",
                job.job_id,
                job.schedule,
                job.description,
            )

        stop = False

        def handle_stop(signum: int, _frame: object) -> None:
            nonlocal stop
            logger.info("Received signal %s, shutting down", signum)
            stop = True

        signal.signal(signal.SIGTERM, handle_stop)
        signal.signal(signal.SIGINT, handle_stop)

        while not stop:
            self.tick()
            time.sleep(poll_interval_seconds())

        for job_id, process in list(self.running.items()):
            logger.info("Terminating in-flight job %s", job_id)
            process.terminate()

        logger.info("Scheduler stopped")


def start_scheduler(
    registry: CronRegistry,
    *,
    foreground: bool,
    python: str | None = None,
    command_builder: Callable[[Any, Path, Path | None], list[str]] | None = None,
    banner: str = "cron",
) -> None:
    paths = resolve_cron_paths(python)
    existing_pid = read_pid(paths.pid_path)
    if existing_pid is not None and is_running(existing_pid):
        raise SchedulerError(
            f"Scheduler already running (pid {existing_pid}). "
            "Stop it with: python -m vendor.cron stop",
        )

    if existing_pid is not None:
        remove_pid(paths.pid_path)

    if not foreground:
        paths.log_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Starting {banner} scheduler in background (log: {paths.log_path})", flush=True)
        daemonize(paths.log_path)

    _configure_logging(paths.log_path, foreground=foreground)
    write_pid(paths.pid_path)

    try:
        SubprocessScheduler(paths, registry, command_builder=command_builder).run_forever()
    finally:
        remove_pid(paths.pid_path)


def stop_scheduler() -> None:
    paths = resolve_cron_paths()
    pid = read_pid(paths.pid_path)
    if pid is None:
        raise SchedulerError("Scheduler is not running (no pid file)")

    if not is_running(pid):
        remove_pid(paths.pid_path)
        raise SchedulerError(f"Scheduler is not running (stale pid {pid})")

    os.kill(pid, signal.SIGTERM)

    deadline = time.time() + 10
    while time.time() < deadline:
        if not is_running(pid):
            remove_pid(paths.pid_path)
            return
        time.sleep(0.2)

    os.kill(pid, signal.SIGKILL)
    remove_pid(paths.pid_path)


def scheduler_status(registry: CronRegistry) -> dict[str, object]:
    paths = resolve_cron_paths()
    pid = read_pid(paths.pid_path)
    running = pid is not None and is_running(pid)
    now = datetime.now(UTC)

    payload_jobs: list[dict[str, object]] = []
    for job in registry.jobs:
        entry: dict[str, object] = {
            "job_id": job.job_id,
            "kind": "job",
            "schedule": job.schedule,
            "description": job.description,
            "next_run": next_run(job.schedule, after=now).isoformat(),
            "last_run": None,
        }
        if getattr(job, "graph", None):
            entry["graph"] = job.graph
            entry["kind"] = "ingestion"
        if getattr(job, "module", None):
            entry["module"] = job.module
        payload_jobs.append(entry)

    for job in registry.gdpr_jobs:
        payload_jobs.append(
            {
                "job_id": job.job_id,
                "kind": "gdpr",
                "schedule": job.schedule,
                "description": job.description,
                "next_run": next_run(job.schedule, after=now).isoformat(),
                "last_run": None,
            },
        )

    return {
        "running": running,
        "pid": pid if running else None,
        "log_file": str(paths.log_path),
        "state_dir": str(state_dir()),
        "poll_seconds": poll_interval_seconds(),
        "timezone": "UTC",
        "jobs": payload_jobs,
    }