"""Command-line interface for structured-config-diff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .differ import compare_configs
from .loader import ConfigLoadError, load_config
from .report import build_report, render_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="config-diff",
        description="Local-first structured diff for JSON and TOML configuration files.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    diff_parser = subparsers.add_parser("diff", help="Compare two config files")
    diff_parser.add_argument("before_path", help="Path to the baseline config file")
    diff_parser.add_argument("after_path", help="Path to the updated config file")
    diff_parser.add_argument(
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="Report output format",
    )
    diff_parser.add_argument("--output", help="Write the report to a local file")
    diff_parser.add_argument(
        "--fail-on-diff",
        action="store_true",
        help="Exit with code 1 when differences are found",
    )
    diff_parser.add_argument(
        "--no-values",
        action="store_true",
        help="Hide all before and after values in reports",
    )
    diff_parser.add_argument(
        "--max-depth",
        type=int,
        default=20,
        help="Maximum recursive comparison depth",
    )
    diff_parser.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="DOT_PATH",
        help="Ignore a dot path. Can be repeated.",
    )
    diff_parser.add_argument(
        "--include-unchanged",
        action="store_true",
        help="Include unchanged scalar values in the report",
    )
    diff_parser.add_argument(
        "--strict-type",
        action="store_true",
        help="Mark type changes as errors instead of warnings",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "diff":
        return _run_diff(args)

    parser.error(f"unsupported command: {args.command}")
    return 2


def _run_diff(args: argparse.Namespace) -> int:
    if args.max_depth < 0:
        print("error: --max-depth must be 0 or greater", file=sys.stderr)
        return 2

    try:
        before = load_config(args.before_path)
        after = load_config(args.after_path)
        diffs = compare_configs(
            before,
            after,
            max_depth=args.max_depth,
            ignore_paths=args.ignore,
            include_unchanged=args.include_unchanged,
            strict_type=args.strict_type,
        )
        report = build_report(args.before_path, args.after_path, diffs, args.ignore)
        rendered = render_report(report, fmt=args.format, no_values=args.no_values)
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except (ConfigLoadError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.fail_on_diff and report.summary.total > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

