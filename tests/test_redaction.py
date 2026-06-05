from __future__ import annotations

from structured_config_diff.redaction import REDACTED, is_sensitive_path, redact_value


def test_sensitive_path_redaction():
    assert is_sensitive_path("auth.api_key")
    assert redact_value("auth.api_key", "FAKE_API_KEY_FOR_TESTING_ONLY") == (
        REDACTED,
        True,
    )


def test_no_values_hides_everything():
    assert redact_value("server.port", 8080, no_values=True) == (None, True)

