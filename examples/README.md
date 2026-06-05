# Examples

This directory contains small fake configuration files used to demonstrate `structured-config-diff`.

- `before/config.json` and `after/config.json`: JSON example with added, removed, changed, type-changed, and array changes.
- `before/config.toml` and `after/config.toml`: TOML example with similar changes.
- `sensitive/before.json` and `sensitive/after.json`: fake sensitive-looking values for redaction checks.

The examples do not contain real credentials, real tokens, real cookies, personal email addresses, production hosts, or proxy links.

Run:

```bash
python -m structured_config_diff.cli diff examples/before/config.json examples/after/config.json
python -m structured_config_diff.cli diff examples/before/config.toml examples/after/config.toml --format markdown
python -m structured_config_diff.cli diff examples/sensitive/before.json examples/sensitive/after.json --format json
```

