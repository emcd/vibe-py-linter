## MODIFIED Requirements

### Requirement: Fix Command

The system SHALL provide a `fix` subcommand.

Priority: High

#### Scenario: Applying fixes

- **WHEN** the user runs `vibelinter fix`
- **THEN** safe fixes are applied to the code

#### Scenario: File discovery

- **WHEN** the user runs `vibelinter fix sources/`
- **THEN** all Python files in the directory are processed
- **AND** fixable violations are corrected

#### Scenario: Rule selection

- **WHEN** the user runs `vibelinter fix --select VBL103`
- **THEN** only fixes from the specified rule are applied

### Requirement: Safety Controls

The system SHALL distinguish between safe and dangerous fixes.

Priority: High

#### Scenario: Dangerous fixes

- **WHEN** a fix is classified as dangerous
- **THEN** it is not applied unless explicitly requested (e.g., via `--apply-dangerous`)

#### Scenario: Safe fixes by default

- **WHEN** the user runs `vibelinter fix` without flags
- **THEN** only fixes classified as `Safe` are applied

#### Scenario: Potentially unsafe fixes

- **WHEN** a fix is classified as `PotentiallyUnsafe`
- **THEN** it is not applied unless `--apply-dangerous` is specified

#### Scenario: Safety reporting

- **WHEN** fixes are skipped due to safety classification
- **THEN** the user is informed which fixes were skipped and why

### Requirement: Dry Run

The system SHALL support a simulation mode.

Priority: High

#### Scenario: Simulating fixes

- **WHEN** the user runs with `--simulate`
- **THEN** changes are previewed but not written to disk

#### Scenario: Unified diff preview

- **WHEN** simulation mode is active with default settings
- **THEN** changes are shown in unified diff format

#### Scenario: Context diff preview

- **WHEN** the user runs `--simulate --diff-format context`
- **THEN** changes are shown in context diff format

## ADDED Requirements

### Requirement: Conflict Resolution

The system SHALL handle overlapping fixes gracefully.

Priority: Medium

#### Scenario: Overlapping fix regions

- **WHEN** multiple fixes target overlapping source regions
- **THEN** fixes are applied in reverse position order (end of file first)
- **AND** conflicting fixes are skipped

#### Scenario: Conflict reporting

- **WHEN** fixes are skipped due to conflicts
- **THEN** the user is informed which fixes were skipped

### Requirement: Fix Collection

The system SHALL collect fixes from fixable rules after violation detection.

Priority: High

#### Scenario: Collecting fixes

- **WHEN** the engine analyzes source code with fixable rules enabled
- **THEN** fixes are collected from rules that support the `FixableRule` interface

#### Scenario: Non-fixable rules

- **WHEN** a rule does not support fixes
- **THEN** it contributes only violations, not fixes
