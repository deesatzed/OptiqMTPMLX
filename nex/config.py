"""
Simple configuration system for Nex multi-model runner.

Stores:
- default_model
- user_added_models (list of extra repos the user cares about)
- per_model_overrides (custom temp, etc.)

Location: ~/.config/nex/config.json (or NEX_CONFIG_PATH env var)
Falls back to local .nex-config.json in the project if present.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import KNOWN_MODELS, ModelProfile, get_profile

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "nex"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"

LOCAL_CONFIG = Path(".nex-config.json")


def get_config_path() -> Path:
    env_path = os.environ.get("NEX_CONFIG_PATH")
    if env_path:
        return Path(env_path)
    if LOCAL_CONFIG.exists():
        return LOCAL_CONFIG
    return DEFAULT_CONFIG_FILE


def load_config() -> Dict[str, Any]:
    path = get_config_path()
    if not path.exists():
        return {"default_model": None, "user_models": [], "overrides": {}}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {"default_model": None, "user_models": [], "overrides": {}}


def save_config(cfg: Dict[str, Any]) -> None:
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2))


def get_default_model() -> Optional[str]:
    cfg = load_config()
    return cfg.get("default_model")


def set_default_model(repo_or_alias: str) -> None:
    cfg = load_config()
    profile = get_profile(repo_or_alias)
    cfg["default_model"] = profile.repo_id
    save_config(cfg)


def get_user_models() -> List[str]:
    cfg = load_config()
    return cfg.get("user_models", [])


def add_user_model(repo_id: str) -> None:
    cfg = load_config()
    if repo_id not in cfg.get("user_models", []):
        cfg.setdefault("user_models", []).append(repo_id)
    save_config(cfg)


def get_overrides(model: str) -> Dict[str, Any]:
    cfg = load_config()
    profile = get_profile(model)
    return cfg.get("overrides", {}).get(profile.repo_id, {})


def set_override(model: str, key: str, value: Any) -> None:
    cfg = load_config()
    profile = get_profile(model)
    overrides = cfg.setdefault("overrides", {})
    model_over = overrides.setdefault(profile.repo_id, {})
    model_over[key] = value
    save_config(cfg)


def get_effective_profile(model: Optional[str] = None) -> ModelProfile:
    """Return profile merged with user config overrides."""
    if model is None:
        model = get_default_model() or "nex-n2-mini"
    profile = get_profile(model)
    overrides = get_overrides(model)

    # Apply simple overrides
    for k, v in overrides.items():
        if hasattr(profile, k):
            setattr(profile, k, v)
    return profile
