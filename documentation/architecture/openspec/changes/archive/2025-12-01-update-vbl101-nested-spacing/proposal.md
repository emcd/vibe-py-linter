# Change: Update VBL101 to Allow Spacing Around Nested Definitions

## Why
The current strict blank line elimination rule (VBL101) makes functions with nested definitions (closures, helper classes) harder to read by forcing them to be visually mashed against the surrounding code. Allowing blank lines around these logical blocks improves readability while maintaining the goal of compactness for simple statements.

## What Changes
- **Rule Logic:** VBL101 will now identify nested `def` and `class` blocks within function bodies.
- **Exception:** Blank lines immediately preceding or following a nested definition will be permitted.
- **Strictness:** Blank lines elsewhere in the function body (between standard statements) remain prohibited.

## Impact
- **Linter Behavior:** Users will no longer receive warnings for blank lines framing nested definitions.
- **Tests:** Existing tests asserting strict prohibition will be updated; new tests for the exception will be added.
