## ADDED Requirements

### Requirement: Per-File Rule Exclusion
The system SHALL support disabling specific rules for specific file patterns via configuration.

#### Scenario: Ignoring rules for test files
- **WHEN** the configuration contains `per-file-ignores` mapping `tests/**/*.py` to `["VBL101"]`
- **THEN** rule `VBL101` is not enforced on files matching `tests/**/*.py`
- **AND** other rules are still enforced
