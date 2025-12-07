# File Discovery and Processing Pipeline Design

This document specifies the file discovery and processing pipeline
system that connects the file system to the existing linter core
framework. The design provides source file discovery with ignore pattern
integration and parallel processing.

## Design Philosophy

The discovery system provides essential file-to-analysis bridging
functionality:

**Architecture Goal**: Simple function-based interface that feeds
filtered source files to existing `Engine.lint_files()` method
**Integration Focus**: Build on validated linter core interfaces without
requiring changes to rule execution **Performance Focus**: Parallel
processing with configurable worker counts for scalability

## Essential Interface

### Core Discovery Functions

The file discovery system provides three essential functions:

``` python
from . import __

# Type aliases for interface clarity
Location: __.typx.TypeAlias = __.pathlib.Path
IgnorePatterns: __.typx.TypeAlias = __.cabc.Sequence[ str ]

def discover_files(
    anchors: __.typx.Annotated[
        __.cabc.Sequence[ Location ],
        __.ddoc.Doc( 'Root directories for source file discovery.' ) ],
    extensions: __.typx.Annotated[
        tuple[ str, ... ],
        __.ddoc.Doc( 'File extensions to treat as source files.' ) ] = ( '.py', '.pyi' ),
    ignore_patterns: IgnorePatterns = ( ),
    ignore_files: __.typx.Annotated[
        tuple[ str, ... ],
        __.ddoc.Doc( 'Ignore file names to search for during traversal.' ) ] = ( '.gitignore', ),
) -> __.typx.Annotated[
    tuple[ Location, ... ],
    __.ddoc.Doc( 'Source files found and filtered for linter processing.' ),
]:
    ''' Discovers source files from anchor locations with ignore pattern filtering. '''

def lint_discovered_files(
    locations: __.typx.Annotated[
        __.cabc.Sequence[ Location ],
        __.ddoc.Doc( 'Source file locations to process through vibelinter.' ) ],
    engine: __.typx.Annotated[
        __.engine.Engine, __.ddoc.Doc( 'Configured linter engine for file analysis.' ) ],
    concurrency: __.typx.Annotated[
        int, __.ddoc.Doc( 'Files to process concurrently (1 = sequential).' ) ] = 4,
    continue_on_errors: __.typx.Annotated[
        bool, __.ddoc.Doc( 'Whether to continue processing after individual file failures.' ) ] = True,
) -> __.typx.Annotated[
    tuple[ __.reporting.Report, ... ],
    __.ddoc.Doc( 'Diagnostic reports from successful file processing.' ),
]:
    ''' Processes files through linter engine with parallel execution and error isolation. '''

def discover_and_lint(
    anchors: __.cabc.Sequence[ Location ],
    engine: __.engine.Engine,
    extensions: tuple[ str, ... ] = ( '.py', '.pyi' ),
    ignore_patterns: IgnorePatterns = ( ),
    concurrency: int = 4,
) -> __.typx.Annotated[
    tuple[ __.reporting.Report, ... ],
    __.ddoc.Doc( 'Complete pipeline results from file discovery through linting.' ),
]:
    ''' Convenience function combining file discovery and linting in single operation. '''
```

## Implementation Architecture

### File Detection Strategy

Source file detection uses multiple strategies for comprehensive
coverage:

``` python
from . import __

def detect_source_file( 
    location: Location, 
    extensions: __.cabc.Sequence[ str ] 
) -> bool:
    ''' Detects source files by extension and shebang analysis. '''

def analyze_shebang( location: Location ) -> bool:
    ''' Analyzes file shebang to detect appropriate interpreter usage. '''
```

### Ignore Pattern Integration

The filtering system supports multiple ignore file formats with
extensible pattern matching:

``` python
from . import __

def collect_ignore_patterns(
    anchor: Location,
    ignore_files: __.cabc.Sequence[ str ],
) -> tuple[ str, ... ]:
    ''' Collects ignore patterns from ignore files in location hierarchy. '''

def should_ignore(
    location: Location,
    patterns: __.cabc.Sequence[ str ],
) -> bool:
    ''' Checks if location should be ignored based on patterns using glob-style matching. '''
```

### Parallel Processing Framework

The processing system provides configurable parallel execution with
error isolation:

``` python
from . import __

def process_files(
    locations: __.cabc.Sequence[ Location ],
    processor: __.cabc.Callable[ [ Location ], __.reporting.Report ],
    concurrency: int,
    continue_on_errors: bool,
) -> tuple[ __.reporting.Report, ... ]:
    ''' Processes files using parallel execution with error handling and isolation. '''
```

## Error Handling Design

### Exception Hierarchy

Simple exception hierarchy for discovery and processing failures:

``` python
from . import __

class FileDiscoverFailure( __.Omnierror ):
    ''' Raised when file discovery encounters unrecoverable errors during traversal. '''
```

## Module Organization

### Minimal Module Structure

The discovery framework uses minimal module organization following
established patterns:

``` 
sources/vibelinter/discovery/
├── __.py                        # Discovery imports
├── __init__.py                  # Package entry point
├── functions.py                 # Core discovery and processing functions
└── utilities.py                 # File detection and filtering utilities
```

### Import Organization

Import structure following established patterns:

``` python
# sources/vibelinter/discovery/__.py
from ..__ import *

# sources/vibelinter/discovery/__init__.py  
from . import __
from .functions import discover_files, lint_discovered_files, discover_and_lint
```

## Design Validation

### Framework Integration Verification

The design integrates seamlessly with existing architectural components:

**Engine Integration:** - Provides [tuple\[Path, \...\]]{.title-ref}
that integrates directly with [Engine.lint_files()]{.title-ref} - No
changes required to existing linter core interfaces - Clean separation
between discovery and analysis concerns

**Practices Compliance:** - Wide parameter types
([\_\_.cabc.Sequence]{.title-ref}) for flexible input interfaces -
Narrow return types ([tuple]{.title-ref}) for concrete results - Proper
[\_\_.typx.Annotated]{.title-ref} patterns with
[\_\_.ddoc.Doc]{.title-ref} documentation - Function signatures follow
established spacing and bracket conventions - Type aliases for complex
reused types ([Location]{.title-ref}, [IgnorePatterns]{.title-ref})

**Configuration Integration:** - Simple parameter-based configuration
avoiding complex configuration objects - Extensible ignore pattern
system supporting [.gitignore]{.title-ref}, [.hgignore]{.title-ref}, and
custom formats - Configurable parallel processing adapting to different
use cases

**Performance Characteristics:** - Parallel processing with configurable
worker counts - Error isolation preventing individual file failures from
stopping batch processing - Early filtering during traversal minimizing
unnecessary file system operations

**Implementation Readiness:** The design provides complete interface
specifications that: - Build directly on existing Engine interfaces
without modification - Support both interactive CLI usage and
programmatic integration - Scale from individual files to large
multi-package codebases with parallel processing - Provide robust error
handling while maintaining architectural simplicity

## File Discovery vs. Engine Processing Architectural Separation

### Design Decision Rationale

The file discovery system maintains deliberate separation from Engine
processing to ensure clear architectural boundaries:

**File Discovery System Responsibilities:** - Path resolution and
expansion from user-provided patterns - .gitignore integration and
custom ignore pattern processing - File system traversal with
configurable filtering - Error handling for path access and permission
issues - Parallel file enumeration for performance optimization

**Engine Processing System Responsibilities:** - Python source code
parsing and AST construction - Rule execution and violation collection -
LibCST metadata provider coordination - Analysis performance
optimization and timing - Rule-specific error handling and reporting

**Separation Rationale:** - **Single Responsibility Principle**:
Discovery determines \"which files to analyze,\" Engine determines \"how
to analyze files\" - **Error Handling Isolation**: Discovery handles
file system errors (permissions, missing files), Engine handles parsing
and analysis errors - **Performance Boundaries**: Discovery optimizes
file system operations, Engine optimizes analysis execution - **Testing
Isolation**: Discovery tested with file system mocks, Engine tested with
code samples - **Scalability**: Discovery can be parallelized
independently from Engine analysis patterns

**Interface Design:** The separation maintains clean interfaces where
Discovery produces [tuple\[Path, \...\]]{.title-ref} that integrates
directly with [Engine.lint_files()]{.title-ref} without requiring Engine
knowledge of file system concerns or Discovery knowledge of analysis
patterns.

This architectural separation enables independent optimization and
evolution of file system operations versus code analysis execution while
maintaining clear integration points.

This file discovery design bridges the file system and linter core
framework while maintaining architectural simplicity and practices
compliance, with extensibility for future source file types including
documentation-embedded code snippets.
