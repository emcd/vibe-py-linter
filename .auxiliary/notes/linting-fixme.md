# Linting Issues to Fix

The core rules framework implementation has 78 linting errors that need to be addressed in a follow-up commit:

## E501 - Line Too Long (> 79 characters)

Many lines in the new code exceed 79 characters. These are primarily in:
- `sources/vibelinter/engine.py` - Type annotations and docstrings
- `sources/vibelinter/rules/violations.py` - Type annotations
- `sources/vibelinter/rules/registry.py` - Type annotations
- `sources/vibelinter/rules/context.py` - Type annotations
- `sources/vibelinter/rules/base.py` - Docstrings and type annotations
- `sources/vibelinter/rules/implementations/vbl101.py` - Docstrings

Strategy: Break long lines at natural boundaries (after commas, before closing brackets).

## F821 - Undefined Forward References

Two forward references need `from __future__ import annotations`:
- `'RuleRegistryManager'` in engine.py
- `'BaseRule'` in registry.py

Strategy: Add `from __future__ import annotations` at the top of these files.

## TRY003 - Long Exception Messages

Exception messages should be defined in the exception class, not at the raise site:
- `RuleRegistryInvalidity` messages in registry.py

Strategy: Consider if this is worth the complexity, or just add `# noqa: TRY003`.

## F403 - Star Imports

The `from ..__ import *` pattern used throughout the codebase triggers this warning.

Strategy: Add `# ruff: noqa: F403` to files using this pattern, consistent with existing code style.

## Status

The code is functionally correct and all tests pass. These are purely style/lint issues that will be addressed in a follow-up commit to keep the implementation commit focused on functionality.
