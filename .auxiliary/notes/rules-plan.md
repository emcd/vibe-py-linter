# Rules System Implementation Plan

## Overview

This plan outlines the implementation of the core linter framework following the hybrid modular architecture defined in ADR-001 and ADR-002. The system will use LibCST for concrete syntax tree analysis with a collection-then-analysis pattern for rule implementation.

## Architecture Summary

Based on the architectural documentation review, the rules system consists of:

1. **Violation Data Structures** - Immutable dataclasses for violations and context
2. **BaseRule Framework** - Abstract base class implementing collection-then-analysis pattern
3. **Rule Registry System** - Bidirectional mapping between VBL codes and rule implementations
4. **Engine Orchestration** - Central coordinator for single-pass CST analysis
5. **Context Extraction** - Enhanced error reporting with source code context

## Implementation Phases

### Phase 1: Core Data Structures (Foundation)

**Module:** `sources/vibelinter/rules/violations.py`

Implement the fundamental data structures:
- `Violation` dataclass with precise positioning (line, column)
- `ViolationContext` dataclass for enhanced error reporting
- Type aliases: `ViolationSequence`, `ViolationContextSequence`

**Key Design Decisions:**
- Use `__.immut.DataclassObject` for immutability
- One-indexed line numbers, zero-indexed column positions
- Support severity levels (error, warning, info)

### Phase 2: Exception Hierarchy

**Module:** `sources/vibelinter/exceptions.py` (expand existing)

Add linter-specific exceptions:
- `RuleExecuteFailure` - Rule execution errors
- `MetadataProvideFailure` - LibCST metadata initialization errors
- `RuleRegistryInvalidity` - Invalid rule registry mappings
- `RuleConfigureFailure` - Invalid rule configuration

Follow the Omniexception → Omnierror pattern established in the project.

### Phase 3: BaseRule Framework

**Module:** `sources/vibelinter/rules/base.py`

Implement the abstract base class:
- Inherit from both `ABC` and `libcst.CSTVisitor`
- Define `METADATA_DEPENDENCIES` (PositionProvider, ScopeProvider, QualifiedNameProvider)
- Implement collection-then-analysis pattern via `leave_Module`
- Provide helper methods:
  - `_produce_violation(node, message, severity)` - Create violations with precise positioning
  - `_position_from_node(node)` - Extract (line, column) from CST node
  - `_extract_context(line, context_size)` - Get source context around violation
- Abstract properties/methods:
  - `rule_id` property - Returns VBL code
  - `_analyze_collections()` - Rule-specific analysis logic

**Critical Pattern:**
Rules collect data during CST traversal, then analyze in `leave_Module` after traversal completes. This supports complex rules requiring complete file information.

### Phase 4: Context Extraction Utilities

**Module:** `sources/vibelinter/rules/context.py`

Implement context extraction for enhanced error reporting:
- `ContextExtractor` class for extracting source lines around violations
- `extract_violation_context()` - Extract context with configurable size
- `format_context_display()` - Format context with line numbers and highlighting
- `extract_contexts_for_violations()` - Batch context extraction

### Phase 5: Rule Registry System

**Modules:**
- `sources/vibelinter/rules/registry.py` - Registry implementation
- `sources/vibelinter/rules/__.py` - Rule-specific import hub

Implement rule discovery and instantiation:
- `RuleDescriptor` dataclass with VBL code, descriptive name, category, subcategory
- `RuleRegistryManager` class:
  - Bidirectional mapping (VBL code ↔ descriptive name)
  - `resolve_rule_identifier()` - Convert any identifier to canonical VBL code
  - `produce_rule_instance()` - Factory pattern for rule instantiation
  - `survey_available_rules()` - List all registered rules
  - `filter_rules_by_category()` - Filter by category/subcategory

**Design Note:**
Registry manages "what rules exist and how to create them" - separate from Configuration which manages "which rules to run and with what settings".

### Phase 6: Engine Orchestration

**Module:** `sources/vibelinter/engine.py`

Implement the central analysis coordinator:
- `EngineConfiguration` dataclass:
  - `enabled_rules: frozenset[str]` - VBL codes to execute
  - `rule_parameters: Dictionary[str, Dictionary[str, Any]]` - Per-rule config
  - `context_size: int` - Context lines around violations
  - `include_context: bool` - Whether to extract context
- `Report` dataclass:
  - `violations: tuple[Violation, ...]`
  - `contexts: tuple[ViolationContext, ...]`
  - `filename: str`
  - `rule_count: int`
  - `analysis_duration_ms: float`
- `Engine` class:
  - `lint_file(file_path)` - Analyze single file from path
  - `lint_source(source_code, filename)` - Analyze source string
  - `lint_files(file_paths)` - Batch analysis

**Single-Pass Analysis Flow:**
1. Parse source with LibCST
2. Create MetadataWrapper with position, scope, qualified name providers
3. Instantiate all enabled rules
4. Single CST traversal visiting all rules
5. Collect violations from all rules
6. Extract contexts if enabled
7. Return Report with results and timing

### Phase 7: Proof-of-Concept Rule

**Module:** `sources/vibelinter/rules/implementations/vbl101.py`

Implement VBL101 (simple blank line elimination rule) as proof-of-concept:
- Detect consecutive blank lines within function bodies
- Use collection-then-analysis pattern:
  - Collect function nodes and their blank line positions during traversal
  - Analyze in `leave_Module` to generate violations
- Validate LibCST integration and metadata access
- Confirm performance characteristics

This validates:
- BaseRule framework works correctly
- LibCST metadata integration functions
- Collection-then-analysis pattern is viable
- Context extraction enhances error reporting
- End-to-end flow from parsing → analysis → reporting

### Phase 8: Module Organization & Import Hub

**Modules:**
- `sources/vibelinter/rules/__init__.py` - Package entry point
- `sources/vibelinter/rules/__.py` - Rule-specific import hub
- `sources/vibelinter/__/imports.py` - Add LibCST imports

Organize the framework following established patterns:
```
sources/vibelinter/
├── __/
│   ├── __init__.py       # Core framework imports
│   ├── imports.py        # Add: libcst, libcst.metadata
│   └── nomina.py         # Framework constants
├── engine.py             # Engine implementation
├── exceptions.py         # Add rule exceptions
└── rules/
    ├── __.py             # Rule-specific imports
    ├── __init__.py       # Package entry
    ├── base.py           # BaseRule
    ├── registry.py       # RuleRegistryManager
    ├── context.py        # ContextExtractor
    ├── violations.py     # Violation data structures
    └── implementations/  # Individual rule implementations
        └── vbl101.py     # First proof-of-concept rule
```

## Implementation Order

1. **Setup Module Structure** - Create directories and `__init__.py` files
2. **Violations & Exceptions** - Foundation data structures
3. **Context Extraction** - Reusable utilities
4. **BaseRule Framework** - Core abstraction
5. **Proof-of-Concept Rule** - Validate design with VBL101
6. **Rule Registry** - Discovery and instantiation
7. **Engine Orchestration** - Wire everything together
8. **Integration Testing** - End-to-end validation

## Key Questions & Design Clarifications Needed

### 1. Rule Parameter Configuration

**Question:** How should rules receive their configuration parameters?

**Options:**
- A) Pass parameters to `__init__` via registry factory
- B) Call a `configure(params)` method after instantiation
- C) Access parameters from a shared configuration object

**Recommendation:** Option A - pass via `__init__`. The registry factory can handle rule-specific parameter injection, keeping rules decoupled from configuration management.

### 2. Metadata Provider Error Handling

**Question:** What should happen if LibCST metadata providers fail to initialize?

**Current Plan:** Raise `MetadataProvideFailure` and fail the analysis. This ensures rules can rely on metadata being available.

**Alternative:** Gracefully degrade - run rules without metadata but with reduced capabilities?

**Recommendation:** Stick with fail-fast approach. All rules depend on PositionProvider for accurate violation reporting.

### 3. Rule Discovery Mechanism

**Question:** Should rules be auto-discovered (via imports/plugins) or explicitly registered?

**Current Plan:** Explicit registration in registry for Phase 1 simplicity.

**Future Enhancement:** Add auto-discovery via entry points or directory scanning in later phase.

### 4. Violation Deduplication

**Question:** How should we handle multiple rules reporting the same violation?

**Current Plan:** Each rule reports independently - deduplication handled at reporting layer if needed.

**Consideration:** Should engine deduplicate by (filename, line, column) or keep all violations?

**Recommendation:** Keep all violations initially. Rules should be specific enough to avoid duplicates. Add deduplication later if it becomes an issue.

### 5. Performance Monitoring

**Question:** Should we track per-rule timing in addition to overall analysis duration?

**Current Plan:** Report overall `analysis_duration_ms` in Report.

**Enhancement:** Add `rule_timings: dict[str, float]` to Report for performance debugging?

**Recommendation:** Start simple with overall timing. Add per-rule timing if performance issues arise.

## Dependencies

### Required External Libraries
- `libcst >= 1.0.0` - CST analysis with metadata providers
- Already in project dependencies (confirmed via architecture docs)

### Project Internal Dependencies
- `__.immut.DataclassObject` - Immutable dataclass base
- `__.typx.Annotated` - Type annotations
- `__.ddoc.Doc` - Documentation annotations
- `__.cabc` - Collections abstract base classes
- Exception hierarchy patterns

## Success Criteria

The rules system implementation is complete when:

1. ✅ All core data structures implemented (Violation, ViolationContext)
2. ✅ BaseRule framework functional with LibCST integration
3. ✅ At least one proof-of-concept rule (VBL101) working end-to-end
4. ✅ Rule registry can instantiate and manage rules
5. ✅ Engine can analyze files and return Reports
6. ✅ Context extraction enhances error reporting
7. ✅ Performance meets targets (<1000ms for 1000 lines)
8. ✅ Unit tests cover all framework components
9. ✅ Integration tests validate end-to-end flow

## Next Steps After Rules System

Once the core framework is operational:

1. **Configuration System** - Implement TOML-based configuration loading
2. **Additional Rules** - Implement remaining VBL rules (VBL102, VBL201, VBL301)
3. **CLI Integration** - Wire engine into `check` subcommand
4. **Diagnostic Reporting** - Implement formatted output (human-readable, JSON, SARIF)
5. **File Discovery** - Implement recursive Python file enumeration
6. **Testing Infrastructure** - Fixture system for rule testing

## Notes

- The collection-then-analysis pattern is validated via proof-of-concept work
- Single-pass analysis with metadata achieves 600ms performance target
- Context extraction significantly improves developer experience
- Rule isolation enables independent testing and development
- Registry abstraction supports both VBL codes and descriptive names for flexibility

## References

- ADR-001: Core Engine and Rule Framework Architecture
- ADR-002: Syntax Tree Analysis Technology Selection
- Design: Linter Core Framework Design
- Design: Diagnostic Reporting (for future output formatting)
