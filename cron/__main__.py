"""CLI for the portable cron scheduler kit.

Usage::

    python -m vendor.cron start
    python -m vendor.cron stop
    python -m vendor.cron status
    python -m vendor.cron list
    python -m vendor.cron run-now JOB_ID
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime

from vendor.cron.daemon import (
    SchedulerError,
    SubprocessScheduler,
    scheduler_status,
    start_scheduler,
    stop_scheduler,
)
from vendor.cron.registry import (
    all_jobs,
    find_job,
    load_command_builder_from_env,
    load_registry,
)
from vendor.cron.runtime import resolve_cron_paths
from vendor.cron.timing import next_run, validate_schedules


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m vendor.cron",
        description="Portable UTC cron scheduler for subprocess jobs",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="Start the scheduler in the background")
    start.add_argument(
        "--foreground",
        action="store_true",
        help="Stay attached to the terminal (do not daemonize)",
    )
    start.add_argument(
        "--python",
        help="Python interpreter for job subprocesses (default: .venv/bin/python)",
    )

    subparsers.add_parser("stop", help="Stop the background scheduler")
    subparsers.add_parser("status", help="Show scheduler status and upcoming runs")
    subparsers.add_parser("list", help="List configured jobs")

    run_now = subparsers.add_parser("run-now", help="Run one job immediately")
    run_now.add_argument("target", help="Job id (or graph / module alias where supported)")

    return parser


def _cmd_list(registry) -> int:
    now = datetime.now(UTC)
    for job in all_jobs(registry):
        nxt = next_run(job.schedule, after=now)
        print(f"{job.job_id:16} {job.schedule:18} next={nxt.isoformat()}  {job.description}")
    return 0


def _cmd_status(registry) -> int:
    print(json.dumps(scheduler_status(registry), indent=2))
    return 0


def _cmd_run_now(registry, target: str) -> int:
    job = find_job(registry, target)
    if job is None:
        print(f"Unknown job: {target}", file=sys.stderr)
        print("Use `python -m vendor.cron list` to see options.", file=sys.stderr)
        return 1

    paths = resolve_cron_paths()
    builder = load_command_builder_from_env()
    scheduler = SubprocessScheduler(paths, registry, command_builder=builder)
    return scheduler.run_once(job)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    registry = load_registry()
    jobs = all_jobs(registry)
    if not jobs:
        print(
            "No cron jobs configured. Set CRON_JOBS or add SCHEDULED_JOBS / INGESTION_JOBS to cron.schedules.",
            file=sys.stderr,
        )
        return 1

    try:
        validate_schedules(jobs)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    builder = load_command_builder_from_env()
    banner = os.getenv("CRON_BANNER", "cron")

    try:
        if args.command == "start":
            start_scheduler(
                registry,
                foreground=args.foreground,
                python=args.python,
                command_builder=builder,
                banner=banner,
            )
            return 0
        if args.command == "stop":
            stop_scheduler()
            print("Scheduler stopped")
            return 0
        if args.command == "status":
            return _cmd_status(registry)
        if args.command == "list":
            return _cmd_list(registry)
        if args.command == "run-now":
            return _cmd_run_now(registry, args.target)
    except SchedulerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())