# Release Checklist

- Run `python -m pytest`.
- Run `python scripts/check_upload_ready.py`.
- Run JSON, TOML, and sensitive example CLI checks.
- Confirm `--fail-on-diff` exits with code `1` when differences exist.
- Check documentation for overstatements about security, privacy, or compliance.
- Confirm examples contain no real credentials, cookies, private logs, personal emails, or production endpoints.
- Confirm there is no network request code.
- Confirm there is no write-back or automatic fix behavior.
- Confirm package metadata contains no private personal information.
- Confirm generated local artifacts are ignored by `.gitignore`.
- Confirm the GitHub upload checklist has been reviewed.
