# Configuration Management

## Purpose
To allow streamlined configuration management without destructive file editing, enabling users to customize the linter for their project needs.
## Requirements
### Requirement: Configuration Commands
The system SHALL provide a `configure` subcommand for configuration management.

Priority: Medium

#### Scenario: Generating configuration
- **WHEN** the user runs `vibelinter configure`
- **THEN** configuration snippets (e.g. TOML) are generated for manual addition

### Requirement: Configuration Validation
The system SHALL validate existing configuration.

Priority: Medium

#### Scenario: Validating config
- **WHEN** the user runs `vibelinter configure --validate`
- **THEN** the current configuration is checked for errors
- **AND** effective merged settings are displayed

### Requirement: Configuration Precedence
The system SHALL follow a defined configuration precedence.

Priority: Medium

#### Scenario: Overriding defaults
- **WHEN** a setting is defined in CLI args, `pyproject.toml`, and defaults
- **THEN** CLI args take precedence over `pyproject.toml`
- **AND** `pyproject.toml` takes precedence over defaults

### Requirement: Per-File Rule Exclusion
The system SHALL support disabling specific rules for specific file patterns via configuration.

#### Scenario: Ignoring rules for test files
- **WHEN** the configuration contains `per-file-ignores` mapping `tests/**/*.py` to `["VBL101"]`
- **THEN** rule `VBL101` is not enforced on files matching `tests/**/*.py`
- **AND** other rules are still enforced

