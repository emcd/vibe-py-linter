# Command Line Interface

## Purpose
To provide a command-line interface for running the linter, allowing integration with existing development workflows and CI/CD pipelines.

## Requirements

### Requirement: CLI Structure
The system SHALL support a verb-based subcommand structure.

Priority: Critical

#### Scenario: Running the default check
- **WHEN** the user runs `vibelinter` without arguments or with `check`
- **THEN** the linter performs the analysis
- **AND** reports violations

#### Scenario: Getting help
- **WHEN** the user runs `vibelinter --help`
- **THEN** usage information and available subcommands are displayed

### Requirement: File Discovery
The system SHALL accept file paths and directory arguments with recursive directory scanning.

Priority: Critical

#### Scenario: Analyzing a directory
- **WHEN** the user runs `vibelinter sources/`
- **THEN** all Python files in `sources/` and subdirectories are analyzed
- **AND** `.gitignore` patterns are respected by default

### Requirement: Rule Selection
The system SHALL support rule selection via parameters.

Priority: Critical

#### Scenario: Selecting specific rules
- **WHEN** the user runs `vibelinter --select VBL101,VBL201`
- **THEN** only rules VBL101 and VBL201 are executed

### Requirement: Parallel Processing
The system SHALL support parallel processing.

Priority: High

#### Scenario: Running on multi-core machine
- **WHEN** the user runs `vibelinter --jobs 4`
- **THEN** the analysis is distributed across 4 processes
- **AND** performance is improved for large codebases

### Requirement: Exit Codes
The system SHALL return appropriate exit codes.

Priority: Critical

#### Scenario: Violations found
- **WHEN** the linter finds rule violations
- **THEN** it exits with code 1

#### Scenario: Clean code
- **WHEN** the linter finds no violations
- **THEN** it exits with code 0

#### Scenario: Errors
- **WHEN** the linter encounters an internal error or configuration error
- **THEN** it exits with code 2 or higher
