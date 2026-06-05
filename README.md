# structured-config-diff

Local-first, read-only structured diff reports for JSON and TOML configuration files.

## Project Positioning

`structured-config-diff` is a small CLI tool for comparing two configuration files as parsed data instead of raw text. It helps developers understand added, removed, changed, type-changed, array-changed, and sensitive-looking configuration fields.

The tool runs locally, reads files from disk, prints or writes a report, and does not modify the input files.

## What It Can Do

- Compare two `.json` files.
- Compare two `.toml` files.
- Report added, removed, changed, type-changed, unchanged, and array-related changes.
- Compare dictionaries by key and arrays by index.
- Hide sensitive-looking values with best-effort redaction.
- Generate `text`, `markdown`, or `json` reports.
- Ignore selected dot paths.
- Exit with code `1` when `--fail-on-diff` is used and differences exist.

## What It Cannot Do

- It does not validate whether a configuration is correct.
- It does not scan for every secret.
- It does not perform a security audit.
- It does not provide privacy compliance certification.
- It does not support YAML, XML, INI, remote URLs, recursive directory diff, or automatic fixes.
- It does not upload files, collect telemetry, or call network services.

## Why Structured Diff

Plain text diffs are useful, but configuration files often contain nested objects, arrays, reordered keys, and generated formatting. A structured diff compares parsed values, so the report can describe `server.port` changed, `features.audit` was added, or `plugins[1]` changed without requiring the reader to mentally reconstruct the file structure.

This is especially useful for release notes, pull request summaries, config example migrations, and CI checks where the shape of the change matters more than line numbers.

## Safety And Privacy Boundaries

The tool is local-first and read-only. It does not upload files, send telemetry, or write back to user configuration files.

Redaction is best-effort. If a path or field name contains words such as `password`, `secret`, `token`, `cookie`, `api_key`, `apikey`, `authorization`, `credential`, `private_key`, or `access_key`, values are shown as `[REDACTED]`. Redaction also walks nested objects and arrays before rendering a report, so an added object containing `api_key` is sanitized in report output.

This is a risk-reduction feature only. It is not a secret scanner and cannot guarantee that every sensitive value is detected. Review reports before sharing them.

## Installation

From a published package, once available:

```bash
python -m pip install structured-config-diff
```

For this first local version, install from the repository root:

```bash
python -m pip install .
```

## Local Development Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Quick Start

```bash
python -m structured_config_diff.cli diff examples/before/config.json examples/after/config.json
```

Or, after installing the CLI entry point:

```bash
config-diff diff examples/before/config.json examples/after/config.json
```

## JSON Example

```bash
python -m structured_config_diff.cli diff examples/before/config.json examples/after/config.json
```

Example output excerpt:

```text
Summary
before path: examples/before/config.json
after path: examples/after/config.json
total changes: 17
added: 4
removed: 2
changed: 6
type_changed: 1
array changes: 4
```

## TOML Example

```bash
python -m structured_config_diff.cli diff examples/before/config.toml examples/after/config.toml --format markdown
```

The Markdown report is intended for pull request comments, release notes, and local documentation.

## Sensitive Field Redaction Example

```bash
python -m structured_config_diff.cli diff examples/sensitive/before.json examples/sensitive/after.json --format json
```

Sensitive-looking paths show `[REDACTED]` and JSON diff entries include:

```json
{
  "path": "auth.api_key",
  "value_redacted": true
}
```

## CLI Usage

```bash
config-diff diff <before-path> <after-path> [options]
```

Options:

- `--format text`: human-readable terminal report. This is the default.
- `--format markdown`: Markdown report for PRs and docs.
- `--format json`: machine-readable report.
- `--output <file>`: write the report to a local file.
- `--fail-on-diff`: return exit code `1` when differences exist.
- `--no-values`: hide all before and after values.
- `--max-depth <number>`: limit recursive comparison depth. The default is `20`.
- `--ignore <dot.path>`: ignore a path. Can be repeated.
- `--include-unchanged`: include unchanged scalar values.
- `--strict-type`: record type changes as errors instead of warnings.

## Report Examples

Text:

```text
Changed
- server.port [CHANGED]: value changed at server.port before=8080 after=9090
```

Markdown:

```markdown
## Changed

- `server.port` `CHANGED`: value changed at server.port. before=8080 after=9090
```

JSON:

```json
{
  "path": "server.port",
  "kind": "CHANGED",
  "before_type": "integer",
  "after_type": "integer",
  "before_value": 8080,
  "after_value": 9090,
  "value_redacted": false,
  "message": "value changed at server.port"
}
```

## `--fail-on-diff`

By default, a completed comparison exits with code `0` even when differences exist.

Use `--fail-on-diff` in CI when any diff should fail the job:

```bash
config-diff diff examples/before/config.json examples/after/config.json --fail-on-diff
```

If differences exist, the command exits with code `1`.

## `--no-values`

Use `--no-values` to hide all before and after values:

```bash
config-diff diff before.json after.json --no-values
```

In JSON output, `before_value` and `after_value` are `null`, and `value_redacted` is `true`.

## `--ignore`

Use `--ignore` to exclude a path and its descendants:

```bash
config-diff diff before.json after.json --ignore logging.level --ignore metadata.generated_at
```

Paths use dot notation for objects and bracket notation for arrays, such as `server.port` and `servers[0].host`.

## Exit Codes

- `0`: comparison completed successfully. Differences may still exist.
- `1`: differences exist and `--fail-on-diff` was used.
- `2`: CLI argument error, file read error, unsupported format, or parse error.

## Examples Directory

- `examples/before/config.json` and `examples/after/config.json`: JSON config diff sample.
- `examples/before/config.toml` and `examples/after/config.toml`: TOML config diff sample.
- `examples/sensitive/before.json` and `examples/sensitive/after.json`: fake sensitive values used to demonstrate redaction.

The examples intentionally do not contain real credentials, tokens, cookies, personal emails, or production endpoints.

## Running Tests

```bash
python -m pytest
```

## Uploading This Repository

Before uploading a public repository, check:

- Generated local artifacts such as `.venv/`, `.pytest_cache/`, `__pycache__/`, and `*.egg-info/` are not committed.
- Example values are fake and contain no real credentials, cookies, logs, personal emails, or production endpoints.
- Documentation does not describe the tool as a security audit, compliance tool, or secret scanner.
- CLI behavior is covered by tests when options or report fields change.

You can also run the local helper:

```bash
python scripts/check_upload_ready.py
```

## GitHub Actions And CI

The included CI workflow tests Python 3.11 and 3.12, installs the package in editable mode, runs pytest, runs the upload-readiness helper, checks the installed `config-diff` entry point, and runs CLI smoke checks for JSON, TOML, sensitive redaction, and expected `--fail-on-diff` behavior.

The workflow does not upload generated reports. The tool itself remains local-first and does not perform network requests.

## Roadmap

See `ROADMAP.md` for planned improvements. First-version priorities are conservative: keep the tool local, read-only, dependency-light, and focused on JSON and TOML.

## Contributing

See `CONTRIBUTING.md`. Changes that add a diff kind or alter CLI behavior should include tests and documentation updates.

## Security

See `SECURITY.md`. Do not post real configuration files, credentials, logs, or sensitive reports in public issues.

## Privacy

See `PRIVACY.md`. Reports are generated locally, but users should review them before sharing.

## Disclaimer

See `DISCLAIMER.md`. This tool is not legal advice, a security audit, a privacy compliance assessment, a secret scanner, or proof that a configuration is correct.

## License

MIT License. See `LICENSE`.
