# Overview

`structured-config-diff` compares two JSON or TOML configuration files as parsed structures. It is intended for local development, pull request summaries, release preparation, and CI checks where a human-readable configuration change report is useful.

The tool is deliberately narrow:

- Local file input only.
- Read-only behavior.
- No network access.
- No telemetry.
- No automatic repair.
- JSON and TOML only in the first version.

The output is a report that groups differences by kind and applies best-effort redaction to sensitive-looking paths.

