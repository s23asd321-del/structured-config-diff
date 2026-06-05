"""Best-effort value redaction for report output."""

from __future__ import annotations

from typing import Any

SENSITIVE_KEYWORDS = (
    "password",
    "secret",
    "token",
    "cookie",
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "private_key",
    "access_key",
)

REDACTED = "[REDACTED]"


def is_sensitive_path(path: str) -> bool:
    lowered = path.lower()
    return any(keyword in lowered for keyword in SENSITIVE_KEYWORDS)


def redact_value(path: str, value: Any, no_values: bool = False) -> tuple[Any, bool]:
    if no_values:
        return None, True
    if is_sensitive_path(path):
        return REDACTED, True
    if isinstance(value, dict):
        redacted = False
        sanitized: dict[Any, Any] = {}
        for key, child_value in value.items():
            child_path = _child_path(path, str(key))
            sanitized_value, child_redacted = redact_value(child_path, child_value)
            sanitized[key] = sanitized_value
            redacted = redacted or child_redacted
        return sanitized, redacted
    if isinstance(value, list):
        redacted = False
        sanitized_items = []
        for index, child_value in enumerate(value):
            child_path = _array_path(path, index)
            sanitized_value, child_redacted = redact_value(child_path, child_value)
            sanitized_items.append(sanitized_value)
            redacted = redacted or child_redacted
        return sanitized_items, redacted
    return value, False


def _child_path(parent: str, key: str) -> str:
    if parent == "$":
        return key
    return f"{parent}.{key}"


def _array_path(parent: str, index: int) -> str:
    if parent == "$":
        return f"$[{index}]"
    return f"{parent}[{index}]"
