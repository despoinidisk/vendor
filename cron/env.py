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


def apply_substring_rewrites(env: dict[str, str]) -> None:
    """Apply ``CRON_ENV_SUBSTRING_REWRITES`` (comma-separated ``needle>>replacement``)."""
    spec = os.getenv("CRON_ENV_SUBSTRING_REWRITES", "")
    if not spec:
        return
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk or ">>" not in chunk:
            continue
        needle, replacement = chunk.split(">>", 1)
        if not needle:
            continue
        for key, value in list(env.items()):
            if needle in value:
                env[key] = value.replace(needle, replacement)


def runtime_env(
    root: Path,
    *,
    extra_pythonpath: Iterable[str] = (),
    repo_env_key: str | None = None,
    mutator: Callable[[dict[str, str]], None] | None = None,
) -> dict[str, str]:
    env = os.environ.copy()
    env.update(load_env_file(root))
    if repo_env_key:
        env[repo_env_key] = str(root)
    env["REPO_ROOT"] = str(root)
    env["PYTHONPATH"] = build_pythonpath(root, extra=extra_pythonpath)

    apply_substring_rewrites(env)

    hook = os.getenv("CRON_RUNTIME_ENV_HOOK")
    if hook:
        module_path, attr = hook.split(":", 1)
        import importlib

        fn = getattr(importlib.import_module(module_path), attr)
        if not callable(fn):
            raise TypeError(f"CRON_RUNTIME_ENV_HOOK {hook!r} is not callable")
        fn(env)

    if mutator is not None:
        mutator(env)
    return env