"""Recursive structured diff implementation."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .models import DiffItem, DiffKind, DiffSummary, Severity
from .paths import ROOT_PATH, array_path, child_path, path_matches_ignore


def type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    return type(value).__name__


def summarize_diffs(diffs: list[DiffItem]) -> DiffSummary:
    counts = {kind: 0 for kind in DiffKind}
    for item in diffs:
        counts[item.kind] += 1
    total = sum(count for kind, count in counts.items() if kind != DiffKind.UNCHANGED)
    return DiffSummary(
        total=total,
        added=counts[DiffKind.ADDED],
        removed=counts[DiffKind.REMOVED],
        changed=counts[DiffKind.CHANGED],
        type_changed=counts[DiffKind.TYPE_CHANGED],
        array_length_changed=counts[DiffKind.ARRAY_LENGTH_CHANGED],
        array_item_changed=counts[DiffKind.ARRAY_ITEM_CHANGED],
        unchanged=counts[DiffKind.UNCHANGED],
    )


def compare_configs(
    before: Any,
    after: Any,
    *,
    max_depth: int = 20,
    ignore_paths: list[str] | None = None,
    include_unchanged: bool = False,
    strict_type: bool = False,
) -> list[DiffItem]:
    ignored = ignore_paths or []
    diffs: list[DiffItem] = []
    _compare(
        before,
        after,
        ROOT_PATH,
        0,
        max_depth,
        ignored,
        include_unchanged,
        strict_type,
        diffs,
        within_array=False,
    )
    return diffs


def _compare(
    before: Any,
    after: Any,
    path: str,
    depth: int,
    max_depth: int,
    ignore_paths: list[str],
    include_unchanged: bool,
    strict_type: bool,
    diffs: list[DiffItem],
    *,
    within_array: bool,
) -> None:
    if path_matches_ignore(path, ignore_paths):
        return

    if depth > max_depth:
        if before != after:
            diffs.append(
                DiffItem(
                    path=path,
                    kind=DiffKind.CHANGED,
                    before_type=type_name(before),
                    after_type=type_name(after),
                    before_value=before,
                    after_value=after,
                    message=f"value differs beyond max depth {max_depth}",
                )
            )
        elif include_unchanged:
            diffs.append(_unchanged(path, before, after))
        return

    if type_name(before) != type_name(after):
        severity = Severity.ERROR if strict_type else Severity.WARNING
        diffs.append(
            DiffItem(
                path=path,
                kind=DiffKind.TYPE_CHANGED,
                before_type=type_name(before),
                after_type=type_name(after),
                before_value=before,
                after_value=after,
                message=(
                    f"type changed from {type_name(before)} to {type_name(after)}"
                ),
                severity=severity,
            )
        )
        return

    if isinstance(before, dict):
        _compare_dicts(
            before,
            after,
            path,
            depth,
            max_depth,
            ignore_paths,
            include_unchanged,
            strict_type,
            diffs,
            within_array=within_array,
        )
        return

    if isinstance(before, list):
        _compare_lists(
            before,
            after,
            path,
            depth,
            max_depth,
            ignore_paths,
            include_unchanged,
            strict_type,
            diffs,
        )
        return

    if before != after:
        diffs.append(
            DiffItem(
                path=path,
                kind=DiffKind.ARRAY_ITEM_CHANGED if within_array else DiffKind.CHANGED,
                before_type=type_name(before),
                after_type=type_name(after),
                before_value=before,
                after_value=after,
                message=f"value changed at {path}",
            )
        )
    elif include_unchanged:
        diffs.append(_unchanged(path, before, after))


def _compare_dicts(
    before: dict[str, Any],
    after: dict[str, Any],
    path: str,
    depth: int,
    max_depth: int,
    ignore_paths: list[str],
    include_unchanged: bool,
    strict_type: bool,
    diffs: list[DiffItem],
    *,
    within_array: bool,
) -> None:
    keys = sorted(set(before) | set(after))
    for key in keys:
        item_path = child_path(path, str(key))
        if path_matches_ignore(item_path, ignore_paths):
            continue
        if key not in before:
            diffs.append(
                DiffItem(
                    path=item_path,
                    kind=DiffKind.ADDED,
                    before_type=None,
                    after_type=type_name(after[key]),
                    after_value=after[key],
                    message=f"added {item_path}",
                )
            )
        elif key not in after:
            diffs.append(
                DiffItem(
                    path=item_path,
                    kind=DiffKind.REMOVED,
                    before_type=type_name(before[key]),
                    after_type=None,
                    before_value=before[key],
                    message=f"removed {item_path}",
                )
            )
        else:
            _compare(
                before[key],
                after[key],
                item_path,
                depth + 1,
                max_depth,
                ignore_paths,
                include_unchanged,
                strict_type,
                diffs,
                within_array=within_array,
            )


def _compare_lists(
    before: list[Any],
    after: list[Any],
    path: str,
    depth: int,
    max_depth: int,
    ignore_paths: list[str],
    include_unchanged: bool,
    strict_type: bool,
    diffs: list[DiffItem],
) -> None:
    if len(before) != len(after) and not path_matches_ignore(path, ignore_paths):
        diffs.append(
            DiffItem(
                path=path,
                kind=DiffKind.ARRAY_LENGTH_CHANGED,
                before_type="array",
                after_type="array",
                before_value=len(before),
                after_value=len(after),
                message=f"array length changed from {len(before)} to {len(after)}",
            )
        )

    shared_length = min(len(before), len(after))
    for index in range(shared_length):
        item_path = array_path(path, index)
        if path_matches_ignore(item_path, ignore_paths):
            continue
        before_count = len(diffs)
        _compare(
            before[index],
            after[index],
            item_path,
            depth + 1,
            max_depth,
            ignore_paths,
            include_unchanged,
            strict_type,
            diffs,
            within_array=True,
        )
        if len(diffs) > before_count:
            last = diffs[-1]
            if last.path == item_path and last.kind == DiffKind.CHANGED:
                diffs[-1] = replace(last, kind=DiffKind.ARRAY_ITEM_CHANGED)

    for index in range(shared_length, len(before)):
        item_path = array_path(path, index)
        if path_matches_ignore(item_path, ignore_paths):
            continue
        diffs.append(
            DiffItem(
                path=item_path,
                kind=DiffKind.REMOVED,
                before_type=type_name(before[index]),
                after_type=None,
                before_value=before[index],
                message=f"removed array item {item_path}",
            )
        )

    for index in range(shared_length, len(after)):
        item_path = array_path(path, index)
        if path_matches_ignore(item_path, ignore_paths):
            continue
        diffs.append(
            DiffItem(
                path=item_path,
                kind=DiffKind.ADDED,
                before_type=None,
                after_type=type_name(after[index]),
                after_value=after[index],
                message=f"added array item {item_path}",
            )
        )


def _unchanged(path: str, before: Any, after: Any) -> DiffItem:
    return DiffItem(
        path=path,
        kind=DiffKind.UNCHANGED,
        before_type=type_name(before),
        after_type=type_name(after),
        before_value=before,
        after_value=after,
        message=f"unchanged at {path}",
    )

