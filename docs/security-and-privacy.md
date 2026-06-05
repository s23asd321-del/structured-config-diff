# Security And Privacy

`structured-config-diff` is a local-first tool. It reads local files, compares them, and writes a report only when the user asks for an output file.

It does not:

- Upload files.
- Collect telemetry.
- Access remote URLs.
- Modify input configuration files.
- Perform security audits.
- Scan for every secret.
- Certify privacy compliance.

## Redaction

Redaction is best-effort. If a path or field name contains a sensitive-looking keyword, report values are shown as `[REDACTED]`. Report rendering also sanitizes nested objects and arrays before displaying values.

This is intended to reduce accidental exposure in reports. It cannot guarantee that every sensitive value is detected.

## Sharing Reports

Users should inspect generated reports before sharing them. Use `--no-values` when a report should show structure and change types without values.
