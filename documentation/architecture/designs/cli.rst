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
CLI System Design
*******************************************************************************

This document specifies the command-line interface design following the subcommand architecture established in ADR-004 and using Tyro's dataclass-based approach.

Overview
===============================================================================

The CLI system implements a verb-based subcommand architecture with clean separation between command logic and CLI orchestration. Each subcommand handles a distinct operational mode with isolated option namespaces, following the patterns established in the CLI discussion and subcommand architecture decision.

Design Principles
-------------------------------------------------------------------------------

**Subcommand Isolation:** Each operational mode (check, fix, configure, describe, serve) has dedicated command classes with specific option sets to prevent namespace conflicts.

**Type Safety:** Comprehensive type annotations using Tyro's dataclass integration provide automatic help generation and runtime type validation.

**Protocol-Based Design:** Common command interface enables consistent execution patterns and future extensibility.

**Integration Architecture:** Seamless coordination with established configuration, engine, and reporting systems.

Module Organization
===============================================================================

The CLI system follows the established filesystem architecture:

.. code-block::

    sources/vibelinter/
    ├── cli.py              # Main CLI orchestration and Tyro integration
    ├── subcommands/        # Individual subcommand implementations
    │   ├── __init__.py     # Subcommand registry and common patterns
    │   ├── __.py           # Centralized imports for subcommand implementations
    │   ├── check.py        # Analysis and violation reporting
    │   ├── fix.py          # Auto-fix with safety controls
    │   ├── configure.py    # Non-destructive configuration management
    │   ├── describe.py     # Rule documentation and discovery
    │   └── serve.py        # Protocol server modes (future)
    └── interfaces.py       # CLI-related type definitions and contracts

Type System Specification
===============================================================================

Core Type Annotations
-------------------------------------------------------------------------------

The CLI system defines comprehensive type annotations following practices guidelines:

.. code-block:: python

    # Type aliases for CLI parameters
    OutputFormat: __.typx.TypeAlias = __.typx.Literal[ 'text', 'json', 'structured' ]
    DiffFormat: __.typx.TypeAlias = __.typx.Literal[ 'unified', 'context' ]
    RuleSelectorArgument: __.typx.TypeAlias = __.typx.Annotated[
        str,
        __.ddoc.Doc( "Comma-separated VBL rule codes (e.g. VBL101,VBL201)." )
    ]
    PathsArgument: __.typx.TypeAlias = __.typx.Annotated[
        tuple[ str, ... ],
        __.ddoc.Doc( "Files or directories to analyze." )
    ]
    ContextLinesArgument: __.typx.TypeAlias = __.typx.Annotated[
        int,
        __.ddoc.Doc( "Number of context lines around violations." )
    ]

Command Protocol Interface
-------------------------------------------------------------------------------

All subcommands implement a common protocol:

.. code-block:: python

    class _CliCommand( __.immut.DataclassProtocol, __.typx.Protocol ):
        ''' CLI command protocol for subcommand implementations. '''

        @__.abc.abstractmethod
        async def __call__(
            self,
            configuration: Configuration,  # From configuration system
            engine: Engine,                # From core engine
        ) -> int:
            ''' Executes command with configuration and engine context.
            
            Returns appropriate exit code (0=success, 1=violations, 2+=errors).
            '''
            '''
            raise NotImplementedError

Subcommand Specifications
===============================================================================

Check Command (Default)
-------------------------------------------------------------------------------

Primary analysis functionality with configurable output and context display:

.. code-block:: python

    class CheckCommand( _CliCommand, decorators = ( __.standard_tyro_class, ) ):
        ''' Analyzes code and reports violations. '''

        paths: PathsArgument = ( '.' )
        select: __.Absential[ RuleSelectorArgument ] = __.absent
        report_format: __.typx.Annotated[
            OutputFormat,
            __.ddoc.Doc( "Output format for violation reporting." )
        ] = 'text'
        context: __.typx.Annotated[
            int,
            __.ddoc.Doc( "Show context lines around violations." )
        ] = 0
        jobs: __.typx.Annotated[
            __.typx.Union[ int, __.typx.Literal[ 'auto' ] ],
            __.ddoc.Doc( "Number of parallel processing jobs." )
        ] = 'auto'

        async def __call__(
            self,
            configuration: Configuration,
            engine: Engine,
        ) -> int: ...

Fix Command
-------------------------------------------------------------------------------

Auto-fix functionality with safety controls and simulation capabilities:

.. code-block:: python

    class FixCommand( _CliCommand, decorators = ( __.standard_tyro_class, ) ):
        ''' Applies automated fixes with safety controls. '''

        paths: PathsArgument = ( '.' )
        select: __.Absential[ RuleSelectorArgument ] = __.absent
        simulate: __.typx.Annotated[
            bool,
            __.ddoc.Doc( "Preview changes without applying them." )
        ] = False
        diff_format: __.typx.Annotated[
            DiffFormat,
            __.ddoc.Doc( "Diff visualization format." )
        ] = 'unified'
        apply_dangerous: __.typx.Annotated[
            bool,
            __.ddoc.Doc( "Enable potentially unsafe fixes." )
        ] = False

        async def __call__(
            self,
            configuration: Configuration,
            engine: Engine,
        ) -> int: ...

Configure Command
-------------------------------------------------------------------------------

Non-destructive configuration management following ADR-003 approach:

.. code-block:: python

    class ConfigureCommand( _CliCommand, decorators = ( __.standard_tyro_class, ) ):
        ''' Manages configuration without destructive file editing. '''

        validate: __.typx.Annotated[
            bool,
            __.ddoc.Doc( "Validate existing configuration without analysis." )
        ] = False
        interactive: __.typx.Annotated[
            bool,
            __.ddoc.Doc( "Interactive configuration wizard." )
        ] = False
        display_effective: __.typx.Annotated[
            bool,
            __.ddoc.Doc( "Display effective merged configuration." )
        ] = False

        async def __call__(
            self,
            configuration: Configuration,
            engine: Engine,
        ) -> int: ...

**Configuration Display Behavior:**

The ``display_effective`` option provides comprehensive configuration transparency:

*Default behavior (validation only):*

.. code-block:: text

    $ linter configure --validate
    ✓ Configuration is valid
    ✓ All enabled rules have valid parameters

*With effective configuration display:*

.. code-block:: text

    $ linter configure --display-effective
    Configuration Sources:
      • CLI arguments: --display-effective=true
      • pyproject.toml: /path/to/project/pyproject.toml
      • Built-in defaults

    Effective Configuration:
      [tool.vibelinter]
      output-format = "text"           # default
      jobs = "auto"                    # default
      
      [tool.vibelinter.rules]
      VBL101 = true                    # pyproject.toml
      VBL102 = false                   # pyproject.toml  
      VBL201 = true                    # default
      VBL301 = true                    # default

      [tool.vibelinter.rules.VBL102]
      similarity-threshold = 0.9       # pyproject.toml
      allow-digits = false            # pyproject.toml

    Rule Status:
      ✓ VBL101 (blank-line-elimination): enabled, severity=error
      ✗ VBL102 (simple-naming-conventions): disabled  
      ✓ VBL201 (function-ordering): enabled, severity=warning
      ✓ VBL301 (collection-type-variance): enabled, severity=error

This comprehensive view supports debugging configuration precedence, team onboarding, CI/CD troubleshooting, and configuration validation workflows.

Describe Command
-------------------------------------------------------------------------------

Rule discovery and documentation with context-aware information display:

.. code-block:: python

    class DescribeRulesCommand( _CliCommand, decorators = ( __.standard_tyro_class, ) ):
        ''' Lists all available rules with descriptions. '''

        details: __.typx.Annotated[
            bool,
            __.ddoc.Doc( "Display detailed rule information including configuration status." )
        ] = False

        async def __call__(
            self,
            configuration: Configuration,
            engine: Engine,
        ) -> int: ...

    class DescribeRuleCommand( _CliCommand, decorators = ( __.standard_tyro_class, ) ):
        ''' Displays detailed information for a specific rule. '''

        rule_id: __.tyro.conf.Positional[ str ]
        details: __.typx.Annotated[
            bool,
            __.ddoc.Doc( "Display detailed rule information including configuration status." )
        ] = False

        async def __call__(
            self,
            configuration: Configuration,
            engine: Engine,
        ) -> int: ...

    class DescribeCommand( __.immut.DataclassObject, decorators = ( __.simple_tyro_class, ) ):
        ''' Displays rule information and documentation. '''

        subcommand: __.typx.Union[
            __.typx.Annotated[
                DescribeRulesCommand,
                __.tyro.conf.subcommand( 'rules', prefix_name = False ),
            ],
            __.typx.Annotated[
                DescribeRuleCommand,
                __.tyro.conf.subcommand( 'rule', prefix_name = False ),
            ],
        ]

        async def __call__(
            self,
            configuration: Configuration,
            engine: Engine,
        ) -> int:
            ''' Delegates to selected subcommand. '''
            return await self.subcommand( configuration, engine )

Main CLI Orchestrator
===============================================================================

CLI Controller Design
-------------------------------------------------------------------------------

The main CLI class orchestrates subcommand execution following Librovore patterns:

.. code-block:: python

    class LinterCli( __.immut.DataclassObject, decorators = ( __.simple_tyro_class, ) ):
        ''' Linter command-line interface. '''

        command: __.typx.Union[
            __.typx.Annotated[
                CheckCommand,
                __.tyro.conf.subcommand( 'check', prefix_name = False ),
            ],
            __.typx.Annotated[
                FixCommand,
                __.tyro.conf.subcommand( 'fix', prefix_name = False ),
            ],
            __.typx.Annotated[
                ConfigureCommand,
                __.tyro.conf.subcommand( 'configure', prefix_name = False ),
            ],
            __.typx.Annotated[
                DescribeCommand,
                __.tyro.conf.subcommand( 'describe', prefix_name = False ),
            ],
        ]
        verbose: __.typx.Annotated[
            bool,
            __.ddoc.Doc( "Enable verbose output." )
        ] = False

        async def __call__( self ) -> None:
            ''' Invokes selected subcommand after system preparation. '''

System Integration Design
-------------------------------------------------------------------------------

The CLI orchestrator integrates with core architecture components:

**Configuration Integration:**
- Uses the configuration system from ADR-003 for discovery and loading
- Supports non-destructive management approach with precedence rules
- Handles CLI argument overrides of file-based settings

**Engine Integration:**  
- Coordinates with LinterEngine for analysis and reporting operations
- Manages rule selection and filtering based on CLI options
- Controls parallel processing coordination

**Reporting Integration:**
- Uses reporting system for output formatting across multiple formats
- Manages context display and violation presentation patterns
- Supports deterministic output ordering for CI/CD consistency

Exception Hierarchy
===============================================================================

CLI-Specific Exceptions
-------------------------------------------------------------------------------

CLI operations use the existing package exception hierarchy in ``sources/vibelinter/exceptions.py``:

.. code-block:: python

    class ConfigurationInvalidity( Omnierror, ValueError ):
        ''' Invalid configuration detected. '''
        
        def __init__( self, source: str, problem: str ): ...

    class RuleDiscoverFailure( Omnierror, ImportError ):
        ''' Rule discovery or loading failed. '''
        
        def __init__( self, rule_id: str ): ...

    class FileDiscoverFailure( Omnierror, OSError ):
        ''' File discovery or access failed. '''
        
        def __init__( self, path: str ): ...

Entry Point Design
===============================================================================

CLI Execution Pattern
-------------------------------------------------------------------------------

.. code-block:: python

    def execute( ) -> None:
        ''' Entry point for CLI execution. '''
        # Tyro configuration and exception handling patterns

Exit Code Strategy
-------------------------------------------------------------------------------

Standard linter conventions with BSD sysexits for runtime issues:

**Exit Code 0:** Clean execution with no violations detected
**Exit Code 1:** Violations found during analysis
**Exit Code 66 (EX_NOINPUT):** Cannot open input files
**Exit Code 70 (EX_SOFTWARE):** Internal software error
**Exit Code 74 (EX_IOERR):** Input/output error during processing
**Exit Code 78 (EX_CONFIG):** Configuration file syntax or validation errors

This approach follows established linter patterns (0=clean, 1=violations) while using BSD sysexits codes for precise runtime error reporting. Scripts expecting standard linter behavior work correctly, while automated tooling can distinguish between different types of runtime failures.

Extensibility
===============================================================================

The design accommodates additional subcommands through protocol-specific isolation, maintaining clean separation of concerns without affecting existing subcommand namespaces.

Design Rationale
===============================================================================

Architecture Objectives
-------------------------------------------------------------------------------

This CLI design achieves several key architectural objectives:

**Clean Separation:** Each subcommand operates in isolation with distinct option namespaces, following ADR-004 requirements for avoiding conflicts between operational modes.

**Type Safety:** Dataclass-based commands with comprehensive type annotations provide automatic help generation and runtime validation through Tyro integration.

**Future Extensibility:** Protocol-based design enables addition of server modes and new subcommands without affecting existing functionality.

**Error Handling:** Comprehensive exception hierarchy with appropriate exit codes supports robust CI/CD integration patterns.

**Configuration Integration:** Seamless coordination with established configuration architecture maintains consistency across the system.

**Practices Compliance:** Design follows all established Python practices for imports, naming, module organization, and exception handling patterns.

Implementation Guidelines
-------------------------------------------------------------------------------

**Subcommand Implementation:** Each subcommand focuses solely on its operational mode, delegating core functionality to engine and configuration systems.

**Option Validation:** Use Tyro's built-in validation for type checking and help generation, with custom validation for business logic constraints.

**Resource Management:** Follow established patterns for configuration loading, engine initialization, and proper cleanup in exception scenarios.

**Output Consistency:** All subcommands coordinate through the reporting system to ensure consistent formatting and presentation across operational modes.

The interface specifications provide clear contracts for implementation while maintaining architectural decisions and following established Python development patterns.