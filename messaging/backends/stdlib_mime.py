"""Load stdlib ``email.message.EmailMessage`` without importing the top-level ``email`` package."""

from __future__ import annotations

import importlib.util
import os
import sysconfig
from functools import lru_cache
from typing import Any, cast


@lru_cache
def stdlib_email_message_class() -> type[Any]:
    stdlib = sysconfig.get_path("stdlib")
    path = os.path.join(stdlib, "email", "message.py")
    spec = importlib.util.spec_from_file_location("_stdlib_email_message", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load stdlib email.message from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return cast(type[Any], mod.EmailMessage)