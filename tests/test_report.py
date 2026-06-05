from __future__ import annotations

import json

from structured_config_diff.differ import compare_configs
from structured_config_diff.models import DiffItem, DiffKind
from structured_config_diff.report import (
    build_report,
    render_json,
    render_markdown,
    render_text,
)


def test_markdown_report_contains_summary():
    diffs = compare_configs({"a": 1}, {"a": 2})
    report = build_report("before.json", "after.json", diffs)

    rendered = render_markdown(report)

    assert "# Structured Config Diff Report" in rendered
    assert "## Summary" in rendered


def test_json_report_can_be_loaded():
    diffs = compare_configs({"a": 1}, {"a": 2})
    report = build_report("before.json", "after.json", diffs)

    payload = json.loads(render_json(report))

    assert payload["tool"] == "structured-config-diff"
    assert payload["diffs"][0]["path"] == "a"


def test_no_values_does_not_output_values():
    diffs = compare_configs({"a": 1}, {"a": 2})
    report = build_report("before.json", "after.json", diffs)

    payload = json.loads(render_json(report, no_values=True))

    assert payload["diffs"][0]["before_value"] is None
    assert payload["diffs"][0]["after_value"] is None
    assert payload["diffs"][0]["value_redacted"] is True


def test_sensitive_report_redacts_values():
    diffs = compare_configs(
        {"auth": {"token": "FAKE_TOKEN_FOR_TESTING_ONLY"}},
        {"auth": {"token": "FAKE_TOKEN_ROTATED_FOR_TESTING_ONLY"}},
    )
    report = build_report("before.json", "after.json", diffs)

    rendered = render_json(report)
    payload = json.loads(rendered)

    assert "FAKE_TOKEN_FOR_TESTING_ONLY" not in rendered
    assert payload["diffs"][0]["before_value"] == "[REDACTED]"
    assert payload["diffs"][0]["value_redacted"] is True


def test_text_report_redacts_added_sensitive_value():
    diffs = compare_configs({}, {"auth": {"api_key": "FAKE_API_KEY_FOR_TESTING_ONLY"}})
    report = build_report("before.json", "after.json", diffs)

    rendered = render_text(report)

    assert "[REDACTED]" in rendered
    assert "FAKE_API_KEY_FOR_TESTING_ONLY" not in rendered


def test_markdown_report_escapes_unusual_paths_and_values():
    item = DiffItem(
        path="weird`key\nnext",
        kind=DiffKind.CHANGED,
        before_type="string",
        after_type="string",
        before_value="<before>",
        after_value="<after>",
        message="value changed at weird<script>\nnext",
    )
    report = build_report("before`file.json", "after.json", [item], ["weird`key\nnext"])

    rendered = render_markdown(report)

    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "&lt;before&gt;" in rendered
    assert "&lt;after&gt;" in rendered
    assert "weird`key\\nnext" in rendered


def test_text_report_escapes_newlines_in_paths_and_messages():
    item = DiffItem(
        path="path\nnext",
        kind=DiffKind.CHANGED,
        before_type="string",
        after_type="string",
        before_value="before",
        after_value="after",
        message="changed\nnext",
    )
    report = build_report("before.json", "after.json", [item])

    rendered = render_text(report)

    assert "path\\nnext" in rendered
    assert "changed\\nnext" in rendered
    assert "- path\nnext" not in rendered
