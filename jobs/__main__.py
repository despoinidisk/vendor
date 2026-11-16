"""Thin CLI for the portable jobs kit.

Usage::

    python -m vendor.jobs worker          # run worker in foreground
    python -m vendor.jobs start           # daemonize worker (background)
    python -m vendor.jobs stop            # stop background worker
    python -m vendor.jobs status          # show worker status (JSON)
    python -m vendor.jobs schema          # apply Procrastinate schema
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys


def _load_app() -> procrastinate.App:  # type: ignore[name-defined]
    """Load the twin-specific Procrastinate app from ``JOBS_APP``."""
    import procrastinate  # noqa: F811 – lazy to avoid import at module level

    entry = os.getenv("JOBS_APP", "tasks.app:app")
    module_path, attr = entry.split(":", 1)
    mod = importlib.import_module(module_path)
    obj = getattr(mod, attr)
    if isinstance(obj, procrastinate.App):
        return obj
    if callable(obj):
        loaded = obj()
        if isinstance(loaded, procrastinate.App):
            return loaded
    if hasattr(obj, "__class__") and obj.__class__.__name__ == "_AppProxy":
        return mod.get_app()
    raise TypeError(f"JOBS_APP entry {entry!r} did not resolve to a procrastinate.App")


def cmd_worker(args: argparse.Namespace) -> None:
    """Start the Procrastinate worker in the foreground."""
    app = _load_app()
    queues: list[str] = args.queues or []
    app.run_worker(queues=queues or None, concurrency=args.concurrency)


def cmd_start(args: argparse.Namespace) -> None:
    """Start the Procrastinate worker as a background daemon."""
    from vendor.jobs.daemon import WorkerError, start_worker

    try:
        start_worker(
            foreground=args.foreground,
            concurrency=args.concurrency,
            queues=args.queues or None,
        )
    except WorkerError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc


def cmd_stop(_: argparse.Namespace) -> None:
    """Stop the background worker."""
    from vendor.jobs.daemon import WorkerError, stop_worker

    try:
        stop_worker()
        print("Jobs worker stopped")
    except WorkerError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc


def cmd_status(_: argparse.Namespace) -> None:
    """Print worker status as JSON."""
    from vendor.jobs.daemon import worker_status

    print(json.dumps(worker_status(), indent=2))


def cmd_schema(_: argparse.Namespace) -> None:
    """Apply the Procrastinate schema."""
    from vendor.jobs.schema import apply_schema

    app = _load_app()
    apply_schema(app)
    print("Procrastinate schema applied.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m vendor.jobs",
        description="Portable Procrastinate job-queue CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    worker = sub.add_parser("worker", help="Run the Procrastinate worker in the foreground")
    worker.add_argument("-q", "--queues", nargs="*", default=[], help="Queues to consume (default: all)")
    worker.add_argument("-c", "--concurrency", type=int, default=1, help="Worker concurrency")

    start = sub.add_parser("start", help="Start the worker in the background")
    start.add_argument(
        "--foreground",
        action="store_true",
        help="Stay attached to the terminal (do not daemonize)",
    )
    start.add_argument("-q", "--queues", nargs="*", default=[], help="Queues to consume (default: all)")
    start.add_argument("-c", "--concurrency", type=int, default=1, help="Worker concurrency")

    sub.add_parser("stop", help="Stop the background worker")
    sub.add_parser("status", help="Show worker status (JSON)")
    sub.add_parser("schema", help="Apply Procrastinate schema to the database")

    args = parser.parse_args()
    {
        "worker": cmd_worker,
        "start": cmd_start,
        "stop": cmd_stop,
        "status": cmd_status,
        "schema": cmd_schema,
    }[args.command](args)


if __name__ == "__main__":
    main()
