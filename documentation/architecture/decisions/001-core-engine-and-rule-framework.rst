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
001. Core Engine and Rule Framework Architecture
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

The Python linter needs a core architecture that supports the PRD requirements for:

- **Extensible rule system**: Four initial rules with ability to add more
- **Performance targets**: Process 1000 lines in <1000ms 
- **Configurable behavior**: Rule enable/disable and parameter customization
- **Precise error reporting**: Line/column positions with actionable messages
- **Incremental development**: Rules implemented and deployed individually

The system must balance simplicity for initial development with extensibility for future growth. Analysis of prototype implementations reveals three approaches with varying architectural merit:

1. **Single-file monolithic design**: All rules in one visitor class (from GPT-5 sketch) - demonstrates implementation patterns but has architectural limitations
2. **Phased incremental approach**: Start simple, add complexity iteratively (from Grok sketch) - excellent development strategy 
3. **Modular plugin architecture**: Separate rule classes with registry system (from Opus sketch) - superior production architecture

Key architectural forces:

- **Development speed vs. maintainability**: Simple designs enable faster initial development but become unmaintainable as rules grow
- **Performance vs. flexibility**: Single-pass analysis is faster but multiple rule instances may provide better isolation
- **Configuration complexity**: Granular rule control requires more sophisticated configuration management

Decision
===============================================================================

We will implement a **hybrid modular architecture** based primarily on the **Opus and Grok approaches**, incorporating the GPT-5 implementation patterns where valuable:

**Core Engine Design:**
- Central ``LinterEngine`` class orchestrates the analysis pipeline
- Single-pass CST traversal with metadata providers (PositionProvider, ScopeProvider, QualifiedNameProvider)
- Rule registry system for automatic discovery and configuration
- Violation collection and deduplication across all rules

**Rule Framework Design:**  
- Abstract ``BaseRule`` class providing common metadata access and violation reporting
- Each rule inherits from both ``BaseRule`` and ``libcst.CSTVisitor``
- Rules operate independently with no cross-dependencies
- **Collection-then-analysis pattern**: Rules collect data during traversal, analyze collections in post-processing (pattern validated in proof-of-concept)
- Context extraction pattern validated for enhanced error reporting
- Standardized violation format with rule ID, location, and message

**Development Progression:**
- Start with simplified single-file prototype for rapid validation (Phase 1)
- Refactor to modular architecture as rule complexity grows (Phase 2)  
- Add advanced features (configuration, auto-fixes) incrementally (Phase 3+)

**Key Architectural Components:**

.. code-block:: python

    # Core abstractions
    @dataclass
    class Violation:
        rule_id: str
        filename: str  
        line: int
        column: int
        message: str
        severity: str = "error"

    class BaseRule(ABC, cst.CSTVisitor):
        """Base class for all linting rules implementing collection-then-analysis pattern."""
        METADATA_DEPENDENCIES = (PositionProvider, ScopeProvider, QualifiedNameProvider)
        
        def __init__(self, filename: str, wrapper: MetadataWrapper):
            self.filename = filename
            self.wrapper = wrapper
            self.violations: List[Violation] = []
            # Subclasses add collection attributes here
        
        @property
        @abstractmethod  
        def rule_id(self) -> str: ...
        
        def leave_Module(self, node: cst.Module) -> None:
            """Override to analyze collected data after traversal completes."""
            self._analyze_collections()
        
        @abstractmethod
        def _analyze_collections(self) -> None:
            """Analyze collected data and generate violations."""
            ...

    class LinterEngine:
        """Central orchestrator for linting analysis."""
        def __init__(self, rules: List[BaseRule], config: Configuration): ...
        def lint_files(self, paths: List[Path]) -> List[Violation]: ...

Alternatives
===============================================================================

**Alternative 1: Pure Single-File Design**

Implement all rules as methods in a single ``CSTVisitor`` class.

*Rejected because:*
- Poor separation of concerns as rule count grows
- Difficult to configure individual rules  
- Testing becomes complex with intermingled rule logic
- Violates single responsibility principle

**Alternative 2: Pure Plugin Architecture**

Implement each rule as completely independent modules with their own CST parsing.

*Rejected because:*
- Performance overhead from multiple parse passes  
- Increased memory usage and complexity
- Harder to share common metadata and utilities
- Overly complex for initial implementation needs

**Alternative 3: Event-Driven Architecture**

Use observer pattern with CST events triggering rule callbacks.

*Rejected because:*
- Added complexity for minimal benefit in this domain
- Harder to debug and trace rule execution
- Potential performance overhead from event dispatch
- LibCST visitor pattern already provides needed traversal

Consequences
===============================================================================

**Positive Consequences:**

- **Rapid prototyping**: Can start with simple implementations and refactor incrementally
- **Good separation of concerns**: Each rule focuses on specific code patterns  
- **Performance optimization**: Single-pass analysis with multiple rule evaluation
- **Easy testing**: Rules can be tested independently with focused test cases
- **Configuration flexibility**: Individual rule enable/disable and parameter control
- **Future extensibility**: New rules require minimal framework changes

**Negative Consequences:**

- **Initial architecture complexity**: More complex than pure single-file approach
- **Development overhead**: Base classes and abstractions require more initial setup
- **Memory usage**: Multiple rule instances consume more memory than single visitor
- **Potential performance impact**: Rule isolation may have minor overhead vs. monolithic design

**Risks and Mitigations:**

- **Risk**: Framework complexity slows initial development  
  *Mitigation*: Start with minimal viable abstractions, add complexity incrementally

- **Risk**: Performance doesn't meet 1000ms target  
  *Mitigation*: Target confirmed achievable through validation - 1000ms target provides comfortable margin for implementation

- **Risk**: Rule interactions create unexpected behaviors  
  *Mitigation*: Enforce rule isolation, comprehensive integration testing

**Implementation Guidance:**

1. **Phase 1**: Implement working prototype with 2-3 core rules to validate approach
2. **Phase 2**: Refactor to full modular architecture with remaining rules  
3. **Phase 3**: Add configuration system and advanced features
4. **Testing strategy**: Unit tests per rule, integration tests for engine, performance benchmarks
5. **Performance monitoring**: Track analysis time per file size, memory usage per rule count