.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
System Overview
*******************************************************************************

The Python linter implements a modular architecture centered around a pluggable rule engine that analyzes Python source code using concrete syntax tree (CST) analysis. The system emphasizes extensibility, performance, and precise error reporting.

High-Level Architecture
===============================================================================

System Overview
-------------------------------------------------------------------------------

The linter follows a pipeline architecture with these major phases:

1. **Input Processing**: File discovery, parsing, and validation
2. **Analysis**: CST construction and metadata extraction  
3. **Rule Execution**: Pluggable rule evaluation against the CST
4. **Result Aggregation**: Violation collection and deduplication
5. **Output Formatting**: User-facing error reporting

Core Components
-------------------------------------------------------------------------------

**Linter Engine** (``sources/vibelinter/engine.py``)
  Central orchestrator that coordinates file processing, rule execution, and result aggregation. Manages the analysis pipeline and provides the primary API for both CLI and programmatic usage.

**Rule Framework** (``sources/vibelinter/rules/``)
  Extensible framework for implementing linting rules. Provides base classes, common utilities, and a registry system for rule discovery and configuration.

**Configuration System** (``sources/vibelinter/configuration.py``)
  Handles TOML-based configuration loading, rule parameter management, and project-specific customization. Supports both command-line overrides and ``pyproject.toml`` integration with non-destructive configuration management.

**CLI Interface** (``sources/vibelinter/cli.py``)
  Subcommand-based command-line interface with verb-based operational modes (check, fix, configure, describe, serve). Provides isolated option namespaces and coordinates different workflows through the linter engine.

**Error Reporting** (``sources/vibelinter/reporting.py``)
  Violation formatting, message generation, and output channel management. Supports multiple output formats and severity levels.

Component Relationships
-------------------------------------------------------------------------------

.. code-block:: text

    ┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
    │ CLI Subcommands │───▶│ Engine       │───▶│ Rules       │
    │ (check,fix,     │    │              │    │ Framework   │
    │  configure...)  │    │              │    │             │
    └─────────────────┘    └──────┬───────┘    └─────────────┘
                                  │                     │
                                  ▼                     ▼
                        ┌──────────────┐    ┌─────────────────┐
                        │ Configuration│    │ Individual      │
                        │ Management   │    │ Rules           │
                        │ (Non-destructive)  │ (VBL codes)     │
                        └──────────────┘    └─────────────────┘
                                  │                     │
                                  ▼                     ▼
                        ┌──────────────┐    ┌─────────────────┐
                        │ CST Analysis │    │ Violation       │
                        │ (LibCST)     │    │ Collection      │
                        └──────────────┘    └─────────────────┘
                                  │                     │
                                  └─────────▼───────────┘
                                       ┌──────────────┐
                                       │ Error        │
                                       │ Reporting    │
                                       └──────────────┘

Data Flow
-------------------------------------------------------------------------------

**Primary Analysis Flow:**

1. **Input**: File paths or directory patterns from CLI
2. **Discovery**: Recursive Python file enumeration 
3. **Parsing**: LibCST syntax tree construction with metadata
4. **Analysis**: Rule execution against enriched CST
5. **Collection**: Violation aggregation and deduplication
6. **Output**: Formatted error reports with precise locations

**Configuration Flow:**

1. **Discovery**: Locate ``pyproject.toml`` or explicit configuration
2. **Loading**: Parse TOML configuration sections
3. **Validation**: Verify rule parameters and severity levels
4. **Application**: Configure rule instances and engine behavior

**Rule Execution Flow:**

1. **Registration**: Discover and instantiate enabled rules
2. **Metadata**: Attach position, scope, and qualified name providers
3. **Traversal**: Visit CST nodes using the visitor pattern
4. **Detection**: Identify code smell violations
5. **Reporting**: Generate precise violation descriptions

Key Architectural Patterns
===============================================================================

Visitor Pattern for Rule Implementation
-------------------------------------------------------------------------------

Rules implement the CST visitor pattern, allowing them to traverse syntax trees and respond to specific node types. This provides:

- **Separation of concerns**: Each rule focuses on specific code patterns
- **Performance**: Single-pass analysis with multiple rule evaluation
- **Extensibility**: New rules require minimal framework changes

Plugin Architecture for Rules
-------------------------------------------------------------------------------

The rule framework uses a plugin-style architecture:

- **Base classes**: Common functionality and metadata access
- **Registry system**: Automatic rule discovery and configuration
- **Isolation**: Rules operate independently without cross-dependencies

Metadata-Rich Analysis
-------------------------------------------------------------------------------

LibCST metadata providers enrich the syntax tree with:

- **Position information**: Precise line/column error reporting
- **Scope analysis**: Variable and function visibility tracking  
- **Qualified names**: Full import path resolution

Configuration-Driven Behavior
-------------------------------------------------------------------------------

All rule behavior is configurable through:

- **Enable/disable**: Individual rule activation control
- **Severity levels**: Error, warning, and info classifications
- **Rule parameters**: Customizable thresholds and options
- **Project integration**: ``pyproject.toml`` configuration sections

Deployment Architecture
===============================================================================

Development Integration
-------------------------------------------------------------------------------

The linter integrates with standard Python development workflows:

- **CLI tool**: Direct command-line execution
- **Python module**: ``python -m vibelinter`` execution
- **Pre-commit hooks**: Automated quality gate integration
- **CI/CD pipelines**: Exit code-based build validation

Performance Characteristics
-------------------------------------------------------------------------------

**Single-threaded analysis**: Per-file processing using LibCST
**Memory efficiency**: Streaming file processing without global state
**Incremental analysis**: File-by-file processing enables parallel execution
**Caching potential**: Future AST caching for improved performance

Error Handling Strategy
-------------------------------------------------------------------------------

**Graceful degradation**: Malformed files generate parse errors without crashing
**Error isolation**: Rule exceptions don't affect other rule execution
**Detailed reporting**: Context-rich error messages with actionable guidance
**Exit codes**: Standard UNIX conventions for CI/CD integration

Future Extensibility
===============================================================================

The architecture supports planned enhancements:

- **Auto-fixing**: CST transformer integration for automated corrections
- **Language server**: Protocol implementation for editor integration  
- **Custom rules**: User-defined rule development framework
- **Performance optimization**: Parallel processing and caching strategies