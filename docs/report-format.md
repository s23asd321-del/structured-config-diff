# Report Format

The CLI supports three report formats.

## Text

Text output is intended for terminal use. It contains:

- Summary
- Before and after paths
- Counts by category
- Grouped diff entries
- Safety and privacy notes

## Markdown

Markdown output is intended for pull request comments, release notes, and local documentation. It contains:

- Title
- Summary
- Inputs
- Added
- Removed
- Changed
- Type changes
- Array changes
- Ignored paths
- Safety and privacy notes
- Limitations

## JSON

JSON output is machine-readable and parseable with `json.loads`.

Top-level fields:

- `tool`
- `version`
- `generated_at`
- `before_path`
- `after_path`
- `summary`
- `diffs`
- `ignored_paths`

Each diff includes:

- `path`
- `kind`
- `before_type`
- `after_type`
- `before_value`
- `after_value`
- `value_redacted`
- `message`

When `--no-values` is used, `before_value` and `after_value` are `null`, and `value_redacted` is `true`.

Sensitive-looking values are sanitized before rendering. For nested objects and arrays, child paths are checked recursively before values appear in text, Markdown, or JSON reports.
