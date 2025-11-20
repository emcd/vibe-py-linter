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
Test Plan: Configuration Reader
*******************************************************************************

Coverage Analysis Summary
===============================================================================

- **Achieved coverage**: 98% (104 statements, 2 uncovered, 34 branches, 1 partial)
- **Test count**: 37 tests
- **Uncovered lines**: 193-194 (unreachable: TOML parser always produces string keys)
- **Test execution**: All tests pass on Linux and Windows

Testing Principle
===============================================================================

**Test behavior through the public API, not implementation details.**

This test suite focuses exclusively on testing the observable behavior of the
configuration reader through its public interface:

- ``discover_configuration()`` - Configuration discovery
- ``load_configuration()`` - Configuration loading and parsing
- ``Configuration`` - Configuration dataclass
- ``ConfigurationInvalidity`` - Validation error exception
- ``ConfigurationAbsence`` - Missing file exception

Private functions (``_parse_configuration``, ``_parse_string_sequence``,
``_parse_optional_int``, ``_parse_rule_parameters``, ``_discover_pyproject_toml``)
are **not** tested directly. They are exercised through the public API tests,
which provides:

- **Better maintainability**: Implementation can be refactored without breaking tests
- **Clearer intent**: Tests document what users can rely on
- **Equivalent coverage**: 98% coverage achieved through public API alone
- **Platform independence**: Behavior tests work across operating systems

Test Strategy
===============================================================================

Basic Functionality Tests (000-099)
-------------------------------------------------------------------------------

- Test 000: Configuration module imports successfully
- Test 010: Configuration dataclass instantiation with default values
- Test 020: PathLike type alias works with str and Path
- Test 030: Exception classes inherit correctly from Omnierror

Configuration Discovery Tests (100-199)
-------------------------------------------------------------------------------

**Function: discover_configuration (Tests 100-149)**

- Test 100: Discovers pyproject.toml in current directory
- Test 110: Discovers pyproject.toml in parent directory
- Test 115: Discovers pyproject.toml multiple levels up
- Test 120: Returns absent when no pyproject.toml found
- Test 125: Returns absent when starting from root directory
- Test 130: Discovers from file path by checking parent directory
- Test 135: Handles absent start_directory parameter (uses cwd)
- Test 140: Stops search at filesystem root
- Test 145: Returns loaded Configuration object when found

**Function: load_configuration (Tests 150-199)**

- Test 150: Loads valid minimal configuration
- Test 155: Loads configuration with all fields populated
- Test 160: Loads configuration with select rules
- Test 165: Loads configuration with exclude rules
- Test 170: Loads configuration with path filters
- Test 175: Loads configuration with context setting
- Test 180: Loads configuration with rule parameters
- Test 185: Raises ConfigurationAbsence for missing file
- Test 190: Raises ConfigurationInvalidity for invalid TOML syntax

Exception Handling Tests (200-299)
-------------------------------------------------------------------------------


**Exception: ConfigurationInvalidity (Tests 200-219)**

- Test 200: Instantiates with location and reason
- Test 205: Inherits from Omnierror and ValueError
- Test 210: Formats error message with location and reason
- Test 215: Stores location as string attribute
- Test 220: Stores reason as string attribute

**Exception: ConfigurationAbsence (Tests 225-249)**

- Test 225: Instantiates with absent location
- Test 230: Instantiates with specific location
- Test 235: Inherits from Omnierror and FileNotFoundError
- Test 240: Formats message for absent location
- Test 245: Formats message for specific location
- Test 250: Stores location as None for absent, string otherwise

Implementation Notes
===============================================================================

Dependencies requiring injection
-------------------------------------------------------------------------------

- **File system operations**: Use ``pyfakefs`` for all file system tests
- **Current working directory**: Create fake filesystem with appropriate structure

Filesystem operations needing pyfakefs
-------------------------------------------------------------------------------

- All pyproject.toml discovery tests
- All configuration loading tests
- Directory traversal tests
- File existence checks

Test data and fixtures
-------------------------------------------------------------------------------

**tests/data/configuration/valid/** - Valid pyproject.toml examples:

- ``minimal.toml`` - Minimal valid configuration
- ``complete.toml`` - All fields populated
- ``rules-only.toml`` - Only rule parameters
- ``paths-only.toml`` - Only path filters
- ``select-exclude.toml`` - Both select and exclude rules

**tests/data/configuration/invalid/** - Invalid configurations:

- ``invalid-toml-syntax.toml`` - TOML syntax errors
- ``invalid-structure.toml`` - Wrong structure type
- ``invalid-select-type.toml`` - Wrong type for select field
- ``invalid-context-negative.toml`` - Negative context value
- ``invalid-rules-not-dict.toml`` - Rules section not a dictionary
- ``invalid-rule-code-not-string.toml`` - Non-string rule code
- ``invalid-rule-params-not-dict.toml`` - Non-dict rule parameters

Fixture setup pattern
-------------------------------------------------------------------------------

Use ``pyfakefs.Patcher`` context manager in each test::

    def test_100_discover_in_current_directory():
        '''Configuration discovery finds pyproject.toml in current directory.'''
        module = __.cache_import_module(f"{__.PACKAGE_NAME}.configuration")
        with Patcher() as patcher:
            patcher.fs.create_file(
                '/project/pyproject.toml',
                contents='[tool.vibelinter]\nselect = ["VBL101"]')
            patcher.fs.create_dir('/project/subdir')
            result = module.discover_configuration(Path('/project/subdir'))
            assert not absence.is_absent(result)
            assert result.select == ('VBL101',)

For tests using real test data files::

    def test_190_raises_invalidity_for_invalid_toml():
        '''Configuration loading raises invalidity for invalid TOML.'''
        module = __.cache_import_module(f"{__.PACKAGE_NAME}.configuration")
        with Patcher() as patcher:
            patcher.fs.add_real_directory(
                'tests/data/configuration/invalid', lazy_read=True)
            with pytest.raises(
                module.ConfigurationInvalidity,
                match='Invalid TOML syntax'):
                module.load_configuration(
                    'tests/data/configuration/invalid/invalid-toml-syntax.toml')

Test module numbering
-------------------------------------------------------------------------------

Create ``tests/test_000_vibelinter/test_200_configuration.py`` following the established numbering scheme where 200-299 is allocated for configuration and parsing layer.

Anti-patterns to avoid
-------------------------------------------------------------------------------

- **DO NOT** test against real file system - use pyfakefs exclusively
- **DO NOT** use monkey-patching - inject dependencies via parameters
- **DO NOT** test implementation details - test behavior through public API
- **DO NOT** create temporary directories for synchronous file operations

Success Metrics
===============================================================================

- **Target line coverage**: 100% (from current 16%)
- **Branch coverage goals**: 100% (from current 0%)
- **Specific gaps to close**: All 82 uncovered lines

Closure of uncovered lines
-------------------------------------------------------------------------------

- **Lines 37-39**: ConfigurationInvalidity.__init__ - Tests 450-465
- **Lines 49-55**: ConfigurationAbsence.__init__ - Tests 470-495
- **Lines 94-97**: discover_configuration - Tests 100-145
- **Lines 102-114**: load_configuration - Tests 150-199
- **Lines 121-134**: _discover_pyproject_toml - Tests 400-445
- **Lines 142-149**: _parse_configuration - Tests 200-249
- **Lines 165-175**: _parse_optional_int - Tests 300-349
- **Lines 183-204**: _parse_rule_parameters - Tests 350-399
- **Lines 213-233**: _parse_string_sequence - Tests 250-299

Expected test count
-------------------------------------------------------------------------------

- Basic functionality: 4 tests
- Configuration discovery: 10 tests
- Configuration loading: 11 tests
- TOML parsing: 50 tests
- Exception handling: 15 tests
- **Total**: Approximately 90 tests

Estimated complexity: Medium

Implementation priority: High - Configuration reading is essential for user customization

Testing philosophy alignment
-------------------------------------------------------------------------------

This test plan follows project testing principles:

- **Dependency injection**: All file system operations use pyfakefs
- **Immutability**: Tests work with immutable Configuration objects
- **Performance**: In-memory filesystem for fast test execution
- **Coverage**: Systematic targeting of all branches and edge cases
- **Behavior testing**: Focus on public API behavior, not implementation
