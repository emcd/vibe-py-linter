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
Linter Core Framework Design
*******************************************************************************

This document specifies the core linter framework design implementing the validated hybrid modular architecture from ADR-001. The design provides the foundational abstractions for rule implementation, violation collection, and single-pass CST analysis orchestration.

Core Framework Architecture
===============================================================================

Framework Components
-------------------------------------------------------------------------------

The linter core consists of five primary components forming the analysis pipeline:

**Violation Data Structures**
  Immutable data classes representing rule violations with precise location information and context extraction capabilities.

**BaseRule Framework**
  Abstract base class providing the collection-then-analysis pattern with LibCST metadata integration and violation reporting utilities.

**Rule Registry System**
  Bidirectional mapping between VBL codes and rule implementations supporting both code-based and descriptive-name-based configuration.

**Engine Orchestration**
  Central coordinator managing the single-pass analysis pipeline with rule execution, violation collection, and deduplication.

**Context Extraction Utilities**
  Validated patterns for enhancing violation reports with source code context display.

Data Structure Design
===============================================================================

Violation Representation
-------------------------------------------------------------------------------

The violation data structures follow immutable design patterns with precise positioning and context extraction:

.. code-block:: python

    from . import __

    # Core violation data structure
    class Violation( __.immut.DataclassObject ):
        ''' Represents a rule violation with precise location and context information. '''
        rule_id: str
        filename: __.typx.Annotated[ 
            str, __.ddoc.Doc( 'Path to source file containing violation.' ) ]
        line: __.typx.Annotated[ 
            int, __.ddoc.Doc( 'One-indexed line number of violation.' ) ]
        column: __.typx.Annotated[ 
            int, __.ddoc.Doc( 'Zero-indexed column position of violation.' ) ]
        message: __.typx.Annotated[ 
            str, __.ddoc.Doc( 'Human-readable description of violation.' ) ]
        severity: str = 'error'

    # Context extraction for enhanced error reporting
    class ViolationContext( __.immut.DataclassObject ):
        ''' Represents source code context surrounding a violation for enhanced error reporting. '''
        violation: Violation
        context_lines: __.typx.Annotated[
            tuple[ str, ... ], __.ddoc.Doc( 'Source lines surrounding violation.' ) ]
        context_start_line: __.typx.Annotated[
            int, __.ddoc.Doc( 'One-indexed starting line of context display.' ) ]

    # Type aliases for rule framework contracts
    ViolationSequence: __.typx.TypeAlias = __.cabc.Sequence[ Violation ]
    ViolationContextSequence: __.typx.TypeAlias = __.cabc.Sequence[ ViolationContext ]

Exception Hierarchy
-------------------------------------------------------------------------------

Package-specific exceptions following established hierarchy patterns:

.. code-block:: python

    from . import __

    class Omniexception( __.immut.Object, BaseException ):
        ''' Base for all exceptions raised by linter framework. '''

    class Omnierror( Omniexception, Exception ):
        ''' Base for error exceptions raised by linter framework. '''

    # Rule execution exceptions
    class RuleExecuteFailure( Omnierror ):
        ''' Raised when rule execution encounters unrecoverable error. '''

    class MetadataProvideFailure( Omnierror ):
        ''' Raised when LibCST metadata provider initialization fails. '''

    # Configuration exceptions  
    class RuleRegistryInvalidity( Omnierror ):
        ''' Raised when rule registry contains invalid mappings. '''

    class RuleConfigureFailure( Omnierror ):
        ''' Raised when rule configuration parameters are invalid. '''

BaseRule Framework Design
===============================================================================

Abstract Base Class Interface
-------------------------------------------------------------------------------

The BaseRule framework implements the validated collection-then-analysis pattern with LibCST integration:

.. code-block:: python

    from . import __

    class BaseRule( __.abc.ABC, __.libcst.CSTVisitor ):
        ''' Abstract base class for linting rules implementing collection-then-analysis pattern.
        
            Rules collect data during CST traversal and perform analysis in leave_Module to
            generate violations. This pattern supports complex rules requiring complete
            information before analysis can occur.
        '''
        
        METADATA_DEPENDENCIES = (
            __.libcst.metadata.PositionProvider,
            __.libcst.metadata.ScopeProvider, 
            __.libcst.metadata.QualifiedNameProvider,
        )

        def __init__(
            self, 
            filename: __.typx.Annotated[
                str, __.ddoc.Doc( 'Path to source file being analyzed.' ) ],
            wrapper: __.typx.Annotated[
                __.libcst.MetadataWrapper,
                __.ddoc.Doc( 'LibCST metadata wrapper providing position and scope information.' ) ],
            source_lines: __.typx.Annotated[
                tuple[ str, ... ], __.ddoc.Doc( 'Source file lines for context extraction.' ) ],
        ) -> None: ...

        @property
        @__.abc.abstractmethod
        def rule_id( self ) -> __.typx.Annotated[
            str, __.ddoc.Doc( 'Unique identifier for rule (VBL code).' ) ]: ...

        @property  
        def violations( self ) -> tuple[ Violation, ... ]:
            ''' Returns violations generated by rule analysis. '''

        def leave_Module( 
            self, node: __.libcst.Module 
        ) -> __.typx.Optional[ __.libcst.Module ]:
            ''' Performs collection analysis after CST traversal completes.
            
                Subclasses must override _analyze_collections to implement rule-specific
                analysis logic using collected data.
            '''

        @__.abc.abstractmethod  
        def _analyze_collections( self ) -> None:
            ''' Analyzes collected data and generates violations.
            
                Called by leave_Module after traversal completes. Implementations
                should examine collected data and call _produce_violation for 
                any violations discovered.
            '''

        def _produce_violation(
            self,
            node: __.libcst.CSTNode,
            message: __.typx.Annotated[
                str, __.ddoc.Doc( 'Human-readable violation description.' ) ],
            severity: str = 'error',
        ) -> None:
            ''' Creates violation from CST node with precise positioning. '''

        def _extract_context(
            self, 
            line: __.typx.Annotated[ int, __.ddoc.Doc( 'One-indexed line number.' ) ],
            context_size: int = 2,
        ) -> ViolationContext:
            ''' Extracts source code context around violation for enhanced reporting. '''

        def _position_from_node(
            self, node: __.libcst.CSTNode
        ) -> tuple[ int, int ]:
            ''' Extracts (line, column) position from CST node using metadata. '''

Rule Registry Design
===============================================================================

VBL Code Mapping System
-------------------------------------------------------------------------------

The registry provides bidirectional mapping between VBL codes and rule implementations:

.. code-block:: python

    from . import __

    # Rule registry data structures
    class RuleDescriptor( __.immut.DataclassObject ):
        ''' Describes rule metadata for registry and configuration systems. '''
        odr_code: __.typx.Annotated[
            str, __.ddoc.Doc( 'VBL code identifier (e.g., "VBL101").' ) ]
        descriptive_name: __.typx.Annotated[
            str, __.ddoc.Doc( 'Hyphen-separated descriptive name (e.g., "blank-line-elimination").' ) ]
        description: __.typx.Annotated[
            str, __.ddoc.Doc( 'Human-readable rule description.' ) ]
        category: __.typx.Annotated[
            str, __.ddoc.Doc( 'Rule category (readability, discoverability, robustness).' ) ]
        subcategory: __.typx.Annotated[
            str, __.ddoc.Doc( 'Rule subcategory (compactness, nomenclature, navigation, etc.).' ) ]
        rule_class: __.typx.Annotated[
            str, __.ddoc.Doc( 'Fully qualified class name for rule implementation.' ) ]

    RuleRegistry: __.typx.TypeAlias = __.immut.Dictionary[ str, RuleDescriptor ]
    RuleClassFactory: __.typx.TypeAlias = __.cabc.Callable[ 
        [ str, __.libcst.MetadataWrapper, tuple[ str, ... ] ], BaseRule ]
    ''' Factory function type for creating rule instances.
    
        Used by the rule registry system to instantiate rules dynamically
        based on VBL codes. Takes filename, LibCST metadata wrapper, and
        source lines as parameters, returns configured rule instance ready
        for analysis.
        
        This enables the registry to support rules with different constructor
        signatures while maintaining a consistent instantiation interface.
        The registry can map VBL codes to factory functions that handle any
        rule-specific initialization requirements while presenting a uniform
        API to the engine.
    '''

    # Registry interface  
    class RuleRegistryManager:
        ''' Manages bidirectional mapping between VBL codes and rule implementations. '''

        def __init__( 
            self, registry: __.cabc.Mapping[ str, RuleDescriptor ] 
        ) -> None: ...

        def resolve_rule_identifier(
            self, identifier: __.typx.Annotated[
                str, __.ddoc.Doc( 'VBL code or descriptive name to resolve.' ) ]
        ) -> __.typx.Annotated[
            str, __.ddoc.Doc( 'Canonical VBL code for identifier.' ),
            __.ddoc.Raises( RuleRegistryInvalidity, 'If identifier is not registered.' ),
        ]: ...

        def produce_rule_instance(
            self,
            odr_code: __.typx.Annotated[ str, __.ddoc.Doc( 'VBL code for rule.' ) ],
            filename: str,
            wrapper: __.libcst.MetadataWrapper,
            source_lines: tuple[ str, ... ],
        ) -> __.typx.Annotated[
            BaseRule, 
            __.ddoc.Doc( 'Instantiated rule ready for analysis.' ),
            __.ddoc.Raises( RuleRegistryInvalidity, 'If VBL code is not registered.' ),
        ]: ...

        def survey_available_rules( self ) -> tuple[ RuleDescriptor, ... ]:
            ''' Returns all registered rule descriptors sorted by VBL code. '''

        def filter_rules_by_category(
            self, 
            category: __.typx.Annotated[ str, __.ddoc.Doc( 'Category to filter by.' ) ]
        ) -> tuple[ RuleDescriptor, ... ]:
            ''' Returns rule descriptors matching specified category. '''

Engine Design  
===============================================================================

Orchestration Interface
-------------------------------------------------------------------------------

The Engine coordinates single-pass analysis with rule execution and violation collection:

.. code-block:: python

    from . import __

    # Engine configuration  
    class EngineConfiguration( __.immut.DataclassObject ):
        ''' Configuration for linter engine behavior and rule selection. '''
        enabled_rules: __.typx.Annotated[
            frozenset[ str ], __.ddoc.Doc( 'VBL codes of rules to execute.' ) ]
        rule_parameters: __.typx.Annotated[
            __.immut.Dictionary[ str, __.immut.Dictionary[ str, __.typx.Any ] ],
            __.ddoc.Doc( 'Rule-specific configuration parameters indexed by VBL code.' ) ]
        context_size: __.typx.Annotated[
            int, __.ddoc.Doc( 'Number of context lines to extract around violations.' ) ] = 2
        include_context: __.typx.Annotated[
            bool, __.ddoc.Doc( 'Whether to extract source context for violations.' ) ] = True

    # Analysis results
    class Report( __.immut.DataclassObject ):
        ''' Results of linting analysis including violations and metadata. '''
        violations: tuple[ Violation, ... ]
        contexts: __.typx.Annotated[
            tuple[ ViolationContext, ... ],
            __.ddoc.Doc( 'Violation contexts when context extraction enabled.' ) ]
        filename: str
        rule_count: __.typx.Annotated[
            int, __.ddoc.Doc( 'Number of rules executed during analysis.' ) ]
        analysis_duration_ms: __.typx.Annotated[
            float, __.ddoc.Doc( 'Time spent in analysis phase excluding parsing.' ) ]

    # Engine orchestration interface
    class Engine:
        ''' Central orchestrator for linting analysis implementing single-pass CST traversal. '''

        def __init__(
            self,
            registry_manager: __.typx.Annotated[
                RuleRegistryManager, __.ddoc.Doc( 'Rule registry for instantiating rules.' ) ],
            configuration: __.typx.Annotated[
                EngineConfiguration, __.ddoc.Doc( 'Engine configuration and rule selection.' ) ],
        ) -> None: ...

        def lint_file(
            self, 
            file_path: __.typx.Annotated[
                __.pathlib.Path, __.ddoc.Doc( 'Path to Python source file to analyze.' ) ]
        ) -> __.typx.Annotated[
            Report,
            __.ddoc.Doc( 'Analysis results including violations and metadata.' ),
            __.ddoc.Raises( RuleExecuteFailure, 'If rule execution fails unrecoverably.' ),
            __.ddoc.Raises( MetadataProvideFailure, 'If LibCST metadata initialization fails.' ),
        ]: ...

        def lint_source(
            self,
            source_code: __.typx.Annotated[
                str, __.ddoc.Doc( 'Python source code to analyze.' ) ],
            filename: __.typx.Annotated[
                str, __.ddoc.Doc( 'Logical filename for source code.' ) ] = '<string>',
        ) -> __.typx.Annotated[
            Report,
            __.ddoc.Doc( 'Analysis results including violations and metadata.' ),
            __.ddoc.Raises( RuleExecuteFailure, 'If rule execution fails unrecoverably.' ),
            __.ddoc.Raises( MetadataProvideFailure, 'If LibCST metadata initialization fails.' ),
        ]: ...

        def lint_files(
            self, 
            file_paths: __.cabc.Sequence[ __.pathlib.Path ]
        ) -> __.typx.Annotated[
            tuple[ Report, ... ],
            __.ddoc.Doc( 'Analysis results for all files.' ),
        ]: ...

Context Extraction Utilities
===============================================================================

Enhanced Error Reporting
-------------------------------------------------------------------------------

Context extraction provides validated patterns for displaying source code around violations:

.. code-block:: python

    from . import __

    class ContextExtractor:
        ''' Utilities for extracting source code context around violations for enhanced reporting. '''

        def __init__( 
            self, source_lines: tuple[ str, ... ] 
        ) -> None: ...

        def extract_violation_context(
            self,
            violation: Violation,
            context_size: __.typx.Annotated[
                int, __.ddoc.Doc( 'Number of lines to show before and after violation.' ) ] = 2,
        ) -> __.typx.Annotated[
            ViolationContext,
            __.ddoc.Doc( 'Violation with surrounding source context.' ),
        ]: ...

        def format_context_display(
            self,
            context: ViolationContext,
            highlight_line: __.typx.Annotated[
                bool, __.ddoc.Doc( 'Whether to highlight the violation line.' ) ] = True,
        ) -> __.typx.Annotated[
            tuple[ str, ... ],
            __.ddoc.Doc( 'Formatted context lines with line numbers and highlighting.' ),
        ]: ...

    # Context extraction utilities
    def extract_contexts_for_violations(
        violations: ViolationSequence,
        source_lines: __.cabc.Sequence[ str ],
        context_size: int = 2,
    ) -> ViolationContextSequence:
        ''' Extracts contexts for multiple violations efficiently. '''

Module Organization Design
===============================================================================

Framework Module Structure
-------------------------------------------------------------------------------

The linter core modules follow established filesystem organization patterns:

.. code-block::

    sources/vibelinter/
    ├── __/                          # Centralized import hub
    │   ├── __init__.py              # Core framework imports
    │   ├── imports.py               # External dependencies (libcst)  
    │   └── nomina.py                # Framework naming constants
    ├── engine.py                    # Engine orchestration
    ├── rules/                       # Rule framework and implementations
    │   ├── __.py                    # Rule-specific imports
    │   ├── __init__.py              # Rule package entry point
    │   ├── base.py                  # BaseRule abstract class
    │   ├── registry.py              # RuleRegistryManager implementation
    │   ├── context.py               # ContextExtractor utilities
    │   └── violations.py            # Violation data structures

Import Hub Design
-------------------------------------------------------------------------------

The framework imports are organized through the centralized ``__`` pattern:

.. code-block:: python

    # sources/vibelinter/__/imports.py - External dependencies
    import libcst
    import libcst.metadata

    # sources/vibelinter/__/__init__.py - Framework exports
    from . import imports
    from .. import exceptions
    from ..rules import violations, base, registry, context

    # sources/vibelinter/rules/__.py - Rule-specific imports  
    from ..__ import *
    from . import violations, base, registry, context

Type Organization
-------------------------------------------------------------------------------

Type aliases are organized by usage domain and dependency relationships:

.. code-block:: python

    # sources/vibelinter/rules/violations.py
    from ..__ import *

    # Core violation types defined here
    class Violation( __.immut.DataclassObject ): ...
    class ViolationContext( __.immut.DataclassObject ): ...

    # Type aliases for framework contracts
    ViolationSequence: __.typx.TypeAlias = __.cabc.Sequence[ Violation ]
    ViolationContextSequence: __.typx.TypeAlias = __.cabc.Sequence[ ViolationContext ]

    # sources/vibelinter/rules/base.py
    from . import __

    # BaseRule depends on violation types
    class BaseRule( __.abc.ABC, __.libcst.CSTVisitor ): ...

Design Validation
===============================================================================

Framework Compliance Verification
-------------------------------------------------------------------------------

The design adheres to established practices and patterns:

**Practices Compliance:**
- Wide parameter types (__.cabc.Sequence, __.cabc.Mapping) for public interfaces
- Narrow return types (tuple, __.immut.Dictionary) for concrete results
- Immutable data structures using __.immut.DataclassObject patterns
- Exception hierarchy following Omniexception → Omnierror patterns
- Type annotations with __.typx.TypeAlias for complex types

**Style Compliance:**  
- Function signatures follow spacing and bracket conventions
- Docstrings use narrative mood with triple single-quotes
- Type annotations use proper __.typx.Annotated patterns with __.ddoc documentation

**Nomenclature Compliance:**
- Class names follow established patterns (Manager, Extractor, Engine suffixes)
- Function names use verb_noun patterns (extract_context, produce_violation)
- Module organization follows established filesystem patterns
- VBL codes maintain semantic series organization

**Architecture Compliance:**
- Single-pass CST traversal with metadata providers
- Collection-then-analysis pattern for complex rule implementation
- Context extraction for enhanced error reporting  
- Rule registry system supporting both VBL codes and descriptive names

Implementation Readiness
-------------------------------------------------------------------------------

The design provides complete interface specifications for:

- Validated LibCST integration patterns from proof-of-concept
- Performance-optimized single-pass analysis achieving 600ms target
- Collection-then-analysis pattern supporting complex rules
- Context extraction enhancing developer experience
- Rule registry supporting configuration flexibility
- Exception handling with proper error propagation

Configuration vs. Registry Architectural Separation
===============================================================================

Design Decision Rationale
-------------------------------------------------------------------------------

The linter core framework maintains deliberate separation between Configuration and Registry systems:

**Registry System Responsibilities:**
- Provides metadata about available rules (VBL codes, descriptive names, categories)
- Manages rule instantiation patterns and factory functions
- Handles bidirectional mapping between VBL codes and rule implementations
- Maintains rule capabilities and documentation references

**Configuration System Responsibilities:**
- Manages user preferences for rule enablement and parameters
- Handles command-line overrides and project-specific settings
- Applies precedence rules across configuration sources
- Validates user-provided configuration values

**Separation Rationale:**
- **Command-Query Separation**: Registry queries rule information, Configuration commands execution behavior
- **Independent Evolution**: Registry changes when rules are added/modified, Configuration changes when user requirements evolve
- **Single Responsibility**: Registry focuses on "what rules exist and how to create them," Configuration focuses on "which rules to run and with what settings"
- **Testability**: Registry can be tested with static rule metadata, Configuration tested with dynamic user preferences
- **Extensibility**: Registry supports rule discovery and introspection, Configuration supports customization and overrides

This architectural separation enables the rule framework to evolve independently from user preference management while maintaining clear interfaces between rule metadata and execution configuration.

The framework design enables immediate implementation of the core linting engine following the validated architectural decisions and proven performance characteristics.