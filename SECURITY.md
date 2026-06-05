# Security Policy

## Reporting Security Issues

Please report security concerns privately through the maintainer contact channel for the project once one is published. Until then, do not include sensitive material in public issues or pull requests.

Do not post real configuration files, real tokens, real logs, cookies, credentials, or private deployment details in public issue trackers.

## Scope

`structured-config-diff` is a local structured diff tool. It is not a secret scanner, vulnerability scanner, or security audit tool.

The redaction behavior is best-effort and is applied while rendering report values, including nested objects and arrays. It reduces the risk of exposing obvious sensitive-looking fields in reports, but it does not guarantee that every sensitive value will be detected.

Users should review reports before sharing them outside their local environment.
