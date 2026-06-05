#!/usr/bin/env python3
"""Lightweight local checks before creating or uploading the GitHub repository."""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "AGENTS.md",
    "SECURITY.md",
    "PRIVACY.md",
    "DISCLAIMER.md",
    ".gitignore",
    ".github/workflows/ci.yml",
    "structured_config_diff/cli.py",
    "structured_config_diff/differ.py",
    "structured_config_diff/report.py",
    "tests/test_cli.py",
)

GENERATED_ARTIFACTS = (
    ".venv",
    "venv",
    ".pytest_cache",
    "dist",
    "build",
    "structured_config_diff.egg-info",
)

GENERATED_NAMES = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".venv",
        "venv",
        "dist",
        "build",
    }
)

DISALLOWED_RUNTIME_TOKENS = (
    "requests",
    "httpx",
    "urllib",
    "urlopen",
    "socket",
    "aiohttp",
    "fetch(",
    "git init",
    "git commit",
    "git push",
    "os.system",
    "subprocess",
)

RUNTIME_PATHS = ("structured_config_diff",)


def run_checks(root: Path) -> list[str]:
    failures: list[str] = []

    for required in REQUIRED_FILES:
        if not (root / required).is_file():
            failures.append(f"missing required file: {required}")

    for artifact in GENERATED_ARTIFACTS:
        if (root / artifact).exists():
            failures.append(f"generated artifact should not be uploaded: {artifact}")

    for path in root.rglob("*"):
        if path.name in GENERATED_NAMES:
            failures.append(f"generated artifact should not be uploaded: {path.relative_to(root)}")
        elif path.suffix == ".pyc" or path.name.endswith(".egg-info"):
            failures.append(f"generated artifact should not be uploaded: {path.relative_to(root)}")

    for runtime_dir in RUNTIME_PATHS:
        for path in (root / runtime_dir).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for token in DISALLOWED_RUNTIME_TOKENS:
                if token in lowered:
                    failures.append(f"disallowed runtime token {token!r} in {path.relative_to(root)}")

    return failures


def main(argv: list[str] | None = None) -> int:
    args = argv or sys.argv[1:]
    root = Path(args[0]) if args else Path.cwd()
    failures = run_checks(root)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("Upload readiness checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
