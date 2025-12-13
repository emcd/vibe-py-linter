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
Test Plan: Fixable Rule Framework (fixable.py)
*******************************************************************************

This test plan covers comprehensive testing of the fixable rule infrastructure,
which provides the base class and data structures for rules that support
automated fixes. This module bridges violation detection (CSTVisitor) with
fix application (CSTTransformer).

Coverage Analysis Summary
===============================================================================

Current Coverage Status
-------------------------------------------------------------------------------

* **Current coverage**: 76% (moderately tested)
* **Target coverage**: 100%
* **Module under test**: ``sources/vibelinter/rules/fixable.py``
* **Lines of code**: 34 statements
* **Uncovered lines**: 84, 92, 124-125, 130, 135, 153-159

Uncovered Functionality by Line Range
-------------------------------------------------------------------------------

1. **Line 84**: ``Fix.render_as_json`` method - JSON serialization

2. **Line 92**: ``Fix.render_as_text`` method - text line rendering

3. **Lines 124-125**: ``FixableRule.__init__`` - base initialization including
   ``_fixes`` list initialization

4. **Line 130**: ``FixableRule.supports_fix`` property

5. **Line 135**: ``FixableRule.fixes`` property - tuple of collected fixes

6. **Lines 153-159**: ``FixableRule._produce_fix`` method - fix creation and
   registration

Components Under Test
-------------------------------------------------------------------------------

* **FixSafety**: Enum classifying fix safety levels (Safe, PotentiallyUnsafe,
  Dangerous)
* **Fix**: Immutable dataclass representing a proposed fix
* **FixableRule**: Abstract base class for rules supporting automated fixes
* **TransformerFactory**: Type alias for transformer factory functions
* **FixSequence**: Type alias for sequences of Fix objects

Test Strategy
===============================================================================

The test strategy employs a concrete test implementation of FixableRule to
verify base class behavior. Tests create minimal rules that exercise the fix
collection infrastructure.

Test Module Structure
-------------------------------------------------------------------------------

Test module: ``tests/test_000_vibelinter/test_140_fixable.py``

The test module follows standard numbering conventions:

* **000-099**: Basic functionality and enum values
* **100-199**: Fix data class functionality
* **200-299**: FixableRule instantiation and properties
* **300-399**: Fix production and collection
* **400-499**: Integration with BaseRule
* **500-599**: Type alias validation

Basic Functionality Tests (000-099)
===============================================================================

test_000_fixsafety_enum_values
-------------------------------------------------------------------------------

Verify FixSafety enum has expected values.

**Expected values**:

* ``FixSafety.Safe`` with value ``'safe'``
* ``FixSafety.PotentiallyUnsafe`` with value ``'potentially_unsafe'``
* ``FixSafety.Dangerous`` with value ``'dangerous'``

test_010_fixsafety_enum_count
-------------------------------------------------------------------------------

Verify FixSafety has exactly three members.

**Expected behavior**: ``len(FixSafety) == 3``

test_020_transformerfactory_type_alias
-------------------------------------------------------------------------------

Verify TransformerFactory type alias is correctly defined.

**Expected behavior**: Type alias accepts callable taking Module and returning
Module.

test_030_fixsequence_type_alias
-------------------------------------------------------------------------------

Verify FixSequence type alias is correctly defined.

**Expected behavior**: Type alias accepts sequences of Fix objects.

Fix Data Class Tests (100-199)
===============================================================================

test_100_fix_instantiation
-------------------------------------------------------------------------------

Verify Fix data class instantiates with required fields.

**Required fields**:

* ``violation``: Violation object this fix addresses
* ``description``: Human-readable description
* ``safety``: FixSafety classification
* ``transformer_factory``: Callable that transforms module

test_110_fix_immutability
-------------------------------------------------------------------------------

Verify Fix instances are immutable.

**Expected behavior**: Attempting to modify attributes raises exception.

test_120_fix_render_as_json
-------------------------------------------------------------------------------

Verify Fix.render_as_json produces correct JSON structure.

**Expected JSON structure**:

.. code-block:: python

   {
       'violation': {...},  # Nested violation JSON
       'description': 'Fix description',
       'safety': 'safe',
   }

**Note**: ``transformer_factory`` is not serialized (not JSON-compatible).

test_130_fix_render_as_text
-------------------------------------------------------------------------------

Verify Fix.render_as_text produces formatted text line.

**Expected format**: ``  {line}:{column} [{safety}] {description}``

**Example**: ``  42:5 [safe] Remove extra whitespace``

test_140_fix_render_as_json_all_safety_levels
-------------------------------------------------------------------------------

Verify JSON rendering works for all safety levels.

**Test cases**:

* Safe fix: ``'safety': 'safe'``
* PotentiallyUnsafe fix: ``'safety': 'potentially_unsafe'``
* Dangerous fix: ``'safety': 'dangerous'``

test_150_fix_render_as_text_all_safety_levels
-------------------------------------------------------------------------------

Verify text rendering includes correct safety indicator.

**Test cases**:

* Safe: ``[safe]``
* PotentiallyUnsafe: ``[potentially_unsafe]``
* Dangerous: ``[dangerous]``

test_160_fix_violation_integration
-------------------------------------------------------------------------------

Verify Fix correctly wraps violation.

**Setup**:

* Create Violation with specific attributes
* Create Fix wrapping the violation

**Expected behavior**: ``fix.violation`` returns original violation with
all attributes intact.

test_170_fix_transformer_factory_callable
-------------------------------------------------------------------------------

Verify transformer_factory is callable and stored correctly.

**Setup**:

* Create identity transformer factory
* Create Fix with the factory

**Expected behavior**: ``fix.transformer_factory(module)`` returns module.

FixableRule Instantiation Tests (200-299)
===============================================================================

test_200_fixablerule_requires_concrete_implementation
-------------------------------------------------------------------------------

Verify FixableRule cannot be instantiated directly (abstract).

**Expected behavior**: Instantiating FixableRule raises TypeError due to
abstract ``rule_id`` property.

test_210_concrete_fixablerule_instantiation
-------------------------------------------------------------------------------

Verify concrete FixableRule subclass instantiates correctly.

**Setup**:

* Create minimal concrete subclass implementing ``rule_id`` and
  ``_analyze_collections``

**Expected behavior**: Instance created successfully with empty fixes list.

test_220_fixablerule_inherits_baserule
-------------------------------------------------------------------------------

Verify FixableRule properly inherits from BaseRule.

**Expected behavior**:

* Has ``filename`` attribute
* Has ``wrapper`` attribute
* Has ``source_lines`` attribute
* Has ``violations`` property

test_230_fixablerule_supports_fix_property
-------------------------------------------------------------------------------

Verify ``supports_fix`` property returns True.

**Expected behavior**: ``rule.supports_fix == True``

test_240_fixablerule_fixes_initially_empty
-------------------------------------------------------------------------------

Verify ``fixes`` property returns empty tuple before analysis.

**Expected behavior**: ``rule.fixes == ()``

test_250_fixablerule_initialization_with_parameters
-------------------------------------------------------------------------------

Verify FixableRule passes parameters to BaseRule.

**Setup**:

* Create concrete rule with specific filename, wrapper, source_lines

**Expected behavior**: All parameters accessible via attributes.

Fix Production and Collection Tests (300-399)
===============================================================================

test_300_produce_fix_single_fix
-------------------------------------------------------------------------------

Verify ``_produce_fix`` creates and registers a fix.

**Setup**:

* Create concrete FixableRule
* Call ``_produce_fix`` with violation, description, transformer

**Expected behavior**: ``rule.fixes`` contains the created fix.

test_310_produce_fix_multiple_fixes
-------------------------------------------------------------------------------

Verify multiple ``_produce_fix`` calls accumulate fixes.

**Setup**:

* Call ``_produce_fix`` three times with different violations

**Expected behavior**: ``len(rule.fixes) == 3``

test_320_produce_fix_default_safety
-------------------------------------------------------------------------------

Verify ``_produce_fix`` uses Safe as default safety level.

**Setup**:

* Call ``_produce_fix`` without safety parameter

**Expected behavior**: Created fix has ``safety == FixSafety.Safe``

test_330_produce_fix_explicit_safety_potentially_unsafe
-------------------------------------------------------------------------------

Verify ``_produce_fix`` accepts PotentiallyUnsafe safety.

**Setup**:

* Call ``_produce_fix`` with ``safety=FixSafety.PotentiallyUnsafe``

**Expected behavior**: Created fix has ``safety == FixSafety.PotentiallyUnsafe``

test_340_produce_fix_explicit_safety_dangerous
-------------------------------------------------------------------------------

Verify ``_produce_fix`` accepts Dangerous safety.

**Setup**:

* Call ``_produce_fix`` with ``safety=FixSafety.Dangerous``

**Expected behavior**: Created fix has ``safety == FixSafety.Dangerous``

test_350_produce_fix_stores_transformer_factory
-------------------------------------------------------------------------------

Verify ``_produce_fix`` stores transformer factory in fix.

**Setup**:

* Create custom transformer factory
* Call ``_produce_fix`` with the factory

**Expected behavior**: ``fix.transformer_factory`` is the same factory.

test_360_produce_fix_stores_description
-------------------------------------------------------------------------------

Verify ``_produce_fix`` stores description in fix.

**Setup**:

* Call ``_produce_fix`` with specific description string

**Expected behavior**: ``fix.description == 'specific description'``

test_370_fixes_property_returns_tuple
-------------------------------------------------------------------------------

Verify ``fixes`` property returns tuple (not list).

**Setup**:

* Produce several fixes
* Access ``rule.fixes``

**Expected behavior**: Result is tuple type.

test_380_fixes_property_is_snapshot
-------------------------------------------------------------------------------

Verify ``fixes`` property returns snapshot (modifications don't affect rule).

**Setup**:

* Produce some fixes
* Get fixes tuple
* Produce more fixes

**Expected behavior**: Original tuple unchanged; new tuple has more fixes.

Integration with BaseRule Tests (400-499)
===============================================================================

test_400_fixablerule_inherits_violations
-------------------------------------------------------------------------------

Verify FixableRule can still produce violations.

**Setup**:

* Create concrete rule that calls ``_produce_violation``

**Expected behavior**: ``rule.violations`` contains produced violations.

test_410_violations_and_fixes_independent
-------------------------------------------------------------------------------

Verify violations and fixes are tracked independently.

**Setup**:

* Produce violation without fix
* Produce violation with fix

**Expected behavior**:

* ``len(rule.violations) == 2``
* ``len(rule.fixes) == 1``

test_420_fix_references_correct_violation
-------------------------------------------------------------------------------

Verify fix correctly references its associated violation.

**Setup**:

* Produce violation
* Produce fix for that violation

**Expected behavior**: ``fix.violation`` is the same object as produced
violation.

test_430_leave_module_triggers_analysis
-------------------------------------------------------------------------------

Verify leave_Module calls _analyze_collections.

**Setup**:

* Create concrete rule with _analyze_collections that produces fix
* Call wrapper.visit(rule)

**Expected behavior**: Fixes produced during _analyze_collections are
accessible after visit.

test_440_metadata_dependencies_inherited
-------------------------------------------------------------------------------

Verify FixableRule can declare METADATA_DEPENDENCIES.

**Setup**:

* Create concrete rule with custom METADATA_DEPENDENCIES

**Expected behavior**: Metadata providers available during visit.

Type Alias Validation Tests (500-599)
===============================================================================

test_500_transformerfactory_accepts_valid_callable
-------------------------------------------------------------------------------

Verify TransformerFactory type validates correct signatures.

**Setup**:

* Create function with signature ``(Module) -> Module``

**Expected behavior**: Type checker accepts function as TransformerFactory.

test_510_fixsequence_accepts_tuple
-------------------------------------------------------------------------------

Verify FixSequence accepts tuple of Fix objects.

**Expected behavior**: Tuple of fixes validates as FixSequence.

test_520_fixsequence_accepts_list
-------------------------------------------------------------------------------

Verify FixSequence accepts list of Fix objects.

**Expected behavior**: List of fixes validates as FixSequence.

Implementation Notes
===============================================================================

Testing Approach
-------------------------------------------------------------------------------

**Concrete Test Rule**:

Tests require a concrete implementation of FixableRule. Create minimal
test fixture:

.. code-block:: python

   class TestableFixableRule(FixableRule):
       ''' Minimal concrete FixableRule for testing. '''

       @property
       def rule_id(self) -> str:
           return 'TEST001'

       def _analyze_collections(self) -> None:
           ''' No-op analysis for testing. '''
           pass

**Helper for Creating Test Fixes**:

.. code-block:: python

   def create_test_violation(
       line: int = 1,
       column: int = 1,
       message: str = 'Test violation'
   ) -> Violation:
       ''' Creates test violation. '''
       from vibelinter.rules.violations import Violation
       return Violation(
           rule_id='TEST001',
           filename='test.py',
           line=line,
           column=column,
           message=message,
           severity='warning',
       )

   def identity_transformer(module):
       ''' Returns module unchanged. '''
       return module

Dependencies and Fixtures Needed
-------------------------------------------------------------------------------

**Helper classes** (in test module):

* ``TestableFixableRule`` - Concrete implementation for testing

**Helper functions**:

* ``create_test_violation(line, column, message)``
* ``identity_transformer(module)``

**Fixtures from rule tests**:

* ``create_rule_wrapper(code, filename)`` - from VBL101 tests

Testing Through Public API
-------------------------------------------------------------------------------

All fixable functionality is tested through public interfaces:

* ``FixSafety`` enum members and values
* ``Fix`` constructor and methods (render_as_json, render_as_text)
* ``FixableRule`` constructor and properties (supports_fix, fixes)

Internal method ``_produce_fix`` is tested by creating a concrete subclass
that calls it and verifying the ``fixes`` property output.

Immutability Constraints
-------------------------------------------------------------------------------

No immutability violations anticipated:

* Fix objects are immutable dataclasses
* Testing via concrete subclass (dependency injection pattern)
* No monkey-patching required

**Assessment**: 100% coverage achievable without violating immutability.

Performance Considerations
-------------------------------------------------------------------------------

* All tests use in-memory code snippets
* Minimal LibCST parsing required
* Target: All fixable tests complete in < 500ms
* Estimated test count: ~35 tests

Test Module Numbering
-------------------------------------------------------------------------------

* **Test module**: ``test_140_fixable.py``

  * Placed in 100-199 range for core rule infrastructure
  * Extends BaseRule (120), precedes registry (130 range)
  * Reflects dependency: fixable rules extend core rule framework

Anti-Patterns to Avoid
-------------------------------------------------------------------------------

* **DO NOT** test abstract FixableRule directly - use concrete subclass
* **DO NOT** access private ``_fixes`` list - use ``fixes`` property
* **DO NOT** mock LibCST internals
* **DO NOT** test implementation of _analyze_collections - that's rule-specific

Pushback Recommendations
===============================================================================

**Fixable module design observations**:

1. **Fix.transformer_factory not serializable**

   * JSON rendering omits transformer_factory (correct behavior)
   * Consider adding note in render_as_json docstring

   **Recommendation**: Document that transformer_factory is intentionally
   excluded from JSON serialization.

2. **FixSafety documentation sparse**

   * Enum values have minimal docstrings
   * Guidance on when to use each level would help rule authors

   **Recommendation**: Expand FixSafety docstrings with examples of when
   each level is appropriate.

3. **TransformerFactory type alias**

   * Type alias is clear but not enforced at runtime
   * Invalid factories will fail at application time, not creation

   **Recommendation**: Consider runtime validation in _produce_fix or
   document that validation happens at fix application time.

**Testability concerns**:

* Module is well-designed for testing
* Concrete subclass pattern works well
* No architectural changes needed

Success Metrics
===============================================================================

Coverage Goals
-------------------------------------------------------------------------------

* **Target line coverage**: 100%
* **Target branch coverage**: 100%
* **Uncovered lines to cover**: 8 lines (from 76% to 100%)

Test Count Estimate
-------------------------------------------------------------------------------

* Basic functionality: 4 tests (000-099)
* Fix data class: 8 tests (100-199)
* FixableRule instantiation: 6 tests (200-299)
* Fix production: 9 tests (300-399)
* BaseRule integration: 5 tests (400-499)
* Type alias validation: 3 tests (500-599)

**Total**: ~35 tests

Validation Criteria
-------------------------------------------------------------------------------

Tests must validate:

* ✓ FixSafety enum has correct values
* ✓ Fix instantiates with all required fields
* ✓ Fix.render_as_json produces valid JSON structure
* ✓ Fix.render_as_text produces correctly formatted output
* ✓ FixableRule subclasses can be instantiated
* ✓ supports_fix property returns True
* ✓ _produce_fix creates and registers fixes
* ✓ fixes property returns tuple of produced fixes
* ✓ Safety levels correctly stored and rendered
* ✓ Multiple fixes accumulate correctly
* ✓ Violations and fixes tracked independently
