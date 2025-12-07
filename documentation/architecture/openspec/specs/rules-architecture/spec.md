# Architecture Rules

## Purpose
To enforce structural patterns, type usage, and dependency management rules that maintain architectural integrity.

## Requirements

### Requirement: Import Hub Enforcement [VBL201]
The system SHALL enforce the import hub pattern, where non-hub modules must not expose public imports.

Priority: High

#### Scenario: Public import in non-hub module
- **WHEN** a module not designated as a "hub" (e.g., `__init__.py`) imports a name without aliasing it to private (e.g., `import os`)
- **THEN** a violation is reported

#### Scenario: Valid private alias
- **WHEN** a module imports a name as private (e.g., `import os as _os`)
- **THEN** no violation is reported

### Requirement: Import Spaghetti Detection [VBL202]
The system SHALL prevent excessive relative import depth to reduce coupling.

Priority: High

#### Scenario: Excessive relative depth
- **WHEN** a relative import exceeds the maximum allowed depth (e.g., `from ...module import name`)
- **THEN** a violation is reported

#### Scenario: Invalid sibling import in hub
- **WHEN** a re-export hub (`__.py`) uses single-level relative import (`from . import`)
- **THEN** a violation is reported (to prevent circular backward imports)

### Requirement: Collection Type Variance (REQ-004) [Not Implemented]
The system SHALL require abstract collection types for parameters and concrete types for returns.

Priority: High

#### Scenario: Concrete parameter type
- **WHEN** a function parameter is typed as a concrete collection (e.g., `list`, `dict`)
- **THEN** a suggestion to use an abstract type (e.g., `Sequence`, `Mapping`) is reported

#### Scenario: Abstract return type
- **WHEN** a return type is annotated as abstract (e.g., `Sequence`)
- **THEN** a suggestion to use a concrete or immutable type is reported
