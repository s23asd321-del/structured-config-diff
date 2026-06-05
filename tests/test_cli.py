from __future__ import annotations

import json
from pathlib import Path

from structured_config_diff.cli import main

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cli_diff_default_exits_zero_with_diff(tmp_path, capsys):
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text('{"a": 1}', encoding="utf-8")
    after.write_text('{"a": 2}', encoding="utf-8")

    exit_code = main(["diff", str(before), str(after)])

    assert exit_code == 0
    assert "total changes: 1" in capsys.readouterr().out


def test_cli_fail_on_diff_exits_one(tmp_path):
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text('{"a": 1}', encoding="utf-8")
    after.write_text('{"a": 2}', encoding="utf-8")

    assert main(["diff", str(before), str(after), "--fail-on-diff"]) == 1


def test_cli_output_writes_file(tmp_path):
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    output = tmp_path / "report.md"
    before.write_text('{"a": 1}', encoding="utf-8")
    after.write_text('{"a": 2}', encoding="utf-8")

    exit_code = main(
        [
            "diff",
            str(before),
            str(after),
            "--format",
            "markdown",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert "## Summary" in output.read_text(encoding="utf-8")


def test_cli_unsupported_format_exits_two(tmp_path, capsys):
    before = tmp_path / "before.yaml"
    after = tmp_path / "after.json"
    before.write_text("a: 1\n", encoding="utf-8")
    after.write_text('{"a": 1}', encoding="utf-8")

    exit_code = main(["diff", str(before), str(after)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "unsupported config format" in captured.err


def test_cli_negative_max_depth_exits_two(tmp_path, capsys):
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text('{"a": 1}', encoding="utf-8")
    after.write_text('{"a": 2}', encoding="utf-8")

    exit_code = main(["diff", str(before), str(after), "--max-depth", "-1"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "--max-depth must be 0 or greater" in captured.err


def test_cli_no_values_text_hides_values(tmp_path, capsys):
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text('{"name": "before-only"}', encoding="utf-8")
    after.write_text('{"name": "after-only"}', encoding="utf-8")

    exit_code = main(["diff", str(before), str(after), "--no-values"])

    rendered = capsys.readouterr().out
    assert exit_code == 0
    assert "before-only" not in rendered
    assert "after-only" not in rendered


def test_cli_ignore_path_removes_diff(tmp_path, capsys):
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text('{"logging": {"level": "info"}}', encoding="utf-8")
    after.write_text('{"logging": {"level": "debug"}}', encoding="utf-8")

    exit_code = main(
        [
            "diff",
            str(before),
            str(after),
            "--format",
            "json",
            "--ignore",
            "logging.level",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["summary"]["total"] == 0
    assert payload["ignored_paths"] == ["logging.level"]


def test_examples_json_diff_runs(capsys):
    exit_code = main(
        [
            "diff",
            str(PROJECT_ROOT / "examples/before/config.json"),
            str(PROJECT_ROOT / "examples/after/config.json"),
        ]
    )

    assert exit_code == 0
    assert "Summary" in capsys.readouterr().out


def test_examples_toml_diff_runs(capsys):
    exit_code = main(
        [
            "diff",
            str(PROJECT_ROOT / "examples/before/config.toml"),
            str(PROJECT_ROOT / "examples/after/config.toml"),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)["summary"]["total"] > 0


def test_sensitive_examples_do_not_output_fake_sensitive_values(capsys):
    exit_code = main(
        [
            "diff",
            str(PROJECT_ROOT / "examples/sensitive/before.json"),
            str(PROJECT_ROOT / "examples/sensitive/after.json"),
            "--format",
            "json",
        ]
    )

    rendered = capsys.readouterr().out
    assert exit_code == 0
    assert "FAKE_TOKEN_FOR_TESTING_ONLY" not in rendered
    assert "FAKE_PASSWORD_FOR_TESTING_ONLY" not in rendered
    assert "[REDACTED]" in rendered
