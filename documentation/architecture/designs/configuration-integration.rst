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
Configuration Integration Design
*******************************************************************************

This document specifies the integration between python-linter's TOML-based configuration system and the emcd-appcore package's configuration management infrastructure.

Design Overview
===============================================================================

The configuration integration bridges python-linter's project-specific TOML configuration requirements with emcd-appcore's standardized configuration infrastructure, providing a unified configuration hierarchy while maintaining compatibility with both systems.

**Integration Goals:**

- Preserve ADR-003 layered precedence model
- Use simple functions for pyproject.toml discovery and loading
- Leverage emcd-appcore's standard preparation and configuration merging
- Support Tyro dataclass-based CLI command integration  
- Enable command-line configuration overrides through dataclass attributes
- Maintain zero-configuration operation with sensible defaults

Configuration Architecture
===============================================================================

Configuration Sources Integration
-------------------------------------------------------------------------------

The integration maintains ADR-003's precedence hierarchy while adapting to emcd-appcore's TomlAcquirer system:

.. code-block:: text

    ┌─────────────────────┐
    │ CLI Arguments       │ ◄─── Highest precedence
    │ (runtime overrides) │
    └─────────────────────┘
              │
    ┌─────────────────────┐
    │ pyproject.toml      │ ◄─── Project configuration
    │ [tool.vibelinter]        │
    └─────────────────────┘
              │
    ┌─────────────────────┐
    │ emcd-appcore        │ ◄─── Base application infrastructure
    │ Built-in Defaults   │
    └─────────────────────┘

**Configuration Flow:**

1. **Base Configuration**: emcd-appcore provides application infrastructure configuration
2. **Project Configuration**: TomlAcquirer loads pyproject.toml [tool.vibelinter] sections
3. **CLI Overrides**: Command-line arguments override project configuration through configedits

Interface Specifications
===============================================================================

Configuration Discovery and Loading
-------------------------------------------------------------------------------

.. code-block:: python

    def discover_pyproject_toml(
        start_path: __.Path,
        max_depth: int = 5,
    ) -> __.Absential[ __.Path ]:
        ''' Discovers pyproject.toml by traversing directory hierarchy. '''

    def acquire_configuration(
        pyproject_path: __.Path,
    ) -> __.immut.Dictionary[ str, __.typx.Any ]:
        ''' Acquires [tool.vibelinter] section from pyproject.toml. '''

**Configuration Merging Pattern:**

.. code-block:: python

    def merge_configurations(
        appcore: __.accret.Dictionary[ str, __.typx.Any ],
        pyproject: __.cabc.Mapping[ str, __.typx.Any ],
    ) -> __.accret.Dictionary[ str, __.typx.Any ]:
        ''' Merges pyproject.toml configuration with appcore base configuration. '''


Configuration Schema Integration
-------------------------------------------------------------------------------

.. code-block:: python

    ConfigurationSchema: __.typx.TypeAlias = __.typx.TypedDict(
        'ConfigurationSchema', {
            # Global settings
            'render_as': str,              # text, json, structured
            'display_source': bool,
            'exit_zero': bool,
            
            # Rule configuration
            'rules': __.cabc.Mapping[ str, __.cabc.Mapping[ str, __.typx.Any ] ],
            
            # Severity overrides
            'severity': __.cabc.Mapping[ str, str ],
        }, total = False
    )

**Rule Configuration Structure:**

.. code-block:: python

    RuleConfiguration: __.typx.TypeAlias = __.typx.TypedDict(
        'RuleConfiguration', {
            'enabled': bool,
            'severity': str,               # error, warning, info
            'parameters': __.cabc.Mapping[ str, __.typx.Any ],
        }, total = False
    )

CLI Integration Pattern
-------------------------------------------------------------------------------

.. code-block:: python

    async def prepare_configuration(
        exits: __.ctxl.AsyncExitStack,
        cli_command: CliCommand,
        project_root: __.Absential[ __.Path ] = __.absent,
    ) -> __.appcore.state.Globals:
        ''' Prepares configuration with application-specific settings. '''

Configuration Access Patterns
===============================================================================

Configuration Reader Interface
-------------------------------------------------------------------------------

.. code-block:: python

    class ConfigurationReader( __.immut.DataclassObject ):
        ''' Provides typed access to configuration values. '''
        
        configuration: __.accret.Dictionary[ str, __.typx.Any ]
        
        def access_render_format( self ) -> str:
            ''' Accesses render format setting with default fallback. '''
        
        def access_rule_configuration(
            self,
            rule_id: str,
        ) -> RuleConfiguration:
            ''' Accesses rule-specific configuration. '''
        
        def access_rule_enablement(
            self,
            rule_id: str,
        ) -> bool:
            ''' Accesses rule enablement status. '''
        
        def access_rule_severity(
            self,
            rule_id: str,
        ) -> str:
            ''' Accesses rule severity level. '''
        
        def access_rule_parameters(
            self,
            rule_id: str,
        ) -> __.immut.Dictionary[ str, __.typx.Any ]:
            ''' Accesses rule-specific parameters. '''

Rule Registry Integration
-------------------------------------------------------------------------------

.. code-block:: python

    class ConfigurationValidator( __.immut.DataclassObject ):
        ''' Validates configuration against rule registry. '''
        
        registry: __.cabc.Mapping[ str, __.cabc.Mapping[ str, __.typx.Any ] ]
        
        def validate_rule_references(
            self,
            configuration: __.cabc.Mapping[ str, __.typx.Any ],
        ) -> tuple[ str, ... ]:
            ''' Validates rule ID references against registry. '''
        
        def validate_rule_parameters(
            self,
            rule_id: str,
            parameters: __.cabc.Mapping[ str, __.typx.Any ],
        ) -> tuple[ str, ... ]:
            ''' Validates rule parameters against schema. '''

Configuration Examples
===============================================================================

Basic pyproject.toml Integration
-------------------------------------------------------------------------------

.. code-block:: toml

    [tool.vibelinter]
    render-as = "text"
    display-source = true
    exit-zero = false

    [tool.vibelinter.rules]
    VBL101 = true                    # blank-line-elimination
    VBL102 = false                   # simple-naming-conventions
    blank-line-elimination = true    # alternative descriptive syntax
    
    [tool.vibelinter.rules.VBL102]        # rule-specific parameters
    similarity-threshold = 0.85
    allow-digits = true
    
    [tool.vibelinter.severity]
    VBL101 = "error"
    VBL102 = "info"

CLI Override Examples
-------------------------------------------------------------------------------

.. code-block:: shell

    # Override render format (via dataclass attribute)
    linter check --render-as=json src/
    
    # Override rule enablement (via dataclass attribute)
    linter check --disable-rule=VBL101 src/
    
    # Override rule parameters (via dataclass attribute)
    linter check --rule-config=VBL102.similarity_threshold=0.9 src/

Integration Workflow
===============================================================================

Application Initialization
-------------------------------------------------------------------------------

.. code-block:: python

    async def prepare_application(
        exits: __.ctxl.AsyncExitStack,
        cli_command: CliCommand,
    ) -> __.appcore.state.Globals:
        ''' Prepares application with integrated configuration. '''
        
        # Use standard appcore preparation
        auxdata = await __.appcore.preparation.prepare(
            exits = exits,
            environment = True,
        )
        
        # Discover pyproject.toml from project root
        project_root = auxdata.distribution.provide_data_location( ).parent
        pyproject_path = discover_pyproject_toml( project_root )
        
        # Merge configurations if pyproject.toml exists
        # Apply CLI overrides via configuration edits
        # Return updated auxdata with final configuration

Configuration Access Pattern
-------------------------------------------------------------------------------

.. code-block:: python

    async def execute_linting_workflow(
        auxdata: __.appcore.state.Globals,
        targets: __.cabc.Sequence[ __.Path ],
    ) -> None:
        ''' Executes linting with configuration-driven behavior. '''
        
        # Access configuration through reader interface
        config_reader = ConfigurationReader( auxdata.configuration )
        
        # Configure rendering based on settings
        render_format = config_reader.access_render_format( )
        
        # Configure rules based on settings
        enabled_rules = [
            rule_id for rule_id in AVAILABLE_RULES
            if config_reader.access_rule_enablement( rule_id )
        ]

Default Configuration Strategy
===============================================================================

Built-in Defaults
-------------------------------------------------------------------------------

.. code-block:: python

    DEFAULT_CONFIGURATION: __.immut.Dictionary[ str, __.typx.Any ] = __.immut.Dictionary(
        render_as = 'text',
        display_source = True,
        exit_zero = False,
        rules = __.immut.Dictionary(
            # All rules enabled by default
            VBL101 = True,
            VBL102 = True,
            VBL201 = True,
            VBL301 = True,
        ),
        severity = __.immut.Dictionary(
            # Default severity levels
            VBL101 = 'error',
            VBL102 = 'error', 
            VBL201 = 'warning',
            VBL301 = 'warning',
        ),
    )

Configuration Discovery Fallback
-------------------------------------------------------------------------------

.. code-block:: python

    def provide_fallback_configuration( ) -> __.immut.Dictionary[ str, __.typx.Any ]:
        ''' Provides fallback when no project configuration exists. '''
        
        # Return copy of defaults for zero-configuration operation
        return __.immut.Dictionary( DEFAULT_CONFIGURATION )

Error Handling Specifications
===============================================================================

Configuration Exception Hierarchy
-------------------------------------------------------------------------------

.. code-block:: python

    class ConfigurationOmnierror( __.Omnierror ):
        ''' Base for configuration-related errors. '''

    class ConfigurationDiscoverFailure( ConfigurationOmnierror ):
        ''' Configuration file discovery failed. '''
    
    class ConfigurationParseFailure( ConfigurationOmnierror ):
        ''' Configuration parsing failed. '''
    
    class ConfigurationValidateFailure( ConfigurationOmnierror ):
        ''' Configuration validation failed. '''
    
    class RuleReferenceInvalidity( ConfigurationOmnierror ):
        ''' Invalid rule reference in configuration. '''

Validation Error Handling
-------------------------------------------------------------------------------

.. code-block:: python

    def validate_and_report_configuration(
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
    ) -> __.cabc.Sequence[ str ]:
        ''' Validates configuration and returns error messages. '''

**Error Recovery Strategy:**

- Invalid rule references: Log warnings, continue with valid rules
- Invalid parameters: Use parameter defaults, log warnings
- Parse errors: Fall back to built-in defaults, report error
- Discovery failures: Use built-in defaults, operate in zero-configuration mode

Integration Benefits
===============================================================================

**Architecture Benefits:**

- **Consistency**: Unified configuration infrastructure across application
- **Immutability**: Leverages emcd-appcore's immutable configuration model
- **Extensibility**: Easy addition of new configuration sections and parameters
- **Type Safety**: Strong typing through TypedDict schemas and validation
- **Error Handling**: Comprehensive validation with graceful fallback

**Development Benefits:**

- **Zero Configuration**: Works without any configuration files
- **Project Integration**: Natural pyproject.toml integration for Python projects
- **CLI Flexibility**: Runtime overrides for development and CI/CD workflows
- **Schema Evolution**: Backward-compatible configuration updates

**Operational Benefits:**

- **Debugging**: Clear configuration precedence and source tracking
- **Validation**: Early detection of configuration errors with helpful messages
- **Performance**: Cached configuration access with immutable structures
- **Testing**: Easy configuration mocking and override for tests

Implementation Dependencies
===============================================================================

**External Dependencies:**

- ``emcd-appcore``: Configuration infrastructure and application preparation
- ``accretive``: Immutable dictionary implementation
- ``absence``: Optional value handling
- ``platformdirs``: Platform-specific directory management

**Internal Dependencies:**

- Rule registry system for validation
- Exception hierarchy for error handling
- CLI argument processing for configuration edits
- File discovery utilities for project configuration location

This design ensures seamless integration between python-linter's domain-specific configuration requirements and emcd-appcore's standardized application infrastructure, maintaining both systems' architectural principles while providing a unified configuration experience.