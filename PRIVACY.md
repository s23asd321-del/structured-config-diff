# Privacy

`structured-config-diff` is designed as a local-first CLI tool.

- It does not access the network by default.
- It does not upload files.
- It does not collect telemetry.
- It does not save user configuration content outside the report destination selected by the user.
- Reports are generated locally.

Generated reports can still contain configuration values unless redaction applies or `--no-values` is used. Users should review reports before sharing them publicly.

The `--no-values` option can reduce the risk of exposing values in generated reports by hiding all before and after values.

