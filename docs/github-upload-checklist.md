# GitHub Upload Checklist

Use this checklist before creating the public repository.

- Confirm the repository contains only project files.
- Confirm generated local artifacts are ignored and not committed.
- Confirm examples use fake values only.
- Confirm no real tokens, passwords, cookies, personal emails, private logs, database files, or proxy links are present.
- Confirm no runtime network request code exists.
- Confirm there is no automatic write-back, repair, or git automation.
- Run `python -m pytest`.
- Run `python scripts/check_upload_ready.py`.
- Run the JSON, TOML, sensitive redaction, and `--fail-on-diff` CLI checks.
- Read `README.md`, `SECURITY.md`, `PRIVACY.md`, and `DISCLAIMER.md` for conservative wording.
- Create the Git repository and first commit manually when ready.
