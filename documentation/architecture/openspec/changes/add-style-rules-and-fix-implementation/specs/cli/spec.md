## ADDED Requirements

### Requirement: Fix Subcommand

The system SHALL provide a `fix` subcommand that applies automated fixes for detected violations.

Priority: High

#### Scenario: Applying fixes to files

- **WHEN** the user runs `vibelinter fix sources/`
- **THEN** fixable violations in Python files are automatically corrected
- **AND** modified files are written to disk

#### Scenario: Selecting specific rules for fixing

- **WHEN** the user runs `vibelinter fix --select VBL103,VBL104`
- **THEN** only fixes for the specified rules are applied

#### Scenario: Simulation mode

- **WHEN** the user runs `vibelinter fix --simulate`
- **THEN** changes are previewed as a diff
- **AND** no files are modified

#### Scenario: Diff format selection

- **WHEN** the user runs `vibelinter fix --simulate --diff-format context`
- **THEN** the preview uses context diff format instead of unified

#### Scenario: Dangerous fix control

- **WHEN** the user runs `vibelinter fix` without `--apply-dangerous`
- **THEN** only safe fixes are applied
- **AND** potentially unsafe and dangerous fixes are skipped

#### Scenario: Enabling dangerous fixes

- **WHEN** the user runs `vibelinter fix --apply-dangerous`
- **THEN** all applicable fixes including dangerous ones are applied

#### Scenario: No fixable violations

- **WHEN** no fixable violations are found
- **THEN** the command exits with code 0
- **AND** reports that no fixes were needed
