# File Discovery

## Purpose
To reliably locate and filter Python source files for analysis, respecting project configuration and ignore patterns.

## Requirements

### Requirement: Recursive Discovery
The system SHALL accept file paths and directory arguments with recursive directory scanning.

Priority: Critical

#### Scenario: Analyzing a directory
- **WHEN** the user runs the linter on a directory
- **THEN** all Python files in that directory and subdirectories are found

### Requirement: Ignore Patterns
The system SHALL honor `.gitignore` files by default.

Priority: Critical

#### Scenario: Ignoring files
- **WHEN** a file matches a `.gitignore` pattern
- **THEN** it is excluded from analysis
