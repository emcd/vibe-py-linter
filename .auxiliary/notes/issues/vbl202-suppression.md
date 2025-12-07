# VBL202 Self-Application Issue

**Severity**: Medium  
**Component**: `sources/vibelinter/rules/implementations/vbl202.py`  
**Discovered**: 2025-12-07 (during `describe` subcommand implementation)  
**Status**: Temporary workaround applied

## Description

VBL202 (import-spaghetti-detection) detects violations in its own implementation code and other rule implementation files when they are imported for the `describe` subcommand. This creates a chicken-and-egg problem where the rule cannot be registered without first violating itself.

## Problem Details

When `vbl202.py` is imported (to register the rule in `RULE_DESCRIPTORS`), the rule's code executes and immediately analyzes the importing module's imports. It detects legitimate violations:

1. **In `vbl101.py:172`**: `from .. import __` - Two-level relative import
2. **In `registry.py:98`**: `from .. import __` - Two-level relative import  
3. **In `registry.py:126`**: `from .. import __` - Two-level relative import

These are actual violations of VBL202's rule (preventing excessive relative import depth), but they prevent the rule from being registered and displayed in the `describe` commands.

## Impact

- `describe rules` command would not show VBL202
- `describe rule import-spaghetti-detection` would fail
- Rule cannot be used if it blocks its own registration

## Temporary Workaround

Added per-file ignore in `pyproject.toml`:
```toml
[sources/vibelinter/rules/**/*.py] = [
  "import-spaghetti-detection", # VBL202
]
```

This allows VBL202 to be registered and used while suppressing violations in rule implementation files.

## Root Cause Analysis

The issue arises because:
1. Rule registration happens at module import time
2. Rule analysis runs during registration (when rule class is defined)
3. The analysis examines the importing context, not just target files
4. Rule implementation files legitimately violate the rule they enforce

## Long-term Solutions

### Option 1: Deferred Analysis
- Modify rule framework to analyze only when explicitly invoked
- Separate rule registration from analysis execution
- Requires architectural changes to `BaseRule`

### Option 2: Exempt Rule Implementation Files
- Add special handling for files in `rules/implementations/` directory
- Could be done via configuration or framework logic
- Maintains rule integrity while allowing registration

### Option 3: Fix Violations in Source
- Restructure imports in rule implementation files
- May require significant refactoring
- Could affect other rules or code organization

## Recommendation

**Option 2 (Exempt Rule Implementation Files)** is recommended as it:
- Maintains rule correctness for user code
- Allows rule registration without self-blocking
- Requires minimal framework changes
- Can be implemented as a configuration option

## Test Coverage

Issue discovered during testing of `describe` subcommand implementation. All tests pass with temporary workaround.

## Related Files

- `pyproject.toml`: Temporary suppression configuration
- `sources/vibelinter/rules/implementations/__init__.py`: Rule imports
- `sources/vibelinter/cli.py`: `describe` command implementation