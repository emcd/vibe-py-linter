# Remediation (Auto-Fix)

## Purpose
To provide automated fix capabilities for certain rule violations to speed up resolution.

## Requirements

### Requirement: Fix Command
The system SHALL provide a `fix` subcommand.

Priority: High

#### Scenario: Applying fixes
- **WHEN** the user runs `vibelinter fix`
- **THEN** safe fixes are applied to the code

### Requirement: Safety Controls
The system SHALL distinguish between safe and dangerous fixes.

Priority: High

#### Scenario: Dangerous fixes
- **WHEN** a fix is classified as dangerous
- **THEN** it is not applied unless explicitly requested (e.g., via `--apply-dangerous`)

### Requirement: Dry Run
The system SHALL support a simulation mode.

Priority: High

#### Scenario: Simulating fixes
- **WHEN** the user runs with `--simulate`
- **THEN** changes are previewed but not written to disk
