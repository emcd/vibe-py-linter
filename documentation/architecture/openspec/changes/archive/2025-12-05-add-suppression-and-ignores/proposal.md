# Change: Add Suppression and Per-File Ignores

## Why
Users currently cannot suppress specific violations or configure exceptions for specific files. This is a critical feature for adopting the linter in existing codebases where strict adherence might not be immediately possible or desired for all files (e.g., tests, migrations).

## What Changes
- **Configuration**: Add support for `[tool.vibelinter.per-file-ignores]` in `pyproject.toml`.
- **Engine**: Implement inline comment suppression (e.g., `# noqa: VBL101`).
- **Engine**: Update violation filtering logic to respect both per-file ignores and inline suppressions.

## Impact
- **Affected specs**: `configuration`, `rule-framework`
- **Affected code**: `configuration.py`, `engine.py`, `rules/base.py`
