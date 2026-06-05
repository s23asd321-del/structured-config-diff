# Design

The first version is built around a small pipeline:

1. Load two local files with `json` or `tomllib`.
2. Recursively compare dictionaries, arrays, and scalar values.
3. Produce `DiffItem` records.
4. Build a `DiffReport`.
5. Render the report as text, Markdown, or JSON.

The implementation avoids optional runtime dependencies. Tests use `pytest`.

## Local-First Boundary

The loader accepts local paths and rejects remote URL-like inputs. The CLI does not upload reports, does not modify input configuration files, and does not collect telemetry.

## Data Handling

Input objects are read and compared in memory. The differ does not mutate the loaded data. Reports are printed to stdout unless the user passes `--output`.

## Format Boundary

Only `.json` and `.toml` files are supported. YAML support is intentionally excluded from the first version to avoid extra dependencies and ambiguous parsing behavior.

