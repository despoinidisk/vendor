from __future__ import annotations

import os
from collections.abc import Callable, Iterable
from pathlib import Path


def load_env_file(root: Path) -> dict[str, str]:
    """Load KEY=VALUE pairs from the repo ``.env`` for subprocess inheritance."""
    env_path = root / ".env"
    if not env_path.is_file():
        return {}

    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def build_pythonpath(root: Path, *, extra: Iterable[str] = ()) -> str:
    entries = [str(root), *extra]
    existing = os.environ.get("PYTHONPATH", "")
    if existing:
        entries.append(existing)
    return ":".join(entries)


def _rewrite_compose_hosts(env: dict[str, str]) -> None:
    """When the daemon runs on the host, map Compose service names to localhost."""
    if env.get("DATABASE_URL", "").find("@postgres:") >= 0:
        env["DATABASE_URL"] = env["DATABASE_URL"].replace("@postgres:", "@localhost:")
    if env.get("GARAGE_S3_ENDPOINT", "").find("//garage:") >= 0:
        env["GARAGE_S3_ENDPOINT"] = env["GARAGE_S3_ENDPOINT"].replace("//garage:", "//localhost:")
    if env.get("SCORPIO_URL", "").find("//scorpio:") >= 0:
        env["SCORPIO_URL"] = env["SCORPIO_URL"].replace("//scorpio:", "//localhost:")


def runtime_env(
    root: Path,
    *,
    extra_pythonpath: Iterable[str] = (),
    root_env_var: str | None = None,
    rewrite_compose_hosts: bool | None = None,
    mutator: Callable[[dict[str, str]], None] | None = None,
) -> dict[str, str]:
    env = os.environ.copy()
    env.update(load_env_file(root))
    if root_env_var:
        env[root_env_var] = str(root)
    env["PYTHONPATH"] = build_pythonpath(root, extra=extra_pythonpath)

    if rewrite_compose_hosts is None:
        rewrite_compose_hosts = os.getenv("CRON_REWRITE_COMPOSE_HOSTS", "1") == "1"
    if rewrite_compose_hosts:
        _rewrite_compose_hosts(env)

    if mutator is not None:
        mutator(env)
    return env