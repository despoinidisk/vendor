from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from croniter import croniter


def validate_schedules(jobs: Iterable[object]) -> None:
    for job in jobs:
        schedule = getattr(job, "schedule", None)
        job_id = getattr(job, "job_id", repr(job))
        if not isinstance(schedule, str):
            raise TypeError(f"Job {job_id!r} has no string schedule")
        if not croniter.is_valid(schedule):
            raise ValueError(f"Invalid cron schedule for {job_id}: {schedule}")


def next_run(
    schedule: str,
    *,
    after: datetime | None = None,
) -> datetime:
    base = after or datetime.now(UTC)
    return croniter(schedule, base).get_next(datetime)


def is_due(
    schedule: str,
    *,
    now: datetime,
    last_run: datetime | None,
) -> bool:
    if last_run is None:
        return False
    return next_run(schedule, after=last_run) <= now