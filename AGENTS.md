# AGENTS.md

This project is a local, read-only structured configuration diff CLI tool.

Agent and maintainer rules:

- Default behavior must not access the network.
- Do not upload user configuration files.
- Do not collect telemetry.
- Do not write back to configuration files.
- Do not automatically repair user configuration files.
- Do not output real values for sensitive-looking fields.
- Do not add real tokens, passwords, cookies, API keys, proxy subscription links, or private credentials.
- Do not add unlawful, abusive, bypass, cracking, piracy, or regulatory-evasion content.
- New diff kinds must include tests.
- CLI behavior changes must update `README.md` or files in `docs/`.
- Security, privacy, and legal wording must stay conservative.
- Avoid unnecessary dependencies.
- Do not implement network features, AI features, database integration, Web UI, or a plugin system in the first version.

