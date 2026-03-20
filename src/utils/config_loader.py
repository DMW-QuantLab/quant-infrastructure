"""
Config loader — reads YAML config files and merges with .env overrides.
All secrets must come from environment variables, never from YAML.
"""
from __future__ import annotations
import os
from pathlib import Path
import yaml


def load_config(path: str | Path) -> dict:
    """Load a YAML config file. Returns empty dict if file does not exist."""
    p = Path(path)
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text()) or {}


def require_env(key: str) -> str:
    """
    Read a required secret from environment.
    Raises immediately if missing — never silently returns None for secrets.
    """
    val = os.environ.get(key)
    if not val:
        raise RuntimeError(
            f"Required environment variable {key!r} is not set. "
            f"Add it to your .env file (local) or GitHub Secrets (CI)."
        )
    return val

