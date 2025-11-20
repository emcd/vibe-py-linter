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

- **Current coverage**: 16% (104 statements, 82 uncovered, 34 branches)
- **Target coverage**: 100%
- **Uncovered lines**: 37-39, 49-55, 94-97, 102-114, 121-134, 142-149, 165-175, 183-204, 213-233
- **Missing functionality tests**:

  - Configuration discovery from parent directories
  - Configuration file loading and parsing
  - TOML syntax error handling
  - Configuration validation and error reporting
  - Rule parameter parsing
  - String sequence parsing with validation
  - Optional integer parsing with validation
  - Edge cases for malformed configuration data

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
- Test 195: Raises ConfigurationInvalidity for invalid structure

TOML Parsing Tests (200-299)
-------------------------------------------------------------------------------

**Function: _parse_configuration (Tests 200-249)**

- Test 200: Parses empty configuration dictionary
- Test 205: Parses configuration with all optional fields absent
- Test 210: Parses select field as tuple
- Test 215: Parses exclude_rules field correctly (maps 'exclude' key)
- Test 220: Parses include_paths field correctly (maps 'include' key)
- Test 225: Parses exclude_paths field correctly
- Test 230: Parses context as integer
- Test 235: Parses rule_parameters dictionary
- Test 240: Handles missing rule_parameters section gracefully
- Test 245: Passes location through for error reporting

**Function: _parse_string_sequence (Tests 250-299)**

- Test 250: Returns absent for missing key
- Test 255: Parses single string as tuple with one element
- Test 260: Parses list of strings as tuple
- Test 265: Parses empty list as empty tuple
- Test 270: Raises ConfigurationInvalidity for non-string/non-list value
- Test 275: Raises ConfigurationInvalidity for list with non-string elements
- Test 280: Includes item index in error message for non-string list items
- Test 285: Handles unicode strings correctly
- Test 290: Preserves order of strings in list

**Function: _parse_optional_int (Tests 300-349)**

- Test 300: Returns absent for missing key
- Test 305: Parses zero as valid integer
- Test 310: Parses positive integer
- Test 315: Raises ConfigurationInvalidity for negative integer
- Test 320: Raises ConfigurationInvalidity for non-integer value (float)
- Test 325: Raises ConfigurationInvalidity for non-integer value (string)
- Test 330: Includes type name in error message
- Test 335: Includes actual value in error message for negative integers

**Function: _parse_rule_parameters (Tests 350-399)**

- Test 350: Returns empty Dictionary for missing 'rules' section
- Test 355: Parses single rule with parameters
- Test 360: Parses multiple rules with parameters
- Test 365: Returns immutable Dictionary instances
- Test 370: Raises ConfigurationInvalidity for non-dict 'rules' section
- Test 375: Raises ConfigurationInvalidity for non-string rule code
- Test 380: Raises ConfigurationInvalidity for non-dict rule parameters
- Test 385: Includes rule code in error messages
- Test 390: Handles empty parameters dictionary for rule
- Test 395: Preserves parameter types (int, float, string, list, dict)

**Function: _discover_pyproject_toml (Tests 400-449)**

- Test 400: Finds pyproject.toml in current directory
- Test 405: Finds pyproject.toml in parent directory
- Test 410: Finds pyproject.toml traversing multiple parent levels
- Test 415: Returns absent when reaching filesystem root
- Test 420: Returns absent when no pyproject.toml exists
- Test 425: Resolves start_directory to absolute path
- Test 430: Handles file path by checking parent directory
- Test 435: Uses cwd when start_directory is absent
- Test 440: Stops at root directory without infinite loop
- Test 445: Ignores directories named 'pyproject.toml'

Exception Handling Tests (450-499)
-------------------------------------------------------------------------------

**Exception: ConfigurationInvalidity (Tests 450-469)**

- Test 450: Instantiates with location and reason
- Test 455: Inherits from Omnierror and ValueError
- Test 460: Formats error message with location and reason
- Test 465: Stores location as string attribute
- Test 470: Stores reason as string attribute

**Exception: ConfigurationAbsence (Tests 470-489)**

- Test 470: Instantiates with absent location
- Test 475: Instantiates with specific location
- Test 480: Inherits from Omnierror and FileNotFoundError
- Test 485: Formats message for absent location
- Test 490: Formats message for specific location
- Test 495: Stores location as None for absent, string otherwise

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

Use module-scoped fixture for fake filesystem with test data::

    @pytest.fixture(scope='module')
    def config_test_fs():
        '''Provides fake filesystem with configuration test data.'''
        with Patcher() as patcher:
            patcher.fs.add_real_directory(
                'tests/data/configuration', lazy_read=True)
            yield patcher.fs

    def test_100_discover_in_current_directory(config_test_fs):
        '''Configuration discovery finds pyproject.toml in current directory.'''
        # Test implementation using pyfakefs

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
