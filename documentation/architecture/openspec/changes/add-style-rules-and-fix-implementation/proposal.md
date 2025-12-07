# Change: Add Style Rules and Fix Implementation

## Why

The linter currently detects violations but cannot automatically fix them. The `fix` command exists as a CLI stub but has no implementation. Additionally, the style conventions documented in `.auxiliary/instructions/practices-python.rst` (bracket spacing, quote normalization, etc.) are not enforced by any rules.

## What Changes

- **CLI**: Implement the `fix` subcommand to apply automated fixes
- **Rules**: Add style enforcement rules (VBL103-108) for:
  - VBL103: Bracket spacing (spaces inside `()`, `[]`, `{}`)
  - VBL104: Keyword argument spacing (spaces around `=`)
  - VBL105: Quote normalization (single for data, double for messages)
  - VBL106: Single-line body compaction (`if x: return y`)
  - VBL107: Trailing comma enforcement (multi-line collections)
  - VBL108: Docstring formatting (triple single-quotes, spacing)
- **Remediation**: Define fix command behavior scenarios

## Impact

- Affected specs: `rules-readability`, `cli`, `remediation`
- Affected code:
  - `sources/vibelinter/cli.py` - FixCommand implementation
  - `sources/vibelinter/rules/fixable.py` - New fix infrastructure
  - `sources/vibelinter/fixer.py` - New fix engine
  - `sources/vibelinter/rules/implementations/vbl103.py` through `vbl108.py` - New style rules
