# linter-rules Specification

## Purpose
TBD - created by archiving change update-vbl101-nested-spacing. Update Purpose after archive.
## Requirements
### Requirement: VBL101 Blank Line Elimination
The linter SHALL detect and report blank lines within function bodies to enforce vertical compactness, with specific exceptions for nested definitions and string literals.

#### Scenario: Blank line between statements
- **WHEN** a blank line exists between two standard statements in a function
- **THEN** a violation is reported

#### Scenario: Blank line in string literal
- **WHEN** a blank line exists inside a triple-quoted string or docstring
- **THEN** no violation is reported

#### Scenario: Blank line before nested definition
- **WHEN** a blank line immediately precedes a nested `def` or `class` statement
- **THEN** no violation is reported

#### Scenario: Blank line after nested definition
- **WHEN** a blank line immediately follows a nested `def` or `class` block
- **THEN** no violation is reported

#### Scenario: Multiple blank lines
- **WHEN** multiple contiguous blank lines exist (even around nested definitions)
- **THEN** violations are reported for the excess blank lines (logic typically reports all blank lines, so strict implementation might report all or allow only one; implying single blank line allowed)

