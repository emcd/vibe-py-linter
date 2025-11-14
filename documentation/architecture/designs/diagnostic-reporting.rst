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
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Diagnostic and Report Formatting Design
*******************************************************************************

This document specifies the diagnostic and report formatting system implementing REQ-007's sophisticated error reporting requirements. The design provides multi-format output capabilities, precise positioning, and context display.

Design Philosophy
===============================================================================

The design focuses on the essential components needed for sophisticated error reporting:

**Architecture Goal**: Provide excellent developer experience with clear, contextual error reporting
**Integration Focus**: Seamless compatibility with the validated linter core framework

Essential Components
===============================================================================

The diagnostic system consists of four core components:

**Enhanced Diagnostic Structure**
  Embeds existing `Violation` objects with additional metadata for sophisticated presentation.

**Context Display System**
  Reuses validated context extraction from POC with enhanced presentation options.

**Unified Report Structure**
  Single report type handling both individual files and aggregate analysis results.

**Pluggable Renderer System**
  Simple protocol-based renderers for text, JSON, and structured output formats.

Enhanced Diagnostic Design
===============================================================================

Diagnostic Structure
-------------------------------------------------------------------------------

The diagnostic system extends existing violations with essential metadata:

.. code-block:: python

    from . import __

    class DiagnosticSeverity( __.enum.Enum ):
        ''' Diagnostic severity levels with deterministic ordering. '''
        Info = 'info'
        Warning = 'warning'
        Error = 'error'

        @property
        def sort_order( self ) -> int:
            ''' Returns numeric value for deterministic sorting. '''

    class Diagnostic( __.immut.DataclassObject ):
        ''' Enhanced diagnostic embedding existing violation with presentation metadata.
        
            Diagnostics extend the validated Violation structure with additional
            information needed for sophisticated error reporting while maintaining
            compatibility with the existing linter core framework.
        '''
        violation: __.typx.Annotated[
            __.violations.Violation, __.ddoc.Doc( 'Core violation from linter framework.' ) ]
        rule_name: __.typx.Annotated[
            str, __.ddoc.Doc( 'Human-readable rule name for display.' ) ]
        category: __.typx.Annotated[
            str, __.ddoc.Doc( 'Rule category (readability, discoverability, robustness).' ) ]
        severity: DiagnosticSeverity
        auto_fixable: __.typx.Annotated[
            bool, __.ddoc.Doc( 'Whether diagnostic supports automatic fixing.' ) ] = False
        documentation_url: __.typx.Annotated[
            __.Absential[ str ], __.ddoc.Doc( 'URL to rule documentation.' ) ] = __.absent

        @property
        def location_sort_key( self ) -> tuple[ str, int, int ]:
            ''' Returns sortable key for deterministic diagnostic ordering. '''

        @property  
        def filename( self ) -> str:
            ''' Returns filename from embedded violation for convenience. '''

        @property
        def line( self ) -> int:
            ''' Returns line number from embedded violation for convenience. '''

        @property
        def column( self ) -> int:
            ''' Returns column from embedded violation for convenience. '''

        @property
        def message( self ) -> str:
            ''' Returns message from embedded violation for convenience. '''

Design Rationale: Violation vs Diagnostic Distinction
-------------------------------------------------------------------------------

The diagnostic system embeds existing ``Violation`` objects rather than replacing them to maintain clear separation of concerns:

**Violation** (Core Rule Execution Data)
    Contains essential detection information generated during rule analysis:
    
    - Location data (filename, line, column)  
    - Core message describing the violation
    - Rule identifier (VBL code)
    - Basic severity level
    
    Violations focus on **what went wrong** and **where it occurred** without carrying presentation overhead.

**Diagnostic** (Enhanced Presentation Layer)
    Adds metadata for sophisticated error reporting by consulting the rule registry:
    
    - Human-readable rule names for display
    - Category classification for organization
    - Auto-fixable capability flags  
    - Documentation URLs for guidance
    - Enhanced severity enum with deterministic ordering
    
    Diagnostics focus on **how to present violations** and **what can be done about them**.

This separation allows:

- **Rules** to remain focused on detection logic without presentation concerns
- **Presentation metadata** to be managed centrally in the rule registry
- **Multiple presentation layers** to enhance the same violations differently
- **Core violation data** to remain lightweight and performance-optimized

The embedded approach avoids duplication while providing a clear upgrade path from basic rule output to sophisticated error reporting.

Context Display System
===============================================================================

Enhanced Context Presentation
-------------------------------------------------------------------------------

The context system reuses the validated POC pattern with enhanced presentation:

.. code-block:: python

    from . import __

    class ContextStyle( __.enum.Enum ):
        ''' Context presentation styles for different output needs. '''
        Plain = 'plain'       # No formatting, just line numbers
        Highlighted = 'highlighted'  # Violation line marked with >
        Compact = 'compact'   # Minimal context for space-constrained output

    class SourceContext( __.immut.DataclassObject ):
        ''' Source code context with presentation formatting from validated POC patterns.
        
            Extends the proven context extraction from blank_line_rule_poc.py
            with configurable presentation styles for different output formats.
        '''
        filename: str
        violation_line_number: __.typx.Annotated[
            int, __.ddoc.Doc( 'One-indexed line containing violation.' ) ]
        context_lines: __.typx.Annotated[
            tuple[ str, ... ], __.ddoc.Doc( 'Source lines including violation and surrounding context.' ) ]
        context_line_number: __.typx.Annotated[
            int, __.ddoc.Doc( 'One-indexed line number of first context line.' ) ]
        style: ContextStyle

        def format_for_display( self ) -> tuple[ str, ... ]:
            ''' Returns formatted context lines with line numbers and violation markers. '''

        def get_line_number_width( self ) -> int:
            ''' Returns character width needed for line number formatting. '''

    class ContextExtractor:
        ''' Context extraction serving both rule framework and diagnostic reporting with configurable presentation. '''

        def __init__(
            self,
            source_lines: __.typx.Annotated[
                tuple[ str, ... ], __.ddoc.Doc( 'Source file lines for extraction.' ) ],
            style_default: ContextStyle = ContextStyle.Highlighted,
        ) -> None: ...

        def extract_context(
            self,
            filename: str,
            line_number: int,
            context_size: __.typx.Annotated[
                int, __.ddoc.Doc( 'Lines to show before and after violation.' ) ] = 2,
        ) -> __.typx.Annotated[
            SourceContext,
            __.ddoc.Doc( 'Source context for specified line.' ),
        ]: ...

        def extract_multiple_contexts(
            self,
            locations: __.cabc.Sequence[ tuple[ str, int ] ],
            context_size: int = 2,
        ) -> __.typx.Annotated[
            tuple[ SourceContext, ... ],
            __.ddoc.Doc( 'Optimized context extraction for multiple locations.' ),
        ]: ...

Unified Report Structure
===============================================================================

Single Report Type
-------------------------------------------------------------------------------

The report system uses one structure for both single files and aggregates:

.. code-block:: python

    from . import __

    class Report( __.immut.DataclassObject ):
        ''' Unified diagnostic report supporting both single files and aggregates.
        
            Simplifies the reporting architecture by using one structure that
            scales from single file analysis to multi-file aggregate results.
        '''
        diagnostics: __.typx.Annotated[
            tuple[ Diagnostic, ... ], __.ddoc.Doc( 'All diagnostics sorted deterministically.' ) ]
        contexts: __.typx.Annotated[
            tuple[ SourceContext, ... ],
            __.ddoc.Doc( 'Source contexts when context extraction enabled.' ) ]
        files: __.typx.Annotated[
            tuple[ str, ... ], __.ddoc.Doc( 'Files analyzed in this report.' ) ]
        metadata: __.typx.Annotated[
            __.immut.Dictionary[ str, __.typx.Any ],
            __.ddoc.Doc( 'Analysis metadata including timing and configuration.' ) ]

        def diagnostic_count( self ) -> int:
            ''' Returns total number of diagnostics in report. '''

        def error_count( self ) -> int:
            ''' Returns number of error-severity diagnostics. '''

        def warning_count( self ) -> int:
            ''' Returns number of warning-severity diagnostics. '''

        def files_with_errors( self ) -> tuple[ str, ... ]:
            ''' Returns filenames containing error-level diagnostics. '''

        def exit_code( self ) -> int:
            ''' Returns appropriate exit code for CI/CD integration. '''

    class ReportAssembler:
        ''' Assembles diagnostics into reports with deterministic ordering and context extraction. '''

        def __init__(
            self,
            include_contexts: __.typx.Annotated[
                bool, __.ddoc.Doc( 'Whether to extract source contexts.' ) ] = True,
            context_style: ContextStyle = ContextStyle.Highlighted,
            sort_diagnostics: __.typx.Annotated[
                bool, __.ddoc.Doc( 'Whether to sort diagnostics deterministically.' ) ] = True,
        ) -> None: ...

        def assemble_file_report(
            self,
            filename: str,
            violations: __.cabc.Sequence[ __.violations.Violation ],
            source_lines: __.cabc.Sequence[ str ],
            rule_registry: __.cabc.Mapping[ str, __.typx.Any ],
        ) -> __.typx.Annotated[
            Report,
            __.ddoc.Doc( 'Complete report for single file with enhanced diagnostics.' ),
        ]: ...

        def assemble_aggregate_report(
            self,
            file_reports: __.cabc.Sequence[ Report ],
        ) -> __.typx.Annotated[
            Report,
            __.ddoc.Doc( 'Aggregate report combining multiple file reports.' ),
        ]: ...

        def convert_violations_to_diagnostics(
            self,
            violations: __.cabc.Sequence[ __.violations.Violation ],
            rule_registry: __.cabc.Mapping[ str, __.typx.Any ],
        ) -> tuple[ Diagnostic, ... ]:
            ''' Converts core violations to enhanced diagnostics with metadata. '''

Pluggable Renderer System
===============================================================================

Simple Renderer Protocol
-------------------------------------------------------------------------------

The rendering system uses protocols for maximum flexibility with minimal complexity:

.. code-block:: python

    from . import __

    # Type alias for display format identifiers
    DisplayFormat: __.typx.TypeAlias = str

    class RenderingOptions( __.immut.DataclassObject ):
        ''' Configuration for diagnostic rendering across formats. '''
        include_context: __.typx.Annotated[
            bool, __.ddoc.Doc( 'Whether to include source context in output.' ) ] = True
        context_size: __.typx.Annotated[
            int, __.ddoc.Doc( 'Lines of context around violations.' ) ] = 2
        include_rule_names: __.typx.Annotated[
            bool, __.ddoc.Doc( 'Whether to include descriptive rule names.' ) ] = True
        use_color: __.typx.Annotated[
            __.Absential[ bool ],
            __.ddoc.Doc( 'Color output (auto-detected if absent).' ) ] = __.absent

    class Renderer( __.immut.Protocol ):
        ''' Protocol for diagnostic report rendering with consistent interface. '''

        def render_report( 
            self, report: Report, options: RenderingOptions 
        ) -> __.typx.Annotated[
            str, __.ddoc.Doc( 'Formatted report content for display.' ) ]: ...

    class TextRenderer:
        ''' Human-readable text renderer with context display and color support. '''

        def render_report( self, report: Report, options: RenderingOptions ) -> str: ...

        def format_diagnostic( 
            self, diagnostic: Diagnostic, include_context: bool = True 
        ) -> tuple[ str, ... ]:
            ''' Formats individual diagnostic with optional context. '''

        def format_summary( self, report: Report ) -> str:
            ''' Formats summary line with diagnostic counts. '''

    class JsonRenderer:
        ''' Structured JSON renderer for programmatic consumption. '''

        def render_report( self, report: Report, options: RenderingOptions ) -> str: ...

        def serialize_diagnostic( 
            self, diagnostic: Diagnostic 
        ) -> __.immut.Dictionary[ str, __.typx.Any ]:
            ''' Converts diagnostic to JSON-serializable structure. '''

    class CompactRenderer:
        ''' Space-efficient text renderer for constrained output environments. '''

        def render_report( self, report: Report, options: RenderingOptions ) -> str: ...

    def validate_renderer( renderer: __.typx.Any ) -> Renderer:
        ''' Validates that object implements Renderer protocol. '''
        if not isinstance( renderer, Renderer ):
            raise TypeError( f"Expected Renderer, got {type( renderer ).__name__}." )
        return renderer

    # Type alias for renderer registry
    RendererRegistry: __.typx.TypeAlias = __.accret.ValidatorDictionary[ DisplayFormat, Renderer ]

    def create_renderer_registry( ) -> RendererRegistry:
        ''' Creates validated registry for display format renderers. '''
        return __.accret.ValidatorDictionary( 
            value_validator = validate_renderer 
        )

Output Management
===============================================================================

Simple Output Handling
-------------------------------------------------------------------------------

Basic output management for essential use cases:

.. code-block:: python

    from . import __

    def print_content(
        content: str,
        stream: __.typx.TextIO,
    ) -> None:
        ''' Prints content to stream (stdout, stderr, files opened as streams). '''

    def detect_stream_color_support( stream: __.typx.TextIO ) -> bool:
        ''' Detects whether stream supports color output. '''

Integration Interface
===============================================================================

Main Diagnostic System
-------------------------------------------------------------------------------

The primary interface connecting the diagnostic system to the linter framework:

.. code-block:: python

    from . import __

    def create_report_from_violations(
        violations: __.cabc.Sequence[ __.violations.Violation ],
        source_lines_by_file: __.cabc.Mapping[ str, __.cabc.Sequence[ str ] ],
        rule_registry: __.cabc.Mapping[ str, __.typx.Any ],
    ) -> __.typx.Annotated[
        Report,
        __.ddoc.Doc( 'Enhanced diagnostic report from linter violations.' ),
    ]:
        ''' Creates diagnostic report from linter violations with enhanced metadata. '''

    def render_report_with_format(
        report: Report,
        format_name: DisplayFormat,
        renderer_registry: RendererRegistry,
        options: RenderingOptions,
    ) -> __.typx.Annotated[
        str,
        __.ddoc.Doc( 'Formatted report in specified display format.' ),
    ]:
        ''' Renders report using specified format and options. '''

    def print_report(
        report: Report,
        format_name: DisplayFormat,
        stream: __.typx.TextIO,
        renderer_registry: RendererRegistry,
        options: RenderingOptions,
    ) -> None:
        ''' Renders and prints report to stream (stdout, stderr, files opened as streams). '''

Module Organization
===============================================================================

Module Structure
-------------------------------------------------------------------------------

The diagnostic framework uses minimal module organization:

.. code-block::

    sources/vibelinter/reporting/
    ├── __.py                        # Reporting imports
    ├── __init__.py                  # Package entry point  
    ├── diagnostics.py               # Diagnostic and Report structures
    ├── context.py                   # SourceContext and ContextExtractor
    ├── renderers.py                 # All renderer implementations
    ├── assembly.py                  # ReportAssembler implementation
    ├── printers.py                  # Stream printing utilities
    └── integration.py               # Integration functions for linter framework

Import Organization
-------------------------------------------------------------------------------

Import structure following established patterns:

.. code-block:: python

    # sources/vibelinter/reporting/__.py
    from ..__ import *

    # sources/vibelinter/reporting/__init__.py  
    from . import __
    from .integration import create_report_from_violations, render_report_with_format, print_report
    from .diagnostics import Diagnostic, Report, DiagnosticSeverity
    from .renderers import DisplayFormat, RenderingOptions

Exception Handling
===============================================================================

Minimal Exception Hierarchy
-------------------------------------------------------------------------------

Simple exceptions following established patterns:

.. code-block:: python

    from . import __

    class RenderFailure( __.Omnierror ):
        ''' Raised when report rendering fails. '''

    class FormatNoSupport( __.Omnierror ):
        ''' Raised when requested display format is not supported. '''

Design Validation
===============================================================================

Compliance Verification
-------------------------------------------------------------------------------

The design maintains compliance with established practices:

**Essential Features Preserved:**
- Multi-format output (text, JSON, compact, GitHub Actions)
- Context display with validated POC patterns  
- Deterministic sorting for CI/CD consistency
- Integration with existing Violation structures
- Pluggable renderer architecture

**Design Choices:**
- Simple string formatting for messages
- Basic file/stream writing for output
- Embedded metadata in Diagnostic structure
- Single unified Report structure
- Focus on essential formats (text, JSON, compact, GitHub Actions)

**Architecture Benefits:**
- Clear integration path with existing linter framework
- Simple protocol-based extension points
- Validated context extraction patterns from POC
- Sophisticated error reporting capabilities

**Implementation Readiness:**
- Complete interface specifications for essential components
- Clear upgrade path from basic violations to enhanced diagnostics
- Proven context display patterns ready for implementation
- Minimal viable sophistication meeting REQ-007 requirements

Architectural Separation Rationale
===============================================================================

Component Boundary Design Decisions
-------------------------------------------------------------------------------

The diagnostic system maintains deliberate architectural separations that serve different abstraction levels and responsibilities:

**Violation vs. Diagnostic Separation**

**Design Decision**: Maintain separation between Violation and Diagnostic structures.

**Rationale:**
- **Violation**: Lightweight core data from rule execution focused on detection (what/where)
- **Diagnostic**: Rich presentation metadata focused on display and guidance (how to present/what can be done)
- **Composition Pattern**: Diagnostic embeds Violation to avoid duplication while adding presentation metadata
- **Performance**: Rules generate lightweight violations without presentation overhead during analysis
- **Extensibility**: Multiple presentation layers can enhance the same violations for different output formats

The embedded approach provides convenient access through proxy properties while maintaining clear separation of concerns between detection and presentation.

**Configuration vs. Registry Separation**

**Design Decision**: Maintain separation between Configuration and Registry systems.

**Rationale:**
- **Registry**: Provides metadata about available rules (what exists, capabilities, instantiation patterns)
- **Configuration**: Manages user preferences and runtime overrides (what to execute, with what parameters)
- **Command-Query Separation**: Registry queries rule information, Configuration commands execution behavior
- **Independent Evolution**: Registry changes with rule additions, Configuration changes with user requirements

This layered architecture enables independent development and testing of rule metadata management versus user preference application.

**File Discovery vs. Engine Processing Separation**

**Design Decision**: Maintain separation between File Discovery and Engine Processing systems.

**Rationale:**  
- **File Discovery**: Handles file system concerns (path resolution, filtering, gitignore integration)
- **Engine Processing**: Handles analysis concerns (rule coordination, violation collection, performance optimization)
- **Single Responsibility**: Discovery focuses on determining which files to analyze, Engine focuses on how to analyze them
- **Error Handling Isolation**: Discovery handles path/permission errors, Engine handles parsing/analysis errors

Clear interfaces prevent mixing file system operations with analysis logic, enabling independent testing and optimization of each concern.

This design provides sophisticated error reporting capabilities with clear integration with the existing linter core framework while maintaining principled architectural separations.