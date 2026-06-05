from __future__ import annotations

from structured_config_diff.differ import compare_configs
from structured_config_diff.models import DiffKind, Severity


def _kinds(diffs):
    return [item.kind for item in diffs]


def test_added_field():
    diffs = compare_configs({"a": 1}, {"a": 1, "b": 2})

    assert DiffKind.ADDED in _kinds(diffs)
    assert diffs[0].path == "b"


def test_removed_field():
    diffs = compare_configs({"a": 1, "b": 2}, {"a": 1})

    removed = [item for item in diffs if item.kind == DiffKind.REMOVED]
    assert removed[0].path == "b"


def test_changed_field():
    diffs = compare_configs({"a": 1}, {"a": 2})

    assert diffs[0].kind == DiffKind.CHANGED
    assert diffs[0].path == "a"


def test_type_changed_defaults_to_warning():
    diffs = compare_configs({"a": 1}, {"a": "1"})

    assert diffs[0].kind == DiffKind.TYPE_CHANGED
    assert diffs[0].severity == Severity.WARNING


def test_strict_type_records_error():
    diffs = compare_configs({"a": 1}, {"a": "1"}, strict_type=True)

    assert diffs[0].kind == DiffKind.TYPE_CHANGED
    assert diffs[0].severity == Severity.ERROR


def test_nested_dot_path_for_change():
    diffs = compare_configs({"server": {"port": 8080}}, {"server": {"port": 9090}})

    assert diffs[0].path == "server.port"


def test_array_length_changed():
    diffs = compare_configs({"items": ["a"]}, {"items": ["a", "b"]})

    assert DiffKind.ARRAY_LENGTH_CHANGED in _kinds(diffs)


def test_array_item_changed():
    diffs = compare_configs({"items": ["a"]}, {"items": ["b"]})

    assert diffs[0].kind == DiffKind.ARRAY_ITEM_CHANGED
    assert diffs[0].path == "items[0]"


def test_ignore_path():
    diffs = compare_configs(
        {"logging": {"level": "info"}, "server": {"port": 8080}},
        {"logging": {"level": "debug"}, "server": {"port": 9090}},
        ignore_paths=["logging"],
    )

    assert [item.path for item in diffs] == ["server.port"]


def test_max_depth_reports_parent_change():
    diffs = compare_configs(
        {"a": {"b": {"c": 1}}},
        {"a": {"b": {"c": 2}}},
        max_depth=1,
    )

    assert diffs[0].kind == DiffKind.CHANGED
    assert diffs[0].path == "a.b"


def test_include_unchanged():
    diffs = compare_configs({"a": 1}, {"a": 1}, include_unchanged=True)

    assert diffs[0].kind == DiffKind.UNCHANGED
    assert diffs[0].path == "a"

