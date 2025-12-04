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
