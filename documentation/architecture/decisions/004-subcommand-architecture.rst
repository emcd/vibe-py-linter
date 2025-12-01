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
   | +--------------------------------------------------------------------------+


*******************************************************************************
004. Subcommand-Based CLI Architecture
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

The linter requires a command-line interface that supports multiple operational modes as defined in PRD requirements REQ-006 through REQ-009:

- **REQ-006**: Core linting functionality with file discovery and rule selection
- **REQ-007**: Error reporting with configurable context display
- **REQ-008**: Auto-fix capabilities with safety controls and simulation
- **REQ-009**: Configuration management without destructive file editing

Analysis of CLI design approaches reveals several architectural forces:

**Operational Mode Isolation:**
Different operations have distinct concerns and option sets:

1. **Analysis mode (check)**: Focus on violation detection and reporting
2. **Fix mode**: Requires safety controls, simulation, and change visualization
3. **Configuration mode**: Non-destructive configuration management and validation
4. **Documentation mode (describe)**: Rule discovery and information display
5. **Server modes**: Protocol-specific isolation for LSP and MCP implementations

**Option Namespace Management:**
Different modes require different option sets that would conflict in a single namespace:

- ``--context`` for check mode vs. ``--diff-format`` for fix mode
- ``--simulate`` for fix mode vs. ``--validate`` for configure mode
- Protocol-specific options for different server modes

**Future Extensibility:**
The architecture must accommodate planned enhancements:

- Language Server Protocol (LSP) implementation
- Model Context Protocol (MCP) server mode
- Additional output formats and integrations
- Enhanced safety classifications for auto-fix

**User Experience Consistency:**
CLI design should follow established patterns from tools like ``git``, ``ruff``, and ``mypy`` that use verb-based subcommand structures for different operational modes.

Decision
===============================================================================

We will implement a **verb-based subcommand architecture** with isolated namespaces for different operational modes:

**Subcommand Structure:**

.. code-block:: text

    linter <subcommand> [OPTIONS] [PATHS...]
    
    Subcommands:
    - check      # Default: Analyze code and report violations
    - fix        # Apply automated fixes with safety controls
    - configure  # Manage configuration without file modification
    - describe   # Display rule information and documentation
    - serve      # Server modes (lsp, mcp) for protocol integration

**Architectural Organization:**

.. code-block:: python

    # cli.py - Main CLI orchestration
    class LinterCLI:
        def run(self, args: List[str]) -> int: ...
        def dispatch_subcommand(self, subcommand: str, args: List[str]) -> int: ...
    
    # subcommands/ - Isolated subcommand implementations
    class CheckCommand:
        """Analysis and violation reporting."""
        def configure_parser(self, parser: ArgumentParser) -> None: ...
        def execute(self, args: Namespace) -> int: ...
    
    class FixCommand:
        """Automated fixing with safety controls."""
        def configure_parser(self, parser: ArgumentParser) -> None: ...
        def execute(self, args: Namespace) -> int: ...
    
    class ConfigureCommand:
        """Non-destructive configuration management."""  
        def configure_parser(self, parser: ArgumentParser) -> None: ...
        def execute(self, args: Namespace) -> int: ...

**Subcommand-Specific Options:**

*Check subcommand:*
- ``--context``: Show lines around violations
- ``--select VBL101,VBL201``: Rule selection
- ``--output-format {text,json,structured}``: Output formatting

*Fix subcommand:*
- ``--simulate``: Preview changes without applying
- ``--diff-format {unified,context}``: Diff visualization
- ``--apply-dangerous``: Enable potentially unsafe fixes
- ``--select VBL101``: Apply fixes only for specific rules

*Configure subcommand:*
- ``--validate``: Check configuration without analysis
- ``--interactive``: Interactive configuration wizard
- Non-destructive TOML snippet generation

*Describe subcommand:*
- ``describe rules``: List all available rules
- ``describe rule VBL101``: Detailed rule information

*Serve subcommand:*
- ``serve lsp [LSP_OPTIONS]``: Language Server Protocol mode
- ``serve mcp [MCP_OPTIONS]``: Model Context Protocol mode

**Component Integration:**

.. code-block:: text

    CLI Entry Point
           │
           ▼
    Subcommand Router
           │
           ├─── CheckCommand ──── LinterEngine ──── Rules Framework
           │
           ├─── FixCommand ──── FixEngine ──── Safety Classifier
           │
           ├─── ConfigureCommand ──── ConfigurationManager
           │
           ├─── DescribeCommand ──── RuleRegistry
           │
           └─── ServeCommand ──── Protocol Handlers

**Default Behavior:**
- ``linter`` with no subcommand defaults to ``linter check``
- Maintains backward compatibility with simple usage patterns
- Common options (``--help``, ``--version``) available at top level

Alternatives
===============================================================================

**Alternative 1: Single Command with Mode Flags**

Use flags like ``--check``, ``--fix``, ``--configure`` to specify operational mode.

*Rejected because:*
- **Option namespace conflicts**: Different modes need conflicting option names
- **Poor user experience**: Flags like ``--fix --simulate`` are less intuitive than ``fix --simulate``
- **Scalability limitations**: Adding new modes becomes increasingly complex
- **Inconsistency**: Deviates from established CLI patterns in developer tools

**Alternative 2: Separate Executables**

Create separate executables: ``linter-check``, ``linter-fix``, ``linter-configure``.

*Rejected because:*
- **Installation complexity**: Multiple executables complicate packaging and PATH management
- **Discovery difficulty**: Users must know about multiple commands
- **Maintenance overhead**: Separate entry points and argument parsing for each mode
- **Ecosystem inconsistency**: Single-executable subcommand pattern is standard

**Alternative 3: Plugin-Based Architecture**

Implement subcommands as dynamically loaded plugins.

*Rejected because:*
- **Unnecessary complexity**: Core operational modes don't require plugin architecture
- **Performance overhead**: Dynamic loading adds startup cost
- **Distribution complexity**: Plugin discovery and loading mechanisms
- **Over-engineering**: Simple subcommand dispatch suffices for known modes

Consequences
===============================================================================

**Positive Consequences:**

- **Clear separation of concerns**: Each subcommand handles a distinct operational mode
- **Option namespace isolation**: No conflicts between mode-specific options
- **Intuitive user experience**: Familiar verb-based CLI pattern matching established tools
- **Future extensibility**: New operational modes (server protocols) can be added easily
- **Testing isolation**: Each subcommand can be tested independently
- **Maintainability**: Subcommand logic is contained and focused

**Negative Consequences:**

- **Implementation complexity**: Requires subcommand dispatch and separate parsers
- **Code organization overhead**: Multiple command classes vs. single monolithic parser
- **Potential code duplication**: Common options and validation logic across subcommands
- **Documentation complexity**: Help system must cover multiple subcommands

**Risks and Mitigations:**

- **Risk**: Code duplication across subcommand implementations
  *Mitigation*: Shared base classes and utility functions for common functionality

- **Risk**: Inconsistent option naming across subcommands
  *Mitigation*: Establish naming conventions and shared option definitions

- **Risk**: Complex help system implementation
  *Mitigation*: Use argparse subparser functionality for automatic help generation

- **Risk**: Increased testing surface area
  *Mitigation*: Focus on integration tests for CLI dispatch, unit tests for subcommand logic

**Implementation Guidelines:**

1. **Subcommand base class**: Common interface and utilities for all subcommands
2. **Shared options**: Common options (paths, verbosity) defined once and reused
3. **Graceful degradation**: Helpful error messages for invalid subcommand usage
4. **Consistent exit codes**: Standard exit code patterns across all subcommands
5. **Progressive disclosure**: Basic usage simple, advanced features discoverable

**Architecture Integration:**

- **Configuration system**: All subcommands use the same configuration discovery and loading
- **Rule engine**: Check and fix modes share the same rule evaluation infrastructure  
- **Reporting system**: Consistent error formatting across operational modes
- **File discovery**: Common file enumeration and filtering logic

**Future Enhancements:**

- **Server protocol isolation**: ``serve lsp`` and ``serve mcp`` with protocol-specific options
- **Additional output formats**: Easy extension within existing subcommand structure
- **Enhanced safety controls**: Fix mode can evolve independently of analysis mode
- **Configuration wizards**: Interactive configuration within configure subcommand