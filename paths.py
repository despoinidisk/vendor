"""Shared path helpers for portable vendor kits (no product imports)."""

from __future__ import annotations

import os
from pathlib import Path


def repo_root(*, prefix: str) -> Path:
    """Resolve repository root from ``{PREFIX}_REPO_ROOT`` or ``REPO_ROOT``."""
    dedicated = os.getenv(f"{prefix}_REPO_ROOT")
    if dedicated:
        return Path(dedicated)
    shared = os.getenv("REPO_ROOT")
    if shared:
        return Path(shared)
    return Path.cwd()