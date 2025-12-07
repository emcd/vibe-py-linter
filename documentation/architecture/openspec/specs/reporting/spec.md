# Reporting

## Purpose
To provide clear, actionable error messages with precise locations so developers can understand and fix violations.

## Requirements

### Requirement: Precise Location
The system SHALL report exact line and column numbers for violations.

Priority: Critical

#### Scenario: Reporting a violation
- **WHEN** a rule is violated
- **THEN** the output includes file path, line number, and column number

### Requirement: Output Formats
The system SHALL support multiple output formats.

Priority: Critical

#### Scenario: JSON output
- **WHEN** the user requests JSON output
- **THEN** the violations are formatted as a JSON array

### Requirement: Context Display
The system SHALL support displaying code context around violations.

Priority: Critical

#### Scenario: Showing context
- **WHEN** the user enables context display
- **THEN** lines of code surrounding the violation are printed
