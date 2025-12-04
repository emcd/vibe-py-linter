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

Priority: High

#### Scenario: Suppressing via comment
- **WHEN** a line contains a `noqa` or specific suppression comment
- **THEN** violations on that line are ignored

#### Scenario: Suppressing via configuration
- **WHEN** a rule is explicitly disabled in the configuration file
- **THEN** the rule is not executed during analysis
