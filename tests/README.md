# Tests

The test suite covers:

- JSON and TOML loading.
- Unsupported format errors.
- Diff kinds.
- Dot path and array path behavior.
- Ignore paths and max-depth behavior.
- Best-effort redaction.
- Text, Markdown, and JSON reports.
- CLI exit codes and output writing.
- CLI `--ignore`, `--no-values`, and parameter error behavior.
- Markdown/text report escaping for unusual paths.
- Local upload-readiness helper checks.
- Example files.

Run:

```bash
python -m pytest
```
