# Readability Rules

## Purpose
To enforce coding standards that improve the readability, consistency, and navigational structure of the code.

## Requirements

### Requirement: Function Ordering (REQ-001)
The system SHALL enforce function ordering: public functions first (alphabetical), then private functions (alphabetical).

Priority: Critical

#### Scenario: Incorrect order (Private before Public)
- **WHEN** a private function (starting with `_`) appears before a public function
- **THEN** a violation is reported

#### Scenario: Incorrect order (Unsorted)
- **WHEN** functions within the same visibility group are not sorted alphabetically
- **THEN** a violation is reported

### Requirement: Blank Line Elimination (REQ-002) [VBL101]
The system SHALL prohibit blank lines within function bodies to keep implementations compact.

Priority: Critical

#### Scenario: Blank line in function body
- **WHEN** a blank line exists between statements in a function body
- **THEN** a violation is reported

#### Scenario: Allowed blank lines
- **WHEN** a blank line appears inside a docstring or multi-line string
- **THEN** no violation is reported

### Requirement: Simple Naming Convention (REQ-003) [Not Implemented]
The system SHALL avoid unnecessary underscores in names unless needed for disambiguation.

Priority: High

#### Scenario: Unnecessary underscore suffix
- **WHEN** a variable name ends with an underscore but no builtin/keyword conflict exists
- **THEN** a violation is reported
