"""Where EKSB keeps its own settings — separate from any workspace.

One small JSON file. Never holds secrets; never holds knowledge.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

APP = "eksb"
DEFAULTS = {"lang": None, "workspace": None, "onboarded": False}


def config_dir() -> Path:
    """Platform convention, no dependency. Overridable with EKSB_CONFIG_DIR."""
    env = os.environ.get("EKSB_CONFIG_DIR")
    if env:
        return Path(env)
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / APP


def config_file() -> Path:
    return config_dir() / "config.json"


def load() -> dict:
    cfg = dict(DEFAULTS)
    try:
        cfg.update(json.loads(config_file().read_text(encoding="utf-8")))
    except (OSError, ValueError):
        pass                     # missing or corrupt: fall back to defaults
    return cfg


def save(cfg: dict) -> Path:
    p = config_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return p


def set_(**kw) -> dict:
    cfg = load()
    cfg.update(kw)
    save(cfg)
    return cfg


def demo_dir() -> Path:
    """Where `eksb demo` installs its copy. Inside app data, not the cwd."""
    return config_dir() / "demo-workspace"
