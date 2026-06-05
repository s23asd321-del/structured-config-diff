"""Local JSON and TOML loading."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any


class ConfigLoadError(ValueError):
    """Raised when a config file cannot be loaded safely."""


def load_config(path: str | Path) -> Any:
    config_path = Path(path)
    raw = str(path)
    if "://" in raw:
        raise ConfigLoadError("remote URLs are not supported")
    if not config_path.exists():
        raise ConfigLoadError(f"file does not exist: {config_path}")
    if not config_path.is_file():
        raise ConfigLoadError(f"path is not a file: {config_path}")

    suffix = config_path.suffix.lower()
    try:
        if suffix == ".json":
            with config_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        if suffix == ".toml":
            with config_path.open("rb") as handle:
                return tomllib.load(handle)
    except json.JSONDecodeError as exc:
        raise ConfigLoadError(f"invalid JSON in {config_path}: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigLoadError(f"invalid TOML in {config_path}: {exc}") from exc
    except OSError as exc:
        raise ConfigLoadError(f"could not read {config_path}: {exc}") from exc

    raise ConfigLoadError(
        f"unsupported config format for {config_path}; supported extensions are .json and .toml"
    )

