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
Test Plan: Linting Engine
*******************************************************************************

Coverage Analysis Summary
===============================================================================

- **Current coverage**: 33% (72 statements, 45 uncovered, 10 branches)
- **Target coverage**: 100%
- **Uncovered lines**: 36, 94-95, 107-108, 114-119, 128-142, 150-153, 159-163, 178-193, 209-214
- **Missing functionality tests**:

  - EngineConfiguration instantiation with defaults
  - Engine initialization and configuration
  - File reading and linting (lint_file)
  - Source code linting with violations
  - Metadata wrapper creation with error handling
  - Rule instantiation with parameters
  - Rule execution via CST traversal
  - Violation collection and sorting
  - Context extraction integration
  - Multi-file linting with error recovery
  - Performance timing measurement
  - Exception handling for MetadataProvideFailure
  - Exception handling for RuleExecuteFailure

Test Strategy
===============================================================================

Basic Functionality Tests (000-099)
-------------------------------------------------------------------------------

- Test 000: Engine module imports successfully
- Test 010: EngineConfiguration dataclass instantiation with minimal parameters
- Test 015: EngineConfiguration uses default values correctly
- Test 020: Report dataclass instantiation
- Test 025: Engine class instantiation with registry and configuration
- Test 030: Helper function _create_empty_rule_parameters returns empty Dictionary

EngineConfiguration Tests (100-199)
-------------------------------------------------------------------------------

**EngineConfiguration Dataclass (Tests 100-149)**

- Test 100: Instantiates with enabled_rules frozenset
- Test 105: Uses empty Dictionary as default for rule_parameters
- Test 110: Uses context_size default of 2
- Test 115: Uses include_context default of True
- Test 120: Accepts custom context_size
- Test 125: Accepts custom include_context value
- Test 130: Accepts custom rule_parameters Dictionary
- Test 135: Stores immutable rule_parameters
- Test 140: Nested rule parameter dictionaries are immutable

Report Dataclass Tests (150-199)
-------------------------------------------------------------------------------

**Report Dataclass (Tests 150-179)**

- Test 150: Instantiates with all required fields
- Test 155: Stores violations as tuple
- Test 160: Stores contexts as tuple
- Test 165: Stores filename string
- Test 170: Stores rule_count integer
- Test 175: Stores analysis_duration_ms float

Engine Initialization Tests (200-249)
-------------------------------------------------------------------------------

**Engine.__init__ (Tests 200-229)**

- Test 200: Initializes with registry_manager
- Test 205: Initializes with configuration
- Test 210: Stores registry_manager as instance attribute
- Test 215: Stores configuration as instance attribute
- Test 220: Works with minimal configuration
- Test 225: Works with complex configuration

Single-File Linting Tests (250-349)
-------------------------------------------------------------------------------

**Engine.lint_file (Tests 250-279)**

- Test 250: Reads and lints valid Python file
- Test 255: Returns Report with violations
- Test 260: Returns Report with empty violations for clean code
- Test 265: Passes file path as filename to lint_source
- Test 270: Reads file with UTF-8 encoding
- Test 275: Propagates exceptions from lint_source

**Engine.lint_source (Tests 280-349)**

- Test 280: Parses valid Python source code
- Test 285: Returns Report with violations from rules
- Test 290: Returns Report with empty violations for clean code
- Test 295: Includes all enabled rules in rule_count
- Test 300: Measures analysis_duration_ms accurately
- Test 305: Uses provided filename in Report
- Test 310: Uses default '<string>' filename when not provided
- Test 315: Extracts contexts when include_context is True
- Test 320: Omits contexts when include_context is False
- Test 325: Sorts violations by line then column
- Test 330: Includes violations from multiple rules
- Test 335: Passes context_size to context extraction
- Test 340: Skips context extraction when no violations
- Test 345: Handles empty source code gracefully

Metadata Wrapper Creation Tests (350-399)
-------------------------------------------------------------------------------

**Engine._create_metadata_wrapper (Tests 350-379)**

- Test 350: Parses valid Python source
- Test 355: Creates MetadataWrapper successfully
- Test 360: Returns tuple of wrapper and source_lines
- Test 365: Splits source into lines correctly
- Test 370: Preserves empty lines in source_lines
- Test 375: Handles single-line source
- Test 380: Raises MetadataProvideFailure on metadata error
- Test 385: Includes filename in MetadataProvideFailure
- Test 390: Chains original exception in MetadataProvideFailure
- Test 395: Handles malformed Python syntax in parse_module

Rule Instantiation Tests (400-449)
-------------------------------------------------------------------------------

**Engine._instantiate_rules (Tests 400-439)**

- Test 400: Instantiates single rule from enabled_rules
- Test 405: Instantiates multiple rules from enabled_rules
- Test 410: Passes filename to rule constructor
- Test 415: Passes wrapper to rule constructor
- Test 420: Passes source_lines to rule constructor
- Test 425: Passes rule parameters from configuration
- Test 430: Uses empty Dictionary for rules without parameters
- Test 435: Returns list of instantiated rules
- Test 440: Raises RuleExecuteFailure on rule instantiation error
- Test 445: Includes VBL code in RuleExecuteFailure
- Test 450: Chains original exception in RuleExecuteFailure

Rule Execution Tests (450-499)
-------------------------------------------------------------------------------

**Engine._execute_rules (Tests 450-479)**

- Test 450: Visits each rule with metadata wrapper
- Test 455: Executes rules in order
- Test 460: Completes traversal for all rules
- Test 465: Raises RuleExecuteFailure on rule visit error
- Test 470: Includes rule_id in RuleExecuteFailure
- Test 475: Chains original exception in RuleExecuteFailure

Violation Collection Tests (480-529)
-------------------------------------------------------------------------------

**Engine._collect_violations (Tests 480-519)**

- Test 480: Collects violations from single rule
- Test 485: Collects violations from multiple rules
- Test 490: Returns empty list when no violations
- Test 495: Sorts violations by line number
- Test 500: Sorts violations by column when lines equal
- Test 505: Maintains stable sort for equal positions
- Test 510: Flattens violations from all rules into single list
- Test 515: Returns list (not tuple) for internal processing

Multi-File Linting Tests (530-599)
-------------------------------------------------------------------------------

**Engine.lint_files (Tests 530-579)**

- Test 530: Lints single file
- Test 535: Lints multiple files
- Test 540: Returns tuple of Reports
- Test 545: Returns Report for each file
- Test 550: Continues after file error
- Test 555: Skips file that raises exception
- Test 560: Returns empty tuple for empty file list
- Test 565: Preserves file order in results
- Test 570: Handles mix of valid and invalid files

Integration Tests (600-699)
-------------------------------------------------------------------------------

**End-to-End Workflows (Tests 600-649)**

- Test 600: Complete workflow from file to Report
- Test 605: Multiple rules detect different violations
- Test 610: Context extraction works with real violations
- Test 615: Rule parameters affect rule behavior
- Test 620: Analysis timing is measured correctly
- Test 625: Violations from multiple files are independent

**Performance Characteristics (Tests 650-699)**

- Test 650: Analysis completes within performance budget
- Test 655: Single-pass traversal (verify metadata wrapper visited once)
- Test 660: Memory-efficient violation storage

Error Handling Integration Tests (700-799)
-------------------------------------------------------------------------------

**Exception Scenarios (Tests 700-749)**

- Test 700: MetadataProvideFailure includes context
- Test 705: RuleExecuteFailure includes rule identifier
- Test 710: File reading errors propagate from lint_file
- Test 715: Parse errors are caught as MetadataProvideFailure
- Test 720: Rule instantiation errors are caught as RuleExecuteFailure
- Test 725: Rule execution errors are caught as RuleExecuteFailure

**Error Recovery (Tests 750-799)**

- Test 750: lint_files continues after single file error
- Test 755: Partial results returned from lint_files
- Test 760: Exception details preserved in error chain

Implementation Notes
===============================================================================

Dependencies requiring injection
-------------------------------------------------------------------------------

- **Rule registry**: Inject RuleRegistryManager with test rules
- **Test rules**: Create simple mock rules for testing engine behavior
- **File system**: Use pyfakefs for lint_file tests

Filesystem operations needing pyfakefs
-------------------------------------------------------------------------------

- All lint_file tests reading from disk
- Multi-file linting tests with file paths

Test data and fixtures
-------------------------------------------------------------------------------

**tests/test_000_vibelinter/fixtures.py** - Shared fixtures:

- ``mock_rule_registry`` - RuleRegistryManager with test rules
- ``minimal_engine_config`` - EngineConfiguration with single rule
- ``mock_violation_rule`` - Rule that produces known violations
- ``clean_code_rule`` - Rule that produces no violations
- ``failing_rule`` - Rule that raises exception during execution

**tests/data/engine/** - Test source files:

- ``valid_simple.py`` - Minimal valid Python file
- ``valid_with_violations.py`` - Code that triggers test rule violations
- ``valid_clean.py`` - Code that passes all rules
- ``invalid_syntax.py`` - Python file with syntax errors
- ``empty.py`` - Empty file
- ``single_line.py`` - Single line of code

Mock rule pattern
-------------------------------------------------------------------------------

Create simple test rules for engine testing::

    class TestViolationRule(BaseRule):
        '''Test rule that produces predictable violations.'''

        @property
        def rule_id(self) -> str:
            return 'TEST001'

        def visit_FunctionDef(self, node):
            # Produce violation for any function
            self._produce_violation(
                node, 'Test violation', 'error')

        def _analyze_collections(self):
            pass  # No collection analysis needed

Test organization pattern
-------------------------------------------------------------------------------

Organize tests by Engine method with clear separation::

    # Basic functionality
    def test_000_engine_module_imports()
    def test_010_configuration_instantiation()

    # Engine initialization
    def test_200_engine_initialization()

    # lint_file method
    def test_250_lint_file_valid_source()

    # lint_source method
    def test_280_lint_source_valid_code()

    # Helper methods (via public API)
    def test_350_metadata_wrapper_creation()
    def test_400_rule_instantiation()
    def test_450_rule_execution()
    def test_480_violation_collection()

    # lint_files method
    def test_530_lint_files_multiple()

    # Integration tests
    def test_600_end_to_end_workflow()

    # Error handling
    def test_700_exception_handling()

Test module numbering
-------------------------------------------------------------------------------

Create ``tests/test_000_vibelinter/test_300_engine.py`` following the established numbering scheme where 300-399 is allocated for the analysis engine layer.

Anti-patterns to avoid
-------------------------------------------------------------------------------

- **DO NOT** test private methods directly - test through public API
- **DO NOT** mock LibCST internals - use real LibCST objects
- **DO NOT** test against real external files - use pyfakefs
- **DO NOT** use sleep() for performance tests - verify timing calculation logic

Pushback recommendations
-------------------------------------------------------------------------------

**Engine design observations:**

- **Silent exception swallowing**: ``lint_files`` silently continues on exceptions (line 212: ``except Exception: continue``). This makes debugging difficult and may hide serious errors.

  **Recommendation**: Consider returning errors alongside successful reports, or providing a callback/logger for error handling. Current behavior prevents users from knowing which files failed and why.

- **No validation of enabled_rules**: Engine doesn't validate that enabled rules exist in registry before attempting instantiation.

  **Recommendation**: Add validation method to check enabled_rules against registry at Engine initialization, failing fast with clear error message.

- **Limited observability**: No hooks for progress reporting or cancellation in multi-file linting.

  **Recommendation**: Consider callback pattern for progress notification in ``lint_files``, especially important for large codebases.

**Testability concerns:**

- The private methods are well-structured and easy to test through the public API.
- Error handling paths are accessible via exception triggering.
- Single-pass design is implicitly validated through performance characteristics.

Success Metrics
===============================================================================

- **Target line coverage**: 100% (from current 33%)
- **Branch coverage goals**: 100% (from current 0%)
- **Specific gaps to close**: All 45 uncovered lines

Closure of uncovered lines
-------------------------------------------------------------------------------

- **Line 36**: _create_empty_rule_parameters - Test 030
- **Lines 94-95**: Engine.__init__ - Tests 200-225
- **Lines 107-108**: lint_file - Tests 250-275
- **Lines 114-119**: _create_metadata_wrapper - Tests 350-395
- **Lines 128-142**: _instantiate_rules - Tests 400-450
- **Lines 150-153**: _execute_rules - Tests 450-475
- **Lines 159-163**: _collect_violations - Tests 480-515
- **Lines 178-193**: lint_source - Tests 280-345
- **Lines 209-214**: lint_files - Tests 530-570

Expected test count
-------------------------------------------------------------------------------

- Basic functionality: 6 tests
- EngineConfiguration: 9 tests
- Report dataclass: 6 tests
- Engine initialization: 6 tests
- lint_file: 6 tests
- lint_source: 14 tests
- Metadata wrapper creation: 10 tests
- Rule instantiation: 11 tests
- Rule execution: 6 tests
- Violation collection: 8 tests
- lint_files: 9 tests
- Integration tests: 11 tests
- Error handling: 13 tests
- **Total**: Approximately 115 tests

Estimated complexity: High - Requires mock rules and integration testing

Implementation priority: High - Engine is the core of the linting system

Testing philosophy alignment
-------------------------------------------------------------------------------

This test plan follows project testing principles:

- **Dependency injection**: Mock rules injected via registry
- **Immutability**: Works with immutable configuration objects
- **Performance**: Tests verify performance characteristics without sleep()
- **Coverage**: Systematic targeting of all branches and error paths
- **Behavior testing**: Focus on observable behavior through public API
- **No monkey-patching**: All tests work with real LibCST and injected dependencies
