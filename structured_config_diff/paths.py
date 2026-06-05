"""Path formatting and ignore matching for config values."""

from __future__ import annotations

from pathlib import Path

ROOT_PATH = "$"


def child_path(parent: str, key: str) -> str:
    if parent == ROOT_PATH:
        return str(key)
    return f"{parent}.{key}"


def array_path(parent: str, index: int) -> str:
    if parent == ROOT_PATH:
        return f"{ROOT_PATH}[{index}]"
    return f"{parent}[{index}]"


def normalize_path(path: str) -> str:
    normalized = path.strip()
    if not normalized:
        return normalized
    if normalized == ROOT_PATH:
        return ROOT_PATH
    if normalized.startswith("$."):
        normalized = normalized[2:]
    elif normalized.startswith("."):
        normalized = normalized[1:]
    return normalized


def path_matches_ignore(path: str, ignore_paths: list[str] | tuple[str, ...]) -> bool:
    normalized = normalize_path(path)
    for ignore in ignore_paths:
        ignored = normalize_path(ignore)
        if not ignored:
            continue
        if ignored == ROOT_PATH:
            return True
        if normalized == ignored:
            return True
        if normalized.startswith(f"{ignored}.") or normalized.startswith(f"{ignored}["):
            return True
    return False


def display_file_path(path: str | Path) -> str:
    """Return a readable path without resolving or exposing extra local context."""

    file_path = Path(path)
    if not file_path.is_absolute():
        return str(file_path)

    try:
        return str(file_path.relative_to(Path.cwd()))
    except ValueError:
        pass

    try:
        return str(Path("~") / file_path.relative_to(Path.home()))
    except ValueError:
        return file_path.name
