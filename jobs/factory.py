"""Create a Procrastinate ``App`` with optional blueprints and import paths."""

from __future__ import annotations

from typing import Any, Sequence, TypeAlias

import procrastinate

BlueprintRegistration: TypeAlias = procrastinate.Blueprint | tuple[procrastinate.Blueprint, str]


def create_app(
    *,
    blueprints: Sequence[BlueprintRegistration] = (),
    import_paths: Sequence[str] = (),
    connector: Any | None = None,
) -> procrastinate.App:
    """Build a :class:`procrastinate.App` ready for deferral.

    Parameters
    ----------
    blueprints:
        :class:`procrastinate.Blueprint` instances, optionally paired with a
        namespace string for :meth:`procrastinate.App.add_tasks_from`.
    import_paths:
        Python dotted paths to modules that register tasks. Procrastinate imports
        them at worker start-up so tasks are discoverable.
    connector:
        Override the database connector (useful for testing). When *None* the
        default Psycopg connector is created from :func:`jobs.config.get_jobs_dsn`.
    """
    if connector is None:
        from vendor.jobs.config import get_jobs_dsn

        connector = procrastinate.PsycopgConnector(conninfo=get_jobs_dsn())

    paths = list(import_paths) or None
    app = procrastinate.App(connector=connector, import_paths=paths)

    for item in blueprints:
        if isinstance(item, tuple):
            blueprint, namespace = item
        else:
            blueprint, namespace = item, item.name
        app.add_tasks_from(blueprint, namespace=namespace)

    return app
