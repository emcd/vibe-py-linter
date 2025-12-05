# Rule Framework

## Purpose
To provide the general mechanisms for rule management, discovery, configuration, and suppression within the linter.
## Requirements
### Requirement: Rule Discovery (REQ-005)
The system SHALL provide a mechanism to discover and understand available rules.

Priority: Medium

#### Scenario: Listing all rules
- **WHEN** the user runs `vibelinter describe rules`
- **THEN** a list of all registered rules is displayed
- **AND** their current status (enabled/disabled) is shown

#### Scenario: Describing a specific rule
- **WHEN** the user runs `vibelinter describe rule [RULE_ID]`
- **THEN** detailed information about the rule is displayed
- **AND** configuration parameters are listed

### Requirement: Rule Suppression
The system SHALL support suppressing rule violations via configuration or inline comments.

#### Scenario: Suppressing via comment (Specific Rule)
- **WHEN** a line contains a comment ending with `# noqa: VBL101`
- **THEN** violations of rule `VBL101` on that line are ignored

#### Scenario: Suppressing via comment (All Rules)
- **WHEN** a line contains a comment ending with `# noqa`
- **THEN** all violations on that line are ignored

#### Scenario: Suppressing via configuration (Per-File)
- **WHEN** a file matches a per-file ignore pattern for a specific rule
- **THEN** violations of that rule in that file are ignored

