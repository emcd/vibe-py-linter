*******************************************************************************
Test Plan: VBL201 Import Hub Enforcement
*******************************************************************************

This test plan covers comprehensive testing of the VBL201 rule, which enforces
the import hub pattern by ensuring non-hub modules only contain private imports,
future imports, or function-local imports.

Coverage Analysis Summary
===============================================================================

Current Coverage Status
-------------------------------------------------------------------------------

* **Current coverage**: 0% (no tests exist yet)
* **Target coverage**: 100%
* **Module under test**: ``sources/vibelinter/rules/implementations/vbl201.py``

Key Functionality to Test
-------------------------------------------------------------------------------

1. **Hub module detection**

   * Pattern matching against configurable hub patterns
   * Default patterns: ``__init__.py``, ``__main__.py``, ``__.py``, ``__/imports.py``
   * Custom patterns from configuration

2. **Import classification**

   * Future imports (``from __future__ import ...``)
   * Private name imports (names starting with ``_``)
   * Simple imports (``import foo``)
   * From imports (``from foo import bar``)
   * Star imports (``from foo import *``)

3. **Function-local imports**

   * Tracking function depth
   * Allowing imports inside function bodies
   * Nested function handling

4. **Violation reporting**

   * Simple import violations with module names
   * From import violations with imported names
   * Proper line/column positioning
   * Severity levels (warnings)

5. **Edge cases**

   * Dotted module names (``from foo.bar.baz import qux``)
   * Aliased imports (``from foo import bar as _bar``)
   * Multiple imports in one statement
   * Relative imports (``from . import foo``)
   * Mixed private/public imports

Test Strategy
===============================================================================

The test strategy employs a hybrid approach combining in-memory test snippets
for simple cases and file-based test data for complex scenarios.

Test Data Organization
-------------------------------------------------------------------------------

Test snippets will be organized under ``tests/data/snippets/vbl201/``:

* ``valid/`` - Code snippets that should NOT trigger VBL201 violations

  * ``hub_modules/`` - Hub modules with various import patterns
  * ``private_imports/`` - Non-hub modules with private imports
  * ``future_imports/`` - __future__ imports
  * ``local_imports/`` - Function-local imports
  * ``mixed_valid/`` - Complex valid combinations

* ``invalid/`` - Code snippets that SHOULD trigger VBL201 violations

  * ``simple_imports/`` - Direct ``import foo`` statements
  * ``public_from_imports/`` - ``from foo import bar`` with public names
  * ``star_imports/`` - ``from foo import *`` statements
  * ``mixed_invalid/`` - Combinations of valid and invalid imports

Test Module Structure
-------------------------------------------------------------------------------

Test module: ``tests/test_000_vibelinter/test_420_rules_vbl201.py``

The test module will follow the standard numbering convention:

* **000-099**: Basic functionality and rule instantiation
* **100-199**: Hub module detection
* **200-299**: Import classification (valid cases)
* **300-399**: Import violations (invalid cases)
* **400-499**: Edge cases and complex scenarios
* **500-599**: Configuration handling

Basic Functionality Tests (000-099)
===============================================================================

test_000_rule_instantiation
-------------------------------------------------------------------------------

Verify VBL201 rule can be instantiated with required parameters:

* ``filename``: Path to source file
* ``wrapper``: LibCST metadata wrapper
* ``source_lines``: Tuple of source lines

**Expected behavior**: Rule instantiates successfully with default hub patterns.

test_010_rule_id
-------------------------------------------------------------------------------

Verify the rule reports correct rule ID.

**Expected behavior**: ``rule.rule_id == 'VBL201'``

test_020_empty_module
-------------------------------------------------------------------------------

Test VBL201 on an empty module (no imports).

**Expected behavior**: No violations generated.

test_030_hub_patterns_default
-------------------------------------------------------------------------------

Verify default hub patterns are set correctly when not provided.

**Expected behavior**: Hub patterns include ``__init__.py``, ``__main__.py``,
``__.py``, ``__/imports.py``

test_040_hub_patterns_custom
-------------------------------------------------------------------------------

Verify custom hub patterns can be provided via configuration.

**Expected behavior**: Rule uses custom patterns instead of defaults.

Hub Module Detection Tests (100-199)
===============================================================================

test_100_hub_init_module
-------------------------------------------------------------------------------

Test that ``__init__.py`` files are recognized as hub modules.

**Test approach**:

* Create module with filename ending in ``__init__.py``
* Include public imports (should be allowed)

**Expected behavior**: No violations for public imports in ``__init__.py``.

test_110_hub_main_module
-------------------------------------------------------------------------------

Test that ``__main__.py`` files are recognized as hub modules.

**Expected behavior**: No violations for public imports in ``__main__.py``.

test_120_hub_dunder_module
-------------------------------------------------------------------------------

Test that ``__.py`` files are recognized as hub modules.

**Expected behavior**: No violations for public imports in ``__.py``.

test_130_hub_imports_module
-------------------------------------------------------------------------------

Test that ``__/imports.py`` files are recognized as hub modules.

**Test approach**:

* Use path matching for ``__/imports.py`` pattern
* Test with full path containing ``__/imports.py``

**Expected behavior**: No violations for public imports.

test_140_hub_pattern_matching
-------------------------------------------------------------------------------

Test glob pattern matching for hub module detection.

**Test cases**:

* Exact filename match
* Path-based pattern match
* Pattern with wildcards (if supported)

**Expected behavior**: All matching patterns correctly identify hub modules.

test_150_non_hub_module
-------------------------------------------------------------------------------

Test that regular modules are NOT identified as hub modules.

**Test approach**:

* Use filename ``utils.py`` or ``helpers.py``
* Verify ``_is_hub_module`` returns False

**Expected behavior**: Regular modules are not hubs.

Valid Import Tests (200-299)
===============================================================================

test_200_future_imports
-------------------------------------------------------------------------------

Test that ``from __future__ import ...`` is always allowed.

**Test cases**:

* ``from __future__ import annotations``
* ``from __future__ import division, print_function``
* Multiple future imports

**Expected behavior**: No violations for any future import.

test_210_private_simple_alias
-------------------------------------------------------------------------------

Test private import via alias on simple import.

**Code example**:

.. code-block:: python

   import json as _json
   import pathlib as _pathlib

**Expected behavior**: No violations (alias makes name private).

**Note**: Current implementation may NOT support this - simple imports are
always flagged. This test will clarify the behavior.

test_220_private_from_import_alias
-------------------------------------------------------------------------------

Test private import via alias on from import.

**Code example**:

.. code-block:: python

   from pathlib import Path as _Path
   from json import loads as _json_loads

**Expected behavior**: No violations (alias is private).

test_230_private_from_import_name
-------------------------------------------------------------------------------

Test import of names that start with underscore.

**Code example**:

.. code-block:: python

   from . import __
   from . import _helpers
   from mymodule import _internal_function

**Expected behavior**: No violations (imported names are private).

test_240_mixed_private_imports
-------------------------------------------------------------------------------

Test from import with all names private (some aliased, some not).

**Code example**:

.. code-block:: python

   from . import __, _types
   from json import loads as _loads, dumps as _dumps

**Expected behavior**: No violations (all resulting names are private).

test_250_function_local_imports
-------------------------------------------------------------------------------

Test that imports inside function bodies are allowed.

**Code example**:

.. code-block:: python

   def my_function():
       import json
       from pathlib import Path
       return json.loads('{}')

**Expected behavior**: No violations for function-local imports.

test_260_nested_function_imports
-------------------------------------------------------------------------------

Test imports in nested functions.

**Code example**:

.. code-block:: python

   def outer():
       def inner():
           import json
           return json.loads('{}')
       return inner()

**Expected behavior**: No violations (depth tracking handles nesting).

test_270_method_local_imports
-------------------------------------------------------------------------------

Test imports inside class methods.

**Code example**:

.. code-block:: python

   class MyClass:
       def my_method(self):
           import json
           return json.loads('{}')

**Expected behavior**: No violations for method-local imports.

Invalid Import Tests (300-399)
===============================================================================

test_300_simple_import_violation
-------------------------------------------------------------------------------

Test that simple imports trigger violations in non-hub modules.

**Code example**:

.. code-block:: python

   import json
   import pathlib

**Expected behavior**: Two violations reported for ``json`` and ``pathlib``.

test_310_from_import_public_name
-------------------------------------------------------------------------------

Test from import with public name triggers violation.

**Code example**:

.. code-block:: python

   from pathlib import Path
   from json import loads

**Expected behavior**: Violations for both imports.

test_320_star_import_violation
-------------------------------------------------------------------------------

Test that star imports always trigger violations in non-hub modules.

**Code example**:

.. code-block:: python

   from pathlib import *
   from json import *

**Expected behavior**: Violations for star imports.

test_330_mixed_private_public
-------------------------------------------------------------------------------

Test from import with mix of private and public names.

**Code example**:

.. code-block:: python

   from mymodule import public_func, _private_func

**Expected behavior**: Violation (not all names are private).

test_340_public_alias_on_private
-------------------------------------------------------------------------------

Test import of private name with public alias.

**Code example**:

.. code-block:: python

   from mymodule import _private as public

**Expected behavior**: Violation (resulting name is public).

test_350_relative_import_public
-------------------------------------------------------------------------------

Test relative imports with public names.

**Code example**:

.. code-block:: python

   from . import utils
   from .. import helpers
   from ...package import module

**Expected behavior**: Violations for all public relative imports.

test_360_dotted_module_import
-------------------------------------------------------------------------------

Test from imports with dotted module names.

**Code example**:

.. code-block:: python

   from foo.bar.baz import qux
   from package.subpackage.module import SomeClass

**Expected behavior**: Violations for public names from dotted modules.

Edge Cases and Complex Scenarios (400-499)
===============================================================================

test_400_empty_from_import
-------------------------------------------------------------------------------

Test edge case of from import with no names (should not occur in valid Python).

**Expected behavior**: Graceful handling without crashes.

test_410_import_with_multiple_names
-------------------------------------------------------------------------------

Test simple import with multiple comma-separated names.

**Code example**:

.. code-block:: python

   import json, pathlib, sys

**Expected behavior**: Violation for the first import (libcst may split these).

test_420_attribute_module_reference
-------------------------------------------------------------------------------

Test that ``_extract_dotted_name`` correctly handles nested attributes.

**Code example**:

.. code-block:: python

   from a.b.c.d.e import something

**Expected behavior**: Module name extracted as ``a.b.c.d.e``.

test_430_module_level_vs_function_level
-------------------------------------------------------------------------------

Test clear distinction between module-level and function-level imports.

**Code example**:

.. code-block:: python

   # Module level - should violate
   import json
   
   def foo():
       # Function level - should be allowed
       import pathlib
       pass

**Expected behavior**: Violation for ``json`` but not ``pathlib``.

test_440_function_exit_tracking
-------------------------------------------------------------------------------

Test that function depth is correctly decremented on function exit.

**Code example**:

.. code-block:: python

   def foo():
       import json  # OK - inside function
   
   # Module level after function
   import pathlib  # Should violate

**Expected behavior**: Violation for ``pathlib`` only.

test_450_class_level_imports
-------------------------------------------------------------------------------

Test imports at class level (not in method).

**Code example**:

.. code-block:: python

   class MyClass:
       import json  # This is actually module-level in Python

**Expected behavior**: Violation (class bodies are not function scopes).

test_460_lambda_local_imports
-------------------------------------------------------------------------------

Test imports inside lambda expressions (likely not possible in Python).

**Expected behavior**: Document behavior or N/A.

test_470_comprehension_imports
-------------------------------------------------------------------------------

Test if imports can appear in comprehensions (likely not valid Python).

**Expected behavior**: Document behavior or N/A.

Configuration Tests (500-599)
===============================================================================

test_500_config_hub_patterns
-------------------------------------------------------------------------------

Test that hub patterns can be configured via rule initialization.

**Test approach**:

* Pass custom ``hub_patterns`` tuple
* Verify only custom patterns are recognized

**Expected behavior**: Rule uses only provided patterns, not defaults.

test_510_config_empty_hub_patterns
-------------------------------------------------------------------------------

Test behavior when empty hub patterns tuple is provided.

**Expected behavior**: No modules recognized as hubs (all imports must be private).

test_520_config_pattern_ordering
-------------------------------------------------------------------------------

Test that pattern order doesn't affect hub detection.

**Expected behavior**: Consistent results regardless of pattern order.

Violation Reporting Tests (600-699)
===============================================================================

test_600_violation_message_simple
-------------------------------------------------------------------------------

Test violation message format for simple imports.

**Expected format**: ``"Direct import of '{module}'. Use import hub or private alias."``

test_610_violation_message_from
-------------------------------------------------------------------------------

Test violation message format for from imports.

**Expected format**: ``"Non-private import from '{module}': {names}. Use private names (starting with _)."``

test_620_violation_severity
-------------------------------------------------------------------------------

Test that violations are reported with 'warning' severity.

**Expected behavior**: All VBL201 violations have ``severity='warning'``.

test_630_violation_positioning
-------------------------------------------------------------------------------

Test that violation line and column numbers are accurate.

**Test approach**:

* Parse known code snippet with imports at specific lines
* Verify violation line numbers match import statement lines

**Expected behavior**: Accurate line/column reporting via LibCST metadata.

test_640_multiple_violations_single_file
-------------------------------------------------------------------------------

Test that multiple violations in one file are all reported.

**Code example**:

.. code-block:: python

   import json
   import pathlib
   from os import path
   from sys import argv

**Expected behavior**: Four violations reported.

Implementation Notes
===============================================================================

Testing Approach
-------------------------------------------------------------------------------

**Hybrid testing strategy**:

1. **In-memory snippets** for simple, focused tests

   * Create code strings directly in test functions
   * Parse with LibCST on the fly
   * Best for unit-level tests (000-299 ranges)

2. **File-based test data** for complex scenarios

   * Store snippets under ``tests/data/snippets/vbl201/``
   * Use pyfakefs to create realistic file structures
   * Best for integration tests (400+ ranges)

3. **Fixtures for common setup**

   * Helper to create MetadataWrapper from code string
   * Helper to run rule and extract violations
   * Fixture to provide test data directory

Dependencies and Fixtures Needed
-------------------------------------------------------------------------------

**Fixtures to create** (in ``tests/test_000_vibelinter/fixtures.py`` or inline):

.. code-block:: python

   def create_rule_wrapper(code: str, filename: str = 'test.py'):
       ''' Creates LibCST wrapper with metadata for testing rules. '''
       # Parse code and create MetadataWrapper
       # Return wrapper and source_lines tuple

   def run_vbl201(code: str, filename: str = 'test.py', 
                  hub_patterns=None):
       ''' Runs VBL201 rule on code snippet, returns violations. '''
       # Create wrapper
       # Instantiate VBL201
       # Visit module
       # Return violations

   @pytest.fixture
   def vbl201_test_data():
       ''' Provides pyfakefs with test snippets loaded. '''
       # Load tests/data/snippets/vbl201/ into fake filesystem

**Dependencies requiring injection**:

* None - VBL201 is self-contained with LibCST

**Filesystem operations needing pyfakefs**:

* Loading test snippet files from ``tests/data/snippets/vbl201/``
* Testing against realistic file paths for hub detection

Test Data Structure
-------------------------------------------------------------------------------

Proposed directory structure under ``tests/data/snippets/vbl201/``:

::

   tests/data/snippets/vbl201/
   ├── valid/
   │   ├── hub_modules/
   │   │   ├── __init__.py          # Hub with public imports
   │   │   ├── __main__.py          # Hub with public imports
   │   │   ├── __.py                # Hub with public imports
   │   │   └── imports.py           # For __/imports.py pattern
   │   ├── private_imports/
   │   │   ├── alias_private.py     # from foo import bar as _bar
   │   │   ├── name_private.py      # from . import __
   │   │   └── mixed_private.py     # All names private
   │   ├── future_imports/
   │   │   └── annotations.py       # from __future__ import annotations
   │   └── local_imports/
   │       ├── function_local.py    # Imports in function
   │       └── nested_function.py   # Imports in nested function
   └── invalid/
       ├── simple_imports/
       │   └── basic.py             # import json, pathlib
       ├── public_from_imports/
       │   └── basic.py             # from pathlib import Path
       ├── star_imports/
       │   └── basic.py             # from json import *
       └── mixed/
           └── partial_private.py   # Mix of private and public

Alternative: In-Memory Snippets
-------------------------------------------------------------------------------

For many tests, in-memory snippets may be more maintainable:

.. code-block:: python

   def test_300_simple_import_violation():
       ''' Simple import triggers violation in non-hub module. '''
       code = '''
   import json
   import pathlib
   '''
       violations = run_vbl201(code, filename='regular.py')
       assert len(violations) == 2
       assert 'json' in violations[0].message
       assert 'pathlib' in violations[1].message

This approach is recommended for most tests due to:

* Better readability (test and data in one place)
* Easier maintenance (no file I/O)
* Faster execution (no filesystem operations)

**Recommendation**: Use in-memory snippets for 90% of tests; use file-based
data only for complex integration scenarios testing hub pattern matching.

Private Functions/Methods Analysis
-------------------------------------------------------------------------------

**Private methods in VBL201**:

* ``_is_import_hub_module()`` - Testable via public API by observing behavior
* ``_is_future_import()`` - Testable via violations (future imports don't violate)
* ``_has_private_names()`` - Testable via violations (private names don't violate)
* ``_extract_dotted_name()`` - Testable via violation messages (dotted names appear)
* ``_report_simple_import_violation()`` - Testable via violation content
* ``_report_from_import_violation()`` - Testable via violation content
* ``_analyze_collections()`` - Called by ``leave_Module``, testable via violations

**Assessment**: All private methods are testable via the public API (violations
produced). No direct testing of private methods is needed.

Immutability Constraints
-------------------------------------------------------------------------------

No immutability constraint violations anticipated. VBL201 testing requires
only:

* Creating LibCST wrappers (standard operation)
* Instantiating VBL201 with different parameters (dependency injection)
* Parsing code snippets (no monkey-patching needed)

**Assessment**: 100% coverage achievable without violating immutability.

Third-Party Testing Patterns
-------------------------------------------------------------------------------

* **LibCST metadata**: Standard LibCST testing patterns (wrapper creation)
* **No external network calls**: All testing is local

Performance Considerations
-------------------------------------------------------------------------------

* Use in-memory code snippets (avoid file I/O)
* Parse code once per test (don't reparse same snippets)
* Consider parametrized tests for similar scenarios
* Target: All VBL201 tests complete in < 500ms

Test Module Numbering
-------------------------------------------------------------------------------

* **Test module**: ``test_420_rules_vbl201.py``

  * Placed in 400-499 range for rule implementations
  * Rules tested after configuration (200-299) and engine (300-399) to reflect architectural dependencies
  * Second rule in the suite (410 would be VBL101)
  * Follows subpackage numbering convention

Success Metrics
===============================================================================

Coverage Goals
-------------------------------------------------------------------------------

* **Line coverage**: 100%
* **Branch coverage**: 100%
* All public methods covered
* All violation paths exercised
* All edge cases tested

Test Count
-------------------------------------------------------------------------------

* Basic functionality: 5 tests
* Hub module detection: 6 tests
* Valid imports: 8 tests
* Invalid imports: 7 tests
* Edge cases: 8 tests
* Configuration: 3 tests
* Violation reporting: 5 tests

**Total**: ~42 tests

Validation Criteria
-------------------------------------------------------------------------------

Tests must validate:

* ✓ VBL201 instantiates correctly
* ✓ Hub modules are correctly identified
* ✓ All valid import patterns are allowed
* ✓ All invalid import patterns are flagged
* ✓ Violation messages are accurate and helpful
* ✓ Function-local imports are distinguished from module-level
* ✓ Custom hub patterns work correctly
* ✓ Edge cases are handled gracefully

