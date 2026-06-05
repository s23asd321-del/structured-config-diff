from __future__ import annotations

from pathlib import Path

from structured_config_diff.paths import (
    ROOT_PATH,
    array_path,
    child_path,
    display_file_path,
    path_matches_ignore,
)


def test_nested_dot_path():
    assert child_path(child_path(ROOT_PATH, "server"), "port") == "server.port"


def test_array_path():
    assert array_path("servers", 0) == "servers[0]"


def test_ignore_path_matches_descendants():
    assert path_matches_ignore("server.tls.enabled", ["server.tls"])
    assert path_matches_ignore("servers[0].host", ["servers[0]"])
    assert not path_matches_ignore("server.port", ["logging"])


def test_display_file_path_prefers_cwd_relative_path():
    path = Path.cwd() / "examples" / "before" / "config.json"

    assert display_file_path(path) == "examples/before/config.json"
