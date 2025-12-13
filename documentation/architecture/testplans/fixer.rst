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
Test Plan: Fix Engine (fixer.py)
*******************************************************************************

This test plan covers comprehensive testing of the fix engine module, which
coordinates fix application with conflict resolution, safety filtering, and
diff generation. The fixer module is foundational infrastructure enabling
automated code remediation across all fixable rules.

Coverage Analysis Summary
===============================================================================

Current Coverage Status
-------------------------------------------------------------------------------

* **Current coverage**: 34% (significantly undertested)
* **Target coverage**: 100%
* **Module under test**: ``sources/vibelinter/fixer.py``
* **Lines of code**: 82 statements, 14 branches
* **Uncovered lines**: 87, 91-99, 103-111, 146, 164-219, 233-243, 250, 272-276

Uncovered Functionality by Line Range
-------------------------------------------------------------------------------

1. **Lines 87, 91-99**: ``FixApplicationResult.has_changes`` property and
   ``generate_unified_diff`` method

2. **Lines 103-111**: ``generate_context_diff`` method

3. **Line 146**: ``FixEngine.__init__`` with ``apply_dangerous=True``

4. **Lines 164-219**: Core ``apply_fixes`` method - the main fix application
   logic including:

   * Empty fixes shortcut (164-172)
   * Safety filtering (173-183)
   * Position-based sorting (184-185)
   * CST parsing and traversal (187)
   * Conflict detection and fix application loop (191-217)
   * Modified source extraction (218-219)

5. **Lines 233-243**: ``_filter_by_safety`` method - safety classification
   filtering logic

6. **Line 250**: ``_sort_fixes_by_position`` method - reverse position sorting

7. **Lines 272-276**: ``apply_fixes_to_file`` method - file I/O integration

Data Classes Under Test
-------------------------------------------------------------------------------

* **FixConflict**: Records when fixes are skipped due to overlap
* **SkippedFix**: Records when fixes are skipped due to safety classification
* **FixApplicationResult**: Result of applying fixes to a single file
* **FixEngineResult**: Aggregate result across multiple files

Core Classes Under Test
-------------------------------------------------------------------------------

* **FixEngine**: Coordinates fix application with safety and conflict handling

Test Strategy
===============================================================================

The test strategy employs in-memory code snippets and mock Fix objects to
verify fix engine behavior without filesystem dependencies. Tests create
minimal transformer factories that produce predictable transformations.

Test Module Structure
-------------------------------------------------------------------------------

Test module: ``tests/test_000_vibelinter/test_360_fixer.py``

The test module follows standard numbering conventions:

* **000-099**: Basic functionality and class instantiation
* **100-199**: FixConflict and SkippedFix data classes
* **200-299**: FixApplicationResult functionality
* **300-399**: FixEngineResult functionality
* **400-499**: FixEngine.apply_fixes core logic
* **500-599**: Safety filtering and conflict resolution
* **600-699**: File I/O integration (apply_fixes_to_file)
* **700-799**: Edge cases and error handling

Basic Functionality Tests (000-099)
===============================================================================

test_000_fixengine_instantiation_default
-------------------------------------------------------------------------------

Verify FixEngine instantiates with default parameters.

**Expected behavior**: ``FixEngine()`` creates engine with
``apply_dangerous=False``.

test_010_fixengine_instantiation_apply_dangerous
-------------------------------------------------------------------------------

Verify FixEngine instantiates with ``apply_dangerous=True``.

**Expected behavior**: ``FixEngine(apply_dangerous=True)`` creates engine
that will apply dangerous fixes.

test_020_fixconflict_instantiation
-------------------------------------------------------------------------------

Verify FixConflict data class instantiates correctly.

**Required attributes**:

* ``skipped_fix``: The fix that was skipped
* ``conflicting_fix``: The fix that caused the conflict
* ``reason``: Description of why conflict occurred

test_030_skippedfix_instantiation
-------------------------------------------------------------------------------

Verify SkippedFix data class instantiates correctly.

**Required attributes**:

* ``fix``: The fix that was skipped
* ``reason``: Reason for skipping

test_040_fixapplicationresult_instantiation
-------------------------------------------------------------------------------

Verify FixApplicationResult instantiates with all required fields.

**Required attributes**:

* ``filename``: Path to processed file
* ``original_source``: Original source code
* ``modified_source``: Modified source code after fixes
* ``applied_fixes``: Tuple of successfully applied fixes
* ``skipped_fixes``: Tuple of SkippedFix objects
* ``conflicts``: Tuple of FixConflict objects

test_050_fixengineresult_instantiation
-------------------------------------------------------------------------------

Verify FixEngineResult instantiates with aggregate statistics.

**Required attributes**:

* ``file_results``: Tuple of FixApplicationResult objects
* ``total_applied``: Total number of fixes applied
* ``total_skipped``: Total number of fixes skipped
* ``total_conflicts``: Total number of conflicts encountered

FixConflict and SkippedFix Tests (100-199)
===============================================================================

test_100_fixconflict_attributes_immutable
-------------------------------------------------------------------------------

Verify FixConflict attributes are immutable after creation.

**Expected behavior**: Attempting to modify attributes raises
``AttributeError`` or similar immutability exception.

test_110_skippedfix_attributes_immutable
-------------------------------------------------------------------------------

Verify SkippedFix attributes are immutable after creation.

**Expected behavior**: Attempting to modify attributes raises
``AttributeError`` or similar immutability exception.

test_120_fixconflict_reason_formats
-------------------------------------------------------------------------------

Verify FixConflict reason contains useful diagnostic information.

**Test cases**:

* Line overlap conflict: Reason mentions line number
* Transformation failure: Reason indicates transformation error

test_130_skippedfix_reason_formats
-------------------------------------------------------------------------------

Verify SkippedFix reason contains actionable information.

**Test cases**:

* PotentiallyUnsafe skip: Reason mentions ``--apply-dangerous``
* Dangerous skip: Reason mentions ``--apply-dangerous``

FixApplicationResult Tests (200-299)
===============================================================================

test_200_has_changes_true_when_fixes_applied
-------------------------------------------------------------------------------

Verify ``has_changes`` returns True when fixes were applied.

**Setup**:

* Create FixApplicationResult with non-empty ``applied_fixes``

**Expected behavior**: ``result.has_changes == True``

test_210_has_changes_false_when_no_fixes_applied
-------------------------------------------------------------------------------

Verify ``has_changes`` returns False when no fixes were applied.

**Setup**:

* Create FixApplicationResult with empty ``applied_fixes``

**Expected behavior**: ``result.has_changes == False``

test_220_generate_unified_diff_with_changes
-------------------------------------------------------------------------------

Verify unified diff generation produces valid diff output.

**Setup**:

* Create result where ``original_source != modified_source``

**Expected behavior**:

* Diff output contains ``---`` and ``+++`` headers
* Diff output contains ``@@`` hunk markers
* Diff output shows actual changes

test_230_generate_unified_diff_no_changes
-------------------------------------------------------------------------------

Verify unified diff is empty when no changes.

**Setup**:

* Create result where ``original_source == modified_source``

**Expected behavior**: Diff output is empty string.

test_240_generate_context_diff_with_changes
-------------------------------------------------------------------------------

Verify context diff generation produces valid diff output.

**Setup**:

* Create result where ``original_source != modified_source``

**Expected behavior**:

* Diff output contains ``***`` and ``---`` headers
* Diff output contains ``***************`` separators
* Diff output shows actual changes

test_250_generate_context_diff_no_changes
-------------------------------------------------------------------------------

Verify context diff is empty when no changes.

**Setup**:

* Create result where ``original_source == modified_source``

**Expected behavior**: Diff output is empty string.

test_260_diff_file_headers_correct
-------------------------------------------------------------------------------

Verify diff file headers use ``a/`` and ``b/`` prefixes.

**Expected behavior**:

* Unified diff contains ``a/{filename}`` and ``b/{filename}``
* Context diff contains ``a/{filename}`` and ``b/{filename}``

test_270_diff_multiline_changes
-------------------------------------------------------------------------------

Verify diff handles multi-line changes correctly.

**Setup**:

* Create result with changes spanning multiple lines

**Expected behavior**: Diff correctly represents multi-line additions,
deletions, and modifications.

FixEngineResult Tests (300-399)
===============================================================================

test_300_aggregate_statistics_accurate
-------------------------------------------------------------------------------

Verify aggregate statistics match individual file results.

**Setup**:

* Create FixEngineResult with multiple FixApplicationResult objects
* Each has varying counts of applied, skipped, and conflicts

**Expected behavior**: Totals match sum of individual results.

test_310_empty_file_results
-------------------------------------------------------------------------------

Verify FixEngineResult handles empty file_results gracefully.

**Setup**:

* Create FixEngineResult with ``file_results=()``

**Expected behavior**: All totals are zero.

FixEngine.apply_fixes Tests (400-499)
===============================================================================

test_400_apply_fixes_empty_fixes_list
-------------------------------------------------------------------------------

Verify apply_fixes handles empty fixes list.

**Setup**:

* Call ``apply_fixes(source_code, fixes=[], filename='test.py')``

**Expected behavior**:

* Returns FixApplicationResult
* ``modified_source == original_source``
* ``applied_fixes == ()``
* ``skipped_fixes == ()``
* ``conflicts == ()``

test_410_apply_fixes_single_safe_fix
-------------------------------------------------------------------------------

Verify apply_fixes applies a single safe fix.

**Setup**:

* Create a Fix with ``safety=FixSafety.Safe``
* Transformer factory that makes a simple transformation

**Expected behavior**:

* Fix is applied
* ``modified_source`` reflects transformation
* ``applied_fixes`` contains the fix
* ``skipped_fixes == ()``

test_420_apply_fixes_multiple_safe_fixes_no_conflicts
-------------------------------------------------------------------------------

Verify apply_fixes applies multiple non-overlapping fixes.

**Setup**:

* Create fixes targeting different lines
* All with ``safety=FixSafety.Safe``

**Expected behavior**:

* All fixes applied
* ``modified_source`` reflects all transformations
* ``applied_fixes`` contains all fixes

test_430_apply_fixes_reverse_position_order
-------------------------------------------------------------------------------

Verify fixes are applied in reverse position order (end of file first).

**Setup**:

* Create fixes at lines 10, 5, 15, 1
* Track transformation order

**Expected behavior**: Transformations applied in order 15, 10, 5, 1.

test_440_apply_fixes_conflict_same_line
-------------------------------------------------------------------------------

Verify conflict detection when two fixes target same line.

**Setup**:

* Create two fixes both targeting line 5
* Both with ``safety=FixSafety.Safe``

**Expected behavior**:

* First fix (by reverse order) is applied
* Second fix appears in ``conflicts``
* Conflict reason mentions line number

test_450_apply_fixes_transformation_failure
-------------------------------------------------------------------------------

Verify graceful handling when transformation raises exception.

**Setup**:

* Create fix with transformer factory that raises exception

**Expected behavior**:

* Fix appears in ``conflicts`` with reason "Transformation failed."
* Other fixes still processed

test_460_apply_fixes_preserves_filename
-------------------------------------------------------------------------------

Verify result contains correct filename.

**Setup**:

* Call ``apply_fixes`` with ``filename='path/to/file.py'``

**Expected behavior**: ``result.filename == 'path/to/file.py'``

test_470_apply_fixes_default_filename
-------------------------------------------------------------------------------

Verify default filename when not specified.

**Setup**:

* Call ``apply_fixes`` without filename parameter

**Expected behavior**: ``result.filename == '<string>'``

Safety Filtering Tests (500-599)
===============================================================================

test_500_filter_safe_fixes_default_mode
-------------------------------------------------------------------------------

Verify Safe fixes are applied in default mode.

**Setup**:

* Create FixEngine with default ``apply_dangerous=False``
* Create fix with ``safety=FixSafety.Safe``

**Expected behavior**: Fix is applied.

test_510_filter_potentially_unsafe_default_mode
-------------------------------------------------------------------------------

Verify PotentiallyUnsafe fixes are skipped in default mode.

**Setup**:

* Create FixEngine with default ``apply_dangerous=False``
* Create fix with ``safety=FixSafety.PotentiallyUnsafe``

**Expected behavior**:

* Fix appears in ``skipped_fixes``
* Reason mentions ``--apply-dangerous``

test_520_filter_dangerous_default_mode
-------------------------------------------------------------------------------

Verify Dangerous fixes are skipped in default mode.

**Setup**:

* Create FixEngine with default ``apply_dangerous=False``
* Create fix with ``safety=FixSafety.Dangerous``

**Expected behavior**:

* Fix appears in ``skipped_fixes``
* Reason mentions ``--apply-dangerous``

test_530_filter_potentially_unsafe_dangerous_mode
-------------------------------------------------------------------------------

Verify PotentiallyUnsafe fixes are applied in dangerous mode.

**Setup**:

* Create FixEngine with ``apply_dangerous=True``
* Create fix with ``safety=FixSafety.PotentiallyUnsafe``

**Expected behavior**: Fix is applied.

test_540_filter_dangerous_dangerous_mode
-------------------------------------------------------------------------------

Verify Dangerous fixes are applied in dangerous mode.

**Setup**:

* Create FixEngine with ``apply_dangerous=True``
* Create fix with ``safety=FixSafety.Dangerous``

**Expected behavior**: Fix is applied.

test_550_mixed_safety_levels
-------------------------------------------------------------------------------

Verify correct handling of mixed safety levels.

**Setup**:

* Create fixes with all three safety levels
* Use default ``apply_dangerous=False``

**Expected behavior**:

* Safe fix applied
* PotentiallyUnsafe and Dangerous in ``skipped_fixes``

test_560_all_fixes_filtered_produces_no_changes
-------------------------------------------------------------------------------

Verify when all fixes are filtered, result shows no changes.

**Setup**:

* Create FixEngine with default ``apply_dangerous=False``
* All fixes have ``safety=FixSafety.Dangerous``

**Expected behavior**:

* ``modified_source == original_source``
* ``applied_fixes == ()``
* ``skipped_fixes`` contains all fixes

test_570_skipped_fix_reason_includes_safety_value
-------------------------------------------------------------------------------

Verify skipped fix reason includes the safety classification.

**Setup**:

* Create fix with ``safety=FixSafety.PotentiallyUnsafe``
* Use default mode

**Expected behavior**: Reason contains ``potentially_unsafe``.

File I/O Integration Tests (600-699)
===============================================================================

test_600_apply_fixes_to_file_reads_file
-------------------------------------------------------------------------------

Verify apply_fixes_to_file reads source from file.

**Setup**:

* Use pyfakefs to create a file with source code
* Call ``apply_fixes_to_file(file_path, fixes, simulate=True)``

**Expected behavior**: File content is read and processed.

test_610_apply_fixes_to_file_simulate_mode
-------------------------------------------------------------------------------

Verify simulate mode does not write to file.

**Setup**:

* Use pyfakefs to create a file
* Call ``apply_fixes_to_file`` with ``simulate=True``

**Expected behavior**: File content unchanged after call.

test_620_apply_fixes_to_file_write_mode
-------------------------------------------------------------------------------

Verify non-simulate mode writes modified source to file.

**Setup**:

* Use pyfakefs to create a file
* Call ``apply_fixes_to_file`` with ``simulate=False`` (default)
* Provide fix that modifies the source

**Expected behavior**: File content updated with modified source.

test_630_apply_fixes_to_file_no_changes_no_write
-------------------------------------------------------------------------------

Verify file is not written when no changes occur.

**Setup**:

* Use pyfakefs to create a file
* Call ``apply_fixes_to_file`` with empty fixes list

**Expected behavior**: File write not called (verified via mock or timestamp).

test_640_apply_fixes_to_file_preserves_encoding
-------------------------------------------------------------------------------

Verify file read/write uses UTF-8 encoding.

**Setup**:

* Create file with UTF-8 content (non-ASCII characters)
* Apply fix and verify encoding preserved

**Expected behavior**: UTF-8 content correctly read and written.

test_650_apply_fixes_to_file_returns_result
-------------------------------------------------------------------------------

Verify apply_fixes_to_file returns FixApplicationResult.

**Expected behavior**: Returns properly populated FixApplicationResult with
filename matching provided path.

Edge Cases and Error Handling (700-799)
===============================================================================

test_700_apply_fixes_invalid_source_code
-------------------------------------------------------------------------------

Verify handling of unparseable source code.

**Setup**:

* Call ``apply_fixes`` with syntactically invalid Python

**Expected behavior**: Raises appropriate exception from LibCST parsing.

test_710_fix_on_nonexistent_line
-------------------------------------------------------------------------------

Verify handling when fix targets line beyond source end.

**Setup**:

* Create fix targeting line 100 in 10-line source

**Expected behavior**: Graceful handling (transformation may be no-op).

test_720_concurrent_fix_detection
-------------------------------------------------------------------------------

Verify multiple fixes on same line all detected as conflicts.

**Setup**:

* Create 3 fixes all targeting line 5

**Expected behavior**: First applied, remaining 2 in conflicts.

test_730_empty_source_code
-------------------------------------------------------------------------------

Verify handling of empty source code.

**Setup**:

* Call ``apply_fixes`` with ``source_code=''``

**Expected behavior**: Returns result with no changes.

test_740_whitespace_only_source
-------------------------------------------------------------------------------

Verify handling of whitespace-only source.

**Setup**:

* Call ``apply_fixes`` with ``source_code='   \n\n   '``

**Expected behavior**: Graceful handling without crash.

test_750_very_large_fix_count
-------------------------------------------------------------------------------

Verify handling of many fixes (performance sanity check).

**Setup**:

* Create 100+ non-conflicting fixes

**Expected behavior**: All processed without timeout or memory issues.

Implementation Notes
===============================================================================

Testing Approach
-------------------------------------------------------------------------------

**Mock Fix Creation**:

Tests require creating Fix objects with controlled transformer factories.
Helper function for test fixture:

.. code-block:: python

   def create_mock_fix(
       line: int,
       column: int = 1,
       safety: FixSafety = FixSafety.Safe,
       transform_fn: Callable | None = None
   ) -> Fix:
       ''' Creates a mock Fix for testing. '''
       from vibelinter.rules.violations import Violation
       from vibelinter.rules.fixable import Fix, FixSafety

       violation = Violation(
           rule_id='TEST',
           filename='test.py',
           line=line,
           column=column,
           message='Test violation',
           severity='warning',
       )

       if transform_fn is None:
           # Identity transformer
           def transform_fn(module):
               return module

       return Fix(
           violation=violation,
           description='Test fix',
           safety=safety,
           transformer_factory=transform_fn,
       )

**Simple Transformer Factory**:

For tests that need actual transformations, create simple transformers:

.. code-block:: python

   def make_replace_transformer(old: str, new: str):
       ''' Creates transformer that replaces string in source. '''
       import libcst as cst

       class Replacer(cst.CSTTransformer):
           def leave_Name(self, original, updated):
               if updated.value == old:
                   return updated.with_changes(value=new)
               return updated

       def transform(module: cst.Module) -> cst.Module:
           return module.visit(Replacer())

       return transform

Dependencies and Fixtures Needed
-------------------------------------------------------------------------------

**Helper functions** (in test module or fixtures.py):

* ``create_mock_fix(line, column, safety, transform_fn)``
* ``make_replace_transformer(old, new)``
* ``make_failing_transformer()`` - returns transformer that raises

**Filesystem operations**:

* pyfakefs for file I/O tests (test_600_apply_fixes_to_file series)

**Test data fixtures**:

* None needed - inline code snippets sufficient

Testing Through Public API
-------------------------------------------------------------------------------

All fixer functionality is tested through public interfaces:

* ``FixEngine(apply_dangerous)`` constructor
* ``FixEngine.apply_fixes(source_code, fixes, filename)``
* ``FixEngine.apply_fixes_to_file(file_path, fixes, simulate)``
* ``FixApplicationResult`` attributes and methods
* ``FixEngineResult`` attributes

Internal methods ``_filter_by_safety`` and ``_sort_fixes_by_position`` are
tested indirectly through observable behavior in ``apply_fixes`` output.

Immutability Constraints
-------------------------------------------------------------------------------

No immutability violations anticipated. Testing requires only:

* Creating Fix objects (dependency injection)
* Creating FixEngine with constructor parameters
* Parsing code snippets (no monkey-patching)

**Assessment**: 100% coverage achievable without violating immutability.

Third-Party Testing Patterns
-------------------------------------------------------------------------------

* **LibCST**: Standard transformer patterns
* **pyfakefs**: For file I/O tests

Performance Considerations
-------------------------------------------------------------------------------

* Use in-memory code snippets
* Keep transformer factories simple
* Target: All fixer tests complete in < 1 second
* Estimated test count: ~50 tests

Test Module Numbering
-------------------------------------------------------------------------------

* **Test module**: ``test_360_fixer.py``

  * Placed in 300-399 range alongside analysis engine
  * fixer.py is top-level infrastructure like engine.py
  * Follows architectural dependency ordering from summary.rst

Anti-Patterns to Avoid
-------------------------------------------------------------------------------

* **DO NOT** test private methods directly - test via ``apply_fixes`` results
* **DO NOT** mock LibCST internals
* **DO NOT** test against real external sites
* **DO NOT** use actual filesystem for unit tests (use pyfakefs)
* **DO NOT** create overly complex transformer factories

Success Metrics
===============================================================================

Coverage Goals
-------------------------------------------------------------------------------

* **Target line coverage**: 100%
* **Target branch coverage**: 100%
* **Uncovered lines to cover**: 49 lines (from 34% to 100%)
* **Uncovered branches to cover**: 14 branches

Test Count Estimate
-------------------------------------------------------------------------------

* Basic functionality: 6 tests (000-099)
* Data class tests: 4 tests (100-199)
* FixApplicationResult: 8 tests (200-299)
* FixEngineResult: 2 tests (300-399)
* Core apply_fixes: 8 tests (400-499)
* Safety filtering: 8 tests (500-599)
* File I/O integration: 6 tests (600-699)
* Edge cases: 6 tests (700-799)

**Total**: ~48 tests

Validation Criteria
-------------------------------------------------------------------------------

Tests must validate:

* ✓ FixEngine instantiates with correct parameters
* ✓ Empty fixes list produces no-change result
* ✓ Safe fixes are applied in default mode
* ✓ Unsafe fixes are filtered in default mode
* ✓ apply_dangerous=True enables all fixes
* ✓ Fixes applied in reverse position order
* ✓ Line conflicts detected and recorded
* ✓ Transformation failures handled gracefully
* ✓ Unified and context diffs generated correctly
* ✓ File I/O reads and writes with correct encoding
* ✓ Simulate mode prevents file writes
