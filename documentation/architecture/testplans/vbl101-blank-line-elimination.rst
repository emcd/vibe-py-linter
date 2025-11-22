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
Test Plan: VBL101 Blank Line Elimination
*******************************************************************************

This test plan covers comprehensive testing of the VBL101 rule, which detects
blank lines within function and method bodies to improve vertical compactness
per project coding standards.

Coverage Analysis Summary
===============================================================================

Current Coverage Status
-------------------------------------------------------------------------------

* **Current coverage**: 15% (extremely low - barely tested)
* **Target coverage**: 100%
* **Module under test**: ``sources/vibelinter/rules/implementations/vbl101.py``
* **Lines of code**: ~115 lines
* **Current state**: Implementation exists but lacks comprehensive tests

Uncovered Functionality
-------------------------------------------------------------------------------

Based on the implementation analysis, the following areas need testing:

1. **Rule instantiation and initialization**

   * BaseRule constructor with filename, wrapper, source_lines
   * Rule ID property returning 'VBL101'

2. **Function detection and collection**

   * Detection of function definitions throughout module
   * Position metadata extraction for functions
   * Start and end line calculation
   * Handling of position metadata absence (graceful degradation)
   * Collection of nested functions

3. **Blank line detection logic**

   * Analysis of collected functions for blank lines
   * Blank line detection outside docstrings
   * Docstring state tracking (triple-double and triple-single quotes)
   * Docstring delimiter detection and matching
   * Single-line vs multi-line docstring handling
   * Blank lines inside docstrings (should be allowed)

4. **Violation reporting**

   * Violation object creation for blank lines
   * Correct line number reporting
   * Column number (always 1 for blank lines)
   * Message: "Blank line in function body."
   * Severity: 'warning'

5. **Edge cases**

   * Empty functions
   * Functions with only docstrings
   * Functions with nested functions
   * Docstrings with blank lines inside
   * Mixed single and double quote docstrings in same file
   * Docstring closing on same line as opening
   * Functions at end of file (boundary condition)
   * Functions with complex bodies

Test Strategy
===============================================================================

The test strategy employs in-memory code snippets parsed with LibCST to verify
VBL101 behavior across all scenarios. This approach provides fast, maintainable
tests without filesystem dependencies.

Test Module Structure
-------------------------------------------------------------------------------

Test module: ``tests/test_000_vibelinter/test_410_rules_vbl101.py``

The test module will follow the standard numbering convention:

* **000-099**: Basic functionality and rule instantiation
* **100-199**: Simple blank line detection (no docstrings)
* **200-299**: Docstring handling (blank lines inside docstrings)
* **300-399**: Edge cases and boundary conditions
* **400-499**: Nested functions and complex scenarios
* **500-599**: Integration with metadata and position providers

Basic Functionality Tests (000-099)
===============================================================================

test_000_rule_instantiation
-------------------------------------------------------------------------------

Verify VBL101 rule can be instantiated with required parameters.

**Required parameters**:

* ``filename``: Path to source file
* ``wrapper``: LibCST metadata wrapper
* ``source_lines``: Tuple of source lines

**Expected behavior**: Rule instantiates successfully.

test_010_rule_id
-------------------------------------------------------------------------------

Verify the rule reports correct rule ID.

**Expected behavior**: ``rule.rule_id == 'VBL101'``

test_020_empty_module
-------------------------------------------------------------------------------

Test VBL101 on an empty module (no functions).

**Code example**:

.. code-block:: python

   # Empty module

**Expected behavior**: No violations generated.

test_030_module_with_no_functions
-------------------------------------------------------------------------------

Test VBL101 on module with code but no functions.

**Code example**:

.. code-block:: python

   x = 42
   y = 'hello'

   class MyClass:
       pass

**Expected behavior**: No violations (only functions are analyzed).

test_040_multiple_functions_detected
-------------------------------------------------------------------------------

Verify that multiple function definitions are detected and analyzed.

**Code example**:

.. code-block:: python

   def func1():
       x = 1

       y = 2

   def func2():
       a = 3

       b = 4

**Expected behavior**: Violations detected in both functions (observable via violations produced).

test_050_violations_initially_empty
-------------------------------------------------------------------------------

Verify violations list is empty before analysis.

**Expected behavior**: ``rule._violations == []`` before ``visit``.

Simple Blank Line Detection Tests (100-199)
===============================================================================

test_100_single_blank_line_in_function
-------------------------------------------------------------------------------

Test detection of single blank line within function body.

**Code example**:

.. code-block:: python

   def my_function():
       x = 1

       y = 2

**Expected behavior**: One violation for the blank line between statements.

test_110_multiple_blank_lines_in_function
-------------------------------------------------------------------------------

Test detection of multiple blank lines within single function.

**Code example**:

.. code-block:: python

   def my_function():
       x = 1

       y = 2

       z = 3

**Expected behavior**: Two violations for the blank lines between statements.

test_120_no_blank_lines_clean_function
-------------------------------------------------------------------------------

Test that compact functions generate no violations.

**Code example**:

.. code-block:: python

   def my_function():
       x = 1
       y = 2
       return x + y

**Expected behavior**: No violations.

test_130_blank_line_after_function_def
-------------------------------------------------------------------------------

Test that blank line immediately after function definition is detected.

**Code example**:

.. code-block:: python

   def my_function():

       x = 1

**Expected behavior**: One violation for the blank line immediately after the function definition.

test_140_multiple_functions_with_violations
-------------------------------------------------------------------------------

Test multiple functions each with blank lines.

**Code example**:

.. code-block:: python

   def func1():
       x = 1

       y = 2

   def func2():
       a = 3

       b = 4

**Expected behavior**: Two violations (one in func1, one in func2).

test_150_method_blank_line_detection
-------------------------------------------------------------------------------

Test blank line detection within class methods.

**Code example**:

.. code-block:: python

   class MyClass:
       def my_method(self):
           x = 1

           y = 2

**Expected behavior**: One violation in method body.

test_160_violation_line_numbers
-------------------------------------------------------------------------------

Verify violation line numbers are accurate and correspond to actual blank line positions.

**Code example**:

.. code-block:: python

   def my_function():
       x = 1

       y = 2

       z = 3

**Expected behavior**: Violations reported with correct line numbers matching the blank line positions in source.

test_170_violation_message_format
-------------------------------------------------------------------------------

Verify violation message is correct.

**Expected message**: ``"Blank line in function body."``

**Expected severity**: ``'warning'``

test_180_violation_column_number
-------------------------------------------------------------------------------

Verify violation column is always 1 for blank lines.

**Expected behavior**: All violations have ``column=1``.

Docstring Handling Tests (200-299)
===============================================================================

test_200_blank_lines_inside_triple_double_docstring
-------------------------------------------------------------------------------

Test that blank lines inside triple-double-quote docstrings are allowed.

**Code example**:

.. code-block:: python

   def my_function():
       ''' This is a docstring.

           It has blank lines inside.

           This is allowed.
       '''
       x = 1

**Expected behavior**: No violations (blank lines inside docstring are OK).

test_210_blank_lines_inside_triple_single_docstring
-------------------------------------------------------------------------------

Test that blank lines inside triple-single-quote docstrings are allowed.

**Code example**:

.. code-block:: python

   def my_function():
       """ This is a docstring.

           It has blank lines inside.

           This is allowed.
       """
       x = 1

**Expected behavior**: No violations.

test_220_blank_line_after_docstring
-------------------------------------------------------------------------------

Test that blank line after docstring (but still in function body) is detected.

**Code example**:

.. code-block:: python

   def my_function():
       ''' Short docstring. '''

       x = 1

**Expected behavior**: One violation (line after docstring).

test_230_single_line_docstring
-------------------------------------------------------------------------------

Test function with single-line docstring and no blank lines.

**Code example**:

.. code-block:: python

   def my_function():
       ''' Does something. '''
       return 42

**Expected behavior**: No violations.

test_240_multiline_docstring_closes_on_same_line
-------------------------------------------------------------------------------

Test docstring that opens and closes on same line (but uses triple quotes).

**Code example**:

.. code-block:: python

   def my_function():
       ''' Short single-line docstring with triple quotes. '''
       x = 1

**Expected behavior**: No violations.

test_250_docstring_with_delimiter_in_content
-------------------------------------------------------------------------------

Test docstring containing the delimiter characters in content.

**Code example**:

.. code-block:: python

   def my_function():
       ''' This docstring mentions ''' in the text.
           But it's still part of the docstring.
       '''
       x = 1

**Expected behavior**: No violations (docstring delimiter tracking works).

test_260_mixed_docstring_types_in_file
-------------------------------------------------------------------------------

Test file with both triple-single and triple-double quote docstrings.

**Code example**:

.. code-block:: python

   def func1():
       ''' Uses triple-single quotes. '''
       x = 1

   def func2():
       """ Uses triple-double quotes. """
       y = 2

**Expected behavior**: No violations (both types handled correctly).

test_270_function_with_only_docstring
-------------------------------------------------------------------------------

Test function containing only a docstring, no other code.

**Code example**:

.. code-block:: python

   def my_function():
       ''' This function only has a docstring. '''

**Expected behavior**: No violations.

test_280_blank_line_before_docstring
-------------------------------------------------------------------------------

Test blank line between function def and docstring.

**Code example**:

.. code-block:: python

   def my_function():

       ''' Docstring after blank line. '''
       x = 1

**Expected behavior**: One violation (blank line before docstring).

test_290_docstring_not_first_statement
-------------------------------------------------------------------------------

Test that blank line detection works when docstring is not first statement.

**Code example**:

.. code-block:: python

   def my_function():
       x = 1
       ''' This is actually a string literal, not a docstring. '''

       y = 2

**Expected behavior**: One violation (blank line after string literal).

Edge Cases and Boundary Conditions (300-399)
===============================================================================

test_300_empty_function_body
-------------------------------------------------------------------------------

Test function with only ``pass`` statement.

**Code example**:

.. code-block:: python

   def my_function():
       pass

**Expected behavior**: No violations.

test_310_function_with_only_pass_and_blank
-------------------------------------------------------------------------------

Test function with blank line and pass.

**Code example**:

.. code-block:: python

   def my_function():

       pass

**Expected behavior**: One violation.

test_320_function_at_end_of_file
-------------------------------------------------------------------------------

Test function at end of file (boundary condition for line ranges).

**Code example**:

.. code-block:: python

   def my_function():
       x = 1

       y = 2

**Expected behavior**: One violation (boundary condition handled).

test_330_function_with_blank_lines_in_string
-------------------------------------------------------------------------------

Test that blank lines inside string literals don't cause false positives.

**Code example**:

.. code-block:: python

   def my_function():
       text = '''
       This is a string

       with blank lines
       '''
       return text

**Expected behavior**: No violations (strings are not docstrings in this context).

Note: Current implementation may flag this as violation since it only tracks
docstrings, not all triple-quoted strings. This test will clarify behavior.

test_340_function_with_comments_on_blank_lines
-------------------------------------------------------------------------------

Test that lines with only whitespace (no comments) are detected.

**Code example**:

.. code-block:: python

   def my_function():
       x = 1
       # This is a comment, not blank

       # The line above is blank and should violate
       y = 2

**Expected behavior**: One violation (truly blank line).

test_350_indented_blank_lines
-------------------------------------------------------------------------------

Test that blank lines with whitespace (indented) are still detected.

**Code example**:

.. code-block:: python

   def my_function():
       x = 1

       y = 2  # Line above has whitespace but is "blank"

**Expected behavior**: One violation (whitespace-only line).

test_360_very_long_function
-------------------------------------------------------------------------------

Test function with many statements and multiple blank lines.

**Code example**:

.. code-block:: python

   def my_function():
       a = 1

       b = 2
       c = 3

       d = 4
       e = 5

       return a + b + c + d + e

**Expected behavior**: Three violations.

test_370_position_metadata_unavailable
-------------------------------------------------------------------------------

Test graceful handling when position metadata is not available.

**Test approach**:

* Test with wrapper that lacks complete position metadata
* Verify rule handles metadata absence gracefully

**Expected behavior**: No crash, rule continues processing other functions successfully.

test_380_source_lines_boundary
-------------------------------------------------------------------------------

Test handling of boundary conditions with source line access.

**Test approach**:

* Test functions at end of file
* Verify proper handling of line number boundaries

**Expected behavior**: No crash, boundary conditions handled gracefully.

Nested Functions and Complex Scenarios (400-499)
===============================================================================

test_400_nested_function_definitions
-------------------------------------------------------------------------------

Test that nested function definitions are both analyzed.

**Code example**:

.. code-block:: python

   def outer():
       x = 1

       def inner():
           y = 2

           z = 3
       return inner()

**Expected behavior**: Two violations (one in outer, one in inner).

test_410_nested_function_no_violations_outer
-------------------------------------------------------------------------------

Test outer function clean, inner function with violation.

**Code example**:

.. code-block:: python

   def outer():
       x = 1
       def inner():
           y = 2

           z = 3
       return inner()

**Expected behavior**: One violation (only in inner function).

test_420_closure_with_blank_lines
-------------------------------------------------------------------------------

Test closure creation with blank lines in both functions.

**Code example**:

.. code-block:: python

   def create_closure():
       captured = 42

       def inner():
           result = captured

           return result * 2
       return inner

**Expected behavior**: Two violations.

test_430_deeply_nested_functions
-------------------------------------------------------------------------------

Test multiple levels of function nesting.

**Code example**:

.. code-block:: python

   def level1():
       def level2():
           def level3():
               x = 1

               y = 2
           return level3()
       return level2()

**Expected behavior**: One violation (in level3).

test_440_lambda_expressions
-------------------------------------------------------------------------------

Test that lambda expressions are not analyzed (they are not FunctionDef nodes).

**Code example**:

.. code-block:: python

   def my_function():
       f = lambda x: x + 1

       return f(42)

**Expected behavior**: One violation (blank line in my_function, lambda ignored).

test_450_async_function_definitions
-------------------------------------------------------------------------------

Test async functions are analyzed the same as regular functions.

**Code example**:

.. code-block:: python

   async def my_async_function():
       x = await some_coroutine()

       y = await another_coroutine()

**Expected behavior**: One violation.

test_460_generator_functions
-------------------------------------------------------------------------------

Test generator functions are analyzed normally.

**Code example**:

.. code-block:: python

   def my_generator():
       yield 1

       yield 2

**Expected behavior**: One violation.

test_470_decorated_functions
-------------------------------------------------------------------------------

Test decorated functions are analyzed (decorator doesn't affect body).

**Code example**:

.. code-block:: python

   @decorator
   def my_function():
       x = 1

       y = 2

**Expected behavior**: One violation.

test_480_staticmethod_and_classmethod
-------------------------------------------------------------------------------

Test static and class methods are analyzed.

**Code example**:

.. code-block:: python

   class MyClass:
       @staticmethod
       def static_method():
           x = 1

           return x

       @classmethod
       def class_method(cls):
           y = 2

           return y

**Expected behavior**: Two violations.

test_490_function_with_multi_statement_lines
-------------------------------------------------------------------------------

Test that only truly blank lines are detected (not lines with semicolons).

**Code example**:

.. code-block:: python

   def my_function():
       x = 1; y = 2

       z = 3

**Expected behavior**: One violation (blank line only).

Integration and Metadata Tests (500-599)
===============================================================================

test_500_metadata_wrapper_integration
-------------------------------------------------------------------------------

Test integration with LibCST MetadataWrapper and PositionProvider.

**Test approach**:

* Create proper MetadataWrapper with PositionProvider
* Verify positions are correctly resolved

**Expected behavior**: Positions accurately reflect source code locations.

test_510_source_lines_consistency
-------------------------------------------------------------------------------

Test that source_lines tuple matches parsed code.

**Test approach**:

* Parse code with LibCST
* Split code into lines for source_lines
* Verify line numbers in violations match source_lines indices

**Expected behavior**: Violations reference correct source lines.

test_520_violation_context_extraction
-------------------------------------------------------------------------------

Test that violations include enough information for context extraction.

**Test approach**:

* Generate violations
* Verify line, column, filename are present

**Expected behavior**: All fields needed for context extraction are populated.

test_530_multiple_violations_sorting
-------------------------------------------------------------------------------

Test that multiple violations are reported in line-number order.

**Code example**:

.. code-block:: python

   def my_function():
       x = 1

       y = 2

       z = 3

       return x + y + z

**Expected behavior**: Violations in ascending line order (3, 5, 7).

test_540_rule_descriptor_registration
-------------------------------------------------------------------------------

Test that VBL101 is properly registered in RULE_DESCRIPTORS.

**Expected behavior**:

* ``RULE_DESCRIPTORS['VBL101']`` exists
* ``vbl_code == 'VBL101'``
* ``descriptive_name == 'blank-line-elimination'``
* ``category == 'readability'``
* ``subcategory == 'compactness'``
* ``rule_class == VBL101``

test_550_baseline_rule_framework_compliance
-------------------------------------------------------------------------------

Test VBL101 complies with BaseRule contract.

**Test approach**:

* Verify rule has required ``rule_id`` property
* Verify rule produces violations when run on code with blank lines
* Verify rule integrates properly with BaseRule visitor pattern

**Expected behavior**: Full compliance with BaseRule interface observable through proper violation generation.

Implementation Notes
===============================================================================

Testing Approach
-------------------------------------------------------------------------------

**In-memory testing strategy**:

1. **Code snippets** created directly in test functions

   * Parse with LibCST on the fly
   * Create MetadataWrapper with PositionProvider
   * Best for all tests - fast and maintainable

2. **Helper functions** for common setup

   * ``create_rule_wrapper(code, filename)`` - Creates wrapper and source_lines
   * ``run_vbl101(code, filename)`` - Runs rule and returns violations
   * Reduces boilerplate in each test

3. **No filesystem dependencies**

   * All tests use in-memory code strings
   * No pyfakefs needed for VBL101
   * Fast test execution (target: < 500ms for all VBL101 tests)

Dependencies and Fixtures Needed
-------------------------------------------------------------------------------

**Helper functions** (inline in test module or in fixtures.py):

.. code-block:: python

   def create_rule_wrapper(code: str, filename: str = 'test.py'):
       ''' Creates LibCST wrapper with metadata for testing VBL101. '''
       from libcst import parse_module
       from libcst.metadata import MetadataWrapper

       # Parse code into CST module
       module = parse_module(code)
       # Create metadata wrapper with required providers
       wrapper = MetadataWrapper(module)
       # Split source into lines for context extraction
       source_lines = tuple(code.splitlines())
       return wrapper, source_lines

   def run_vbl101(code: str, filename: str = 'test.py'):
       ''' Runs VBL101 rule on code snippet and returns violations. '''
       from vibelinter.rules.implementations.vbl101 import VBL101

       wrapper, source_lines = create_rule_wrapper(code, filename)
       rule = VBL101(
           filename=filename,
           wrapper=wrapper,
           source_lines=source_lines,
       )
       # Visit the module to collect data and analyze
       wrapper.visit(rule)
       return rule.violations

**Dependencies requiring injection**:

* None - VBL101 is self-contained with LibCST

**Filesystem operations**:

* None - All tests use in-memory code

**Test data fixtures**:

* None needed - Inline code snippets are sufficient

Testing Through Public API
-------------------------------------------------------------------------------

**Testing Philosophy**:

All VBL101 functionality is tested exclusively through its public API:

* Rule instantiation (constructor)
* ``rule_id`` property
* ``violations`` property (tuple of Violation objects)

**Observable Behaviors**:

* Function detection - Verified by violations appearing for functions with blank lines
* Blank line detection - Verified by violations at correct line numbers
* Docstring handling - Verified by absence of violations for blank lines in docstrings
* Violation reporting - Verified by violation message, severity, and position

**Implementation Details**:

Internal implementation details (private methods, collection mechanisms, state tracking)
are not tested directly. Instead, tests verify the rule produces correct violations
for various input scenarios, confirming the implementation works correctly without
coupling tests to implementation specifics.

Immutability Constraints
-------------------------------------------------------------------------------

No immutability constraint violations anticipated. VBL101 testing requires
only:

* Creating LibCST wrappers (standard operation)
* Instantiating VBL101 with required parameters (dependency injection)
* Parsing code snippets (no monkey-patching needed)

**Assessment**: 100% coverage achievable without violating immutability.

Third-Party Testing Patterns
-------------------------------------------------------------------------------

* **LibCST metadata**: Standard LibCST testing patterns (wrapper creation)
* **PositionProvider**: Built-in LibCST metadata provider
* **No external network calls**: All testing is local

Performance Considerations
-------------------------------------------------------------------------------

* Use in-memory code snippets (no file I/O)
* Parse code once per test (cached by LibCST internally)
* Keep test snippets minimal and focused
* Target: All VBL101 tests complete in < 500ms
* Estimated test count: ~55 tests × ~5ms each = ~275ms total

Test Module Numbering
-------------------------------------------------------------------------------

* **Test module**: ``test_410_rules_vbl101.py``

  * Placed in 400-499 range for rule implementations
  * First rule in the suite (410 is first in the rules block)
  * VBL201 would be 420, VBL202 would be 430, etc.
  * Follows subpackage numbering convention from summary.rst

Anti-Patterns to Avoid
-------------------------------------------------------------------------------

* **DO NOT** test private methods or internal state directly - test exclusively through public API
* **DO NOT** inspect internal attributes like ``_function_ranges`` or ``_violations`` - use public ``violations`` property
* **DO NOT** mock LibCST internals - use real LibCST objects
* **DO NOT** create actual files - use in-memory code snippets
* **DO NOT** test implementation details (state machines, algorithms) - test observable
  behavior (violations produced or not produced)
* **DO NOT** verify method calls or execution order - verify outcomes only

Pushback Recommendations
===============================================================================

**VBL101 design observations**:

1. **String literal handling**

   * Current implementation tracks docstrings at function start
   * Triple-quoted string literals (not docstrings) elsewhere may contain blank lines
   * May produce false positives for string literals with blank lines

   **Recommendation**: Consider enhancing string tracking to recognize all
   triple-quoted strings, or document that blank lines in non-docstring
   string literals may trigger violations. Current implementation is simple
   but may need refinement based on test results.

2. **Position metadata dependency**

   * Gracefully handles absence of position metadata
   * Silent skip means functions without positions are ignored
   * No warning or diagnostic for debugging

   **Recommendation**: Consider logging when functions are skipped due to
   missing metadata. This aids debugging metadata provider issues.

3. **Boundary condition handling**

   * Implementation checks for line numbers exceeding source_lines length
   * This prevents index errors but may silently skip function ends
   * Could indicate metadata/source mismatch

   **Recommendation**: Consider logging or warning when boundary conditions
   trigger, as it may indicate a problem with source_lines vs metadata
   consistency.

4. **Docstring delimiter tracking**

   * Current tracking counts delimiters to detect single-line docstrings
   * Relies on delimiter counting to track docstring state
   * May have edge cases with delimiter characters in string content

   **Recommendation**: Current approach is sound for well-formed code. Testing
   will validate edge case handling.

**Testability concerns**:

* VBL101 is well-designed for testing
* Collection-then-analysis pattern is ideal for test verification
* All functionality accessible via public API
* No architectural changes needed for testability

Success Metrics
===============================================================================

Coverage Goals
-------------------------------------------------------------------------------

* **Target line coverage**: 100%
* **Target branch coverage**: 100%
* **Uncovered lines to cover**: ~98 lines (from current 15% to 100%)
* All public methods covered
* All violation paths exercised
* All edge cases tested

Test Count Estimate
-------------------------------------------------------------------------------

* Basic functionality: 6 tests
* Simple blank line detection: 9 tests
* Docstring handling: 10 tests
* Edge cases and boundaries: 9 tests
* Nested functions and complex scenarios: 10 tests
* Integration and metadata: 6 tests

**Total**: ~50 tests

Validation Criteria
-------------------------------------------------------------------------------

Tests must validate:

* ✓ VBL101 instantiates correctly
* ✓ Blank lines in function bodies are detected
* ✓ Blank lines inside docstrings are allowed
* ✓ Both triple-single and triple-double quote docstrings work
* ✓ Single-line and multi-line docstrings handled correctly
* ✓ Nested functions are both analyzed
* ✓ Violation messages are accurate
* ✓ Line numbers in violations are correct
* ✓ Methods (not just functions) are analyzed
* ✓ Edge cases are handled gracefully
* ✓ No false positives for legitimate blank lines in docstrings

Potential Challenges
===============================================================================

1. **Docstring tracking complexity**

   * Challenge: Ensuring docstring state machine is correct
   * Solution: Comprehensive tests of docstring scenarios (200-299 range)

2. **Triple-quoted string literals vs docstrings**

   * Challenge: Distinguishing docstrings from other triple-quoted strings
   * Solution: Test to document current behavior; may reveal enhancement needs

3. **Nested function position ranges**

   * Challenge: Ensuring nested function ranges don't interfere
   * Solution: Explicit tests of nested scenarios (400-499 range)

4. **Metadata provider integration**

   * Challenge: Creating proper test setup with PositionProvider
   * Solution: Helper fixture abstracts wrapper creation (500-599 range)

5. **Source line boundary conditions**

   * Challenge: Edge cases at file end or with mismatched metadata
   * Solution: Boundary tests (300-399 range) and defensive test design

Priority and Implementation Order
===============================================================================

**High Priority** (implement first):

1. Basic functionality tests (000-099) - Foundation
2. Simple blank line detection (100-199) - Core feature
3. Docstring handling (200-299) - Critical for avoiding false positives

**Medium Priority** (implement second):

4. Edge cases (300-399) - Robustness
5. Integration tests (500-599) - Verify metadata integration

**Lower Priority** (implement last):

6. Nested functions (400-499) - Advanced scenarios

Estimated Complexity
-------------------------------------------------------------------------------

**Medium complexity** - VBL101 testing is straightforward with well-defined
behavior, but requires careful testing of docstring state tracking and nested
function scenarios.

Implementation Priority
-------------------------------------------------------------------------------

**High priority** - VBL101 currently has only 15% coverage and is an active
rule in the linter. Comprehensive testing is needed to ensure correctness and
prevent regressions.
