"""Dataclasses used by the structured config diff engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DiffKind(str, Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    CHANGED = "CHANGED"
    TYPE_CHANGED = "TYPE_CHANGED"
    ARRAY_LENGTH_CHANGED = "ARRAY_LENGTH_CHANGED"
    ARRAY_ITEM_CHANGED = "ARRAY_ITEM_CHANGED"
    UNCHANGED = "UNCHANGED"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class DiffItem:
    path: str
    kind: DiffKind
    before_type: str | None
    after_type: str | None
    before_value: Any = None
    after_value: Any = None
    value_redacted: bool = False
    message: str = ""
    severity: Severity = Severity.INFO


@dataclass(frozen=True)
class DiffSummary:
    total: int = 0
    added: int = 0
    removed: int = 0
    changed: int = 0
    type_changed: int = 0
    array_length_changed: int = 0
    array_item_changed: int = 0
    unchanged: int = 0


@dataclass(frozen=True)
class DiffReport:
    tool: str
    version: str
    generated_at: str
    before_path: str
    after_path: str
    summary: DiffSummary
    diffs: list[DiffItem] = field(default_factory=list)
    ignored_paths: list[str] = field(default_factory=list)

