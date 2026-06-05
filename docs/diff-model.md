# Diff Model

Diff paths use dot notation:

- Root path: `$`
- Object field: `server.port`
- Array item: `servers[0].host`

Objects are compared by key. Arrays are compared by index. The first version does not try to match array objects by `id` or any other field.

## Diff Kinds

- `ADDED`: the path exists only in the after file.
- `REMOVED`: the path exists only in the before file.
- `CHANGED`: the path exists in both files with the same type but different scalar values.
- `TYPE_CHANGED`: the path exists in both files but the parsed type differs.
- `ARRAY_LENGTH_CHANGED`: an array has a different length.
- `ARRAY_ITEM_CHANGED`: an array item at the same index changed.
- `UNCHANGED`: emitted only when `--include-unchanged` is used.

## Max Depth

`--max-depth` limits recursive comparison. When a difference is found beyond that depth, it is reported at the current path instead of expanding further.

## Ignored Paths

`--ignore <dot.path>` excludes a path and its descendants. It can be repeated.

