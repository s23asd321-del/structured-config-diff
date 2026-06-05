from __future__ import annotations

import pytest

from structured_config_diff.loader import ConfigLoadError, load_config


def test_load_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"app": {"port": 8080}}', encoding="utf-8")

    assert load_config(path) == {"app": {"port": 8080}}


def test_load_toml(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("[app]\nport = 8080\n", encoding="utf-8")

    assert load_config(path) == {"app": {"port": 8080}}


def test_unsupported_format_raises_clear_error(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("app: demo\n", encoding="utf-8")

    with pytest.raises(ConfigLoadError, match="unsupported config format"):
        load_config(path)


def test_remote_url_like_input_is_rejected():
    with pytest.raises(ConfigLoadError, match="remote URLs are not supported"):
        load_config("https://example.invalid/config.json")
