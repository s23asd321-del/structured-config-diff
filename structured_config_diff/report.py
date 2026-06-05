"""Report rendering for text, Markdown, and JSON output."""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import UTC, datetime
from html import escape
from typing import Any

from . import __version__
from .differ import summarize_diffs
from .models import DiffItem, DiffKind, DiffReport, Severity
from .paths import display_file_path
from .redaction import redact_value

TOOL_NAME = "structured-config-diff"


def build_report(
    before_path: str,
    after_path: str,
    diffs: list[DiffItem],
    ignored_paths: list[str] | None = None,
) -> DiffReport:
    return DiffReport(
        tool=TOOL_NAME,
        version=__version__,
        generated_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        before_path=display_file_path(before_path),
        after_path=display_file_path(after_path),
        summary=summarize_diffs(diffs),
        diffs=diffs,
        ignored_paths=ignored_paths or [],
    )


def render_report(report: DiffReport, *, fmt: str = "text", no_values: bool = False) -> str:
    if fmt == "text":
        return render_text(report, no_values=no_values)
    if fmt == "markdown":
        return render_markdown(report, no_values=no_values)
    if fmt == "json":
        return render_json(report, no_values=no_values)
    raise ValueError(f"unsupported report format: {fmt}")


def render_text(report: DiffReport, *, no_values: bool = False) -> str:
    lines = [
        "Summary",
        f"before path: {report.before_path}",
        f"after path: {report.after_path}",
        f"total changes: {report.summary.total}",
        f"added: {report.summary.added}",
        f"removed: {report.summary.removed}",
        f"changed: {report.summary.changed}",
        f"type_changed: {report.summary.type_changed}",
        f"array changes: {report.summary.array_length_changed + report.summary.array_item_changed}",
        "",
    ]
    if report.ignored_paths:
        lines.append("Ignored paths")
        for path in report.ignored_paths:
            lines.append(f"- {path}")
        lines.append("")

    for title, kinds in _groups(include_unchanged=report.summary.unchanged > 0):
        items = [item for item in report.diffs if item.kind in kinds]
        if not items:
            continue
        lines.append(title)
        for item in items:
            values = _format_values(item, no_values=no_values)
            severity = "" if item.severity == Severity.INFO else f" severity={item.severity.value}"
            lines.append(
                f"- {_plain_text(item.path)} [{item.kind.value}]{severity}: "
                f"{_plain_text(item.message)}{values}"
            )
        lines.append("")

    lines.extend(
        [
            "Safety and privacy notes",
            "- Sensitive-looking paths are redacted with best-effort matching.",
            "- This tool is not a secret scanner or security audit tool.",
            "- Review reports before sharing them outside your local environment.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_markdown(report: DiffReport, *, no_values: bool = False) -> str:
    lines = [
        "# Structured Config Diff Report",
        "",
        "## Summary",
        "",
        f"- Total changes: {report.summary.total}",
        f"- Added: {report.summary.added}",
        f"- Removed: {report.summary.removed}",
        f"- Changed: {report.summary.changed}",
        f"- Type changes: {report.summary.type_changed}",
        f"- Array changes: {report.summary.array_length_changed + report.summary.array_item_changed}",
        "",
        "## Inputs",
        "",
        f"- Before: {_markdown_code(report.before_path)}",
        f"- After: {_markdown_code(report.after_path)}",
        "",
    ]

    sections = [
        ("## Added", (DiffKind.ADDED,)),
        ("## Removed", (DiffKind.REMOVED,)),
        ("## Changed", (DiffKind.CHANGED,)),
        ("## Type changes", (DiffKind.TYPE_CHANGED,)),
        ("## Array changes", (DiffKind.ARRAY_LENGTH_CHANGED, DiffKind.ARRAY_ITEM_CHANGED)),
    ]
    if report.summary.unchanged:
        sections.append(("## Unchanged", (DiffKind.UNCHANGED,)))

    for title, kinds in sections:
        lines.append(title)
        lines.append("")
        items = [item for item in report.diffs if item.kind in kinds]
        if not items:
            lines.append("_None._")
        else:
            for item in items:
                values = _format_values(item, no_values=no_values, markdown=True)
                severity = "" if item.severity == Severity.INFO else f" Severity: `{item.severity.value}`."
                lines.append(
                    f"- {_markdown_code(item.path)} `{item.kind.value}`: "
                    f"{_markdown_text(item.message)}.{severity}{values}"
                )
        lines.append("")

    lines.extend(
        [
            "## Ignored paths",
            "",
        ]
    )
    if report.ignored_paths:
        lines.extend(f"- {_markdown_code(path)}" for path in report.ignored_paths)
    else:
        lines.append("_None._")
    lines.extend(
        [
            "",
            "## Safety and privacy notes",
            "",
            "- Redaction is best-effort and is intended to reduce accidental exposure in reports.",
            "- This tool is not a secret scanner and cannot guarantee that every sensitive value is found.",
            "- The tool does not upload files, collect telemetry, or modify configuration files.",
            "- Review generated reports before sharing them publicly.",
            "",
            "## Limitations",
            "",
            "- JSON and TOML files are supported in the first version.",
            "- Arrays are compared by index; there is no object matching by id.",
            "- The report is a local diff aid, not proof that a configuration is correct or safe.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_json(report: DiffReport, *, no_values: bool = False) -> str:
    payload = {
        "tool": report.tool,
        "version": report.version,
        "generated_at": report.generated_at,
        "before_path": report.before_path,
        "after_path": report.after_path,
        "summary": asdict(report.summary),
        "diffs": [_diff_to_json(item, no_values=no_values) for item in report.diffs],
        "ignored_paths": list(report.ignored_paths),
    }
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _groups(include_unchanged: bool) -> list[tuple[str, tuple[DiffKind, ...]]]:
    groups = [
        ("Added", (DiffKind.ADDED,)),
        ("Removed", (DiffKind.REMOVED,)),
        ("Changed", (DiffKind.CHANGED,)),
        ("Type changes", (DiffKind.TYPE_CHANGED,)),
        ("Array changes", (DiffKind.ARRAY_LENGTH_CHANGED, DiffKind.ARRAY_ITEM_CHANGED)),
    ]
    if include_unchanged:
        groups.append(("Unchanged", (DiffKind.UNCHANGED,)))
    return groups


def _format_values(item: DiffItem, *, no_values: bool, markdown: bool = False) -> str:
    before_value, before_redacted = redact_value(item.path, item.before_value, no_values)
    after_value, after_redacted = redact_value(item.path, item.after_value, no_values)
    if no_values:
        return ""
    if item.before_type is None and item.after_type is None:
        return ""
    if item.before_type is None:
        if after_redacted and after_value == "[REDACTED]":
            return " after=[REDACTED]"
        return f" after={_display_report_value(after_value, markdown=markdown)}"
    if item.after_type is None:
        if before_redacted and before_value == "[REDACTED]":
            return " before=[REDACTED]"
        return f" before={_display_report_value(before_value, markdown=markdown)}"
    redacted = before_redacted or after_redacted or item.value_redacted
    label = " value=[REDACTED]" if redacted else ""
    if redacted:
        return label
    return (
        f" before={_display_report_value(before_value, markdown=markdown)}"
        f" after={_display_report_value(after_value, markdown=markdown)}"
    )


def _display_value(value: Any) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _display_report_value(value: Any, *, markdown: bool) -> str:
    displayed = _display_value(value)
    if markdown:
        return _markdown_text(displayed)
    return displayed


def _plain_text(value: Any) -> str:
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def _markdown_text(value: Any) -> str:
    return escape(_plain_text(value), quote=False)


def _markdown_code(value: Any) -> str:
    text = _plain_text(value)
    runs = [len(match.group(0)) for match in re.finditer(r"`+", text)]
    fence = "`" * (max(runs, default=0) + 1)
    pad = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def _diff_to_json(item: DiffItem, *, no_values: bool) -> dict[str, Any]:
    before_value, before_redacted = redact_value(item.path, item.before_value, no_values)
    after_value, after_redacted = redact_value(item.path, item.after_value, no_values)
    value_redacted = before_redacted or after_redacted or item.value_redacted
    if no_values:
        before_value = None
        after_value = None
        value_redacted = True
    return {
        "path": item.path,
        "kind": item.kind.value,
        "before_type": item.before_type,
        "after_type": item.after_type,
        "before_value": before_value,
        "after_value": after_value,
        "value_redacted": value_redacted,
        "message": item.message,
    }
