# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Test VBL202 Import Spaghetti Detection rule. '''


from libcst import parse_module as _parse_module
from libcst.metadata import MetadataWrapper as _MetadataWrapper


def create_rule_wrapper( code: str, filename: str = 'test.py' ):
    ''' Creates LibCST wrapper with metadata for testing rules. '''
    # Parse code into CST module
    module = _parse_module( code )
    # Create metadata wrapper with required providers
    wrapper = _MetadataWrapper( module )
    # Split source into lines for context extraction
    source_lines = tuple( code.splitlines( ) )
    return wrapper, source_lines


def run_vbl202(
    code: str,
    filename: str = 'test.py',
    reexport_hub_patterns = None,
):
    ''' Runs VBL202 rule on code snippet and returns violations. '''
    from vibelinter.rules.implementations.vbl202 import VBL202
    wrapper, source_lines = create_rule_wrapper( code, filename )
    # Build rule kwargs
    kwargs = {
        'filename': filename,
        'wrapper': wrapper,
        'source_lines': source_lines,
    }
    if reexport_hub_patterns is not None:
        # Only pass reexport_hub_patterns if explicitly provided (not None)
        kwargs[ 'reexport_hub_patterns' ] = reexport_hub_patterns
    # Instantiate rule
    rule = VBL202( **kwargs )
    # Visit the module to collect data
    wrapper.visit( rule )
    # Return violations
    return rule.violations


#-----------------------------------------------------------------------------
# Basic Functionality Tests (000-099)
#-----------------------------------------------------------------------------


def test_000_rule_instantiation( ):
    ''' Rule instantiates successfully with required parameters. '''
    code = ''
    wrapper, source_lines = create_rule_wrapper( code )
    from vibelinter.rules.implementations.vbl202 import VBL202
    rule = VBL202(
        filename = 'test.py',
        wrapper = wrapper,
        source_lines = source_lines,
    )
    assert rule is not None
    assert rule.filename == 'test.py'


def test_010_rule_id( ):
    ''' Rule reports correct rule ID. '''
    code = ''
    wrapper, source_lines = create_rule_wrapper( code )
    from vibelinter.rules.implementations.vbl202 import VBL202
    rule = VBL202(
        filename = 'test.py',
        wrapper = wrapper,
        source_lines = source_lines,
    )
    assert rule.rule_id == 'VBL202'


def test_020_empty_module( ):
    ''' Empty module generates no violations. '''
    code = ''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 0


def test_030_reexport_hub_patterns_default( ):
    ''' Default re-export hub patterns are set correctly when not provided. '''
    code = ''
    wrapper, source_lines = create_rule_wrapper( code )
    from vibelinter.rules.implementations.vbl202 import VBL202
    rule = VBL202(
        filename = 'test.py',
        wrapper = wrapper,
        source_lines = source_lines,
    )
    # Verify default patterns are set
    assert '__.py' in rule._reexport_hub_patterns


def test_040_reexport_hub_patterns_custom( ):
    ''' Custom re-export hub patterns can be provided via configuration. '''
    code = ''
    wrapper, source_lines = create_rule_wrapper( code )
    from vibelinter.rules.implementations.vbl202 import VBL202
    custom_patterns = ( 'reexports.py', 'hub.py' )
    rule = VBL202(
        filename = 'test.py',
        wrapper = wrapper,
        source_lines = source_lines,
        reexport_hub_patterns = custom_patterns,
    )
    # Verify custom patterns are used
    assert rule._reexport_hub_patterns == custom_patterns
    assert '__.py' not in rule._reexport_hub_patterns


#-----------------------------------------------------------------------------
# Re-export Hub Detection Tests (100-199)
#-----------------------------------------------------------------------------


def test_100_reexport_hub_dunder_module( ):
    ''' __.py files are recognized as re-export hub modules. '''
    code = '''
from .. import foo
from .. import bar
'''
    violations = run_vbl202( code, filename = '__.py' )
    # Re-export hubs should allow 2-level imports
    assert len( violations ) == 0


def test_110_reexport_hub_pattern_matching( ):
    ''' Glob pattern matching correctly identifies re-export hub modules. '''
    code = '''
from .. import foo
'''
    # Test with path containing hub pattern
    violations = run_vbl202( code, filename = 'some/path/__.py' )
    assert len( violations ) == 0

    violations = run_vbl202( code, filename = 'deep/nested/path/__.py' )
    assert len( violations ) == 0


def test_120_non_reexport_hub_module( ):
    ''' Regular modules are NOT identified as re-export hub modules. '''
    code = '''
from .. import foo
'''
    violations = run_vbl202( code, filename = 'utils.py' )
    # Regular modules should violate on 2-level imports
    assert len( violations ) > 0


def test_130_custom_hub_pattern( ):
    ''' Custom re-export hub patterns work correctly. '''
    code = '''
from .. import foo
'''
    # With custom pattern that matches
    violations = run_vbl202(
        code,
        filename = 'reexports.py',
        reexport_hub_patterns = ( 'reexports.py', ),
    )
    assert len( violations ) == 0

    # With custom pattern that doesn't match
    violations = run_vbl202(
        code,
        filename = 'regular.py',
        reexport_hub_patterns = ( 'reexports.py', ),
    )
    assert len( violations ) == 1


#-----------------------------------------------------------------------------
# Valid Import Tests (200-299)
#-----------------------------------------------------------------------------


def test_200_absolute_imports( ):
    ''' Absolute imports are always allowed. '''
    code = '''
from foo import bar
from foo.bar.baz import qux
import something
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 0


def test_210_single_level_relative_import( ):
    ''' Single-level relative imports (from . import) are always allowed. '''
    code = '''
from . import foo
from . import bar
from .baz import qux
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 0


def test_220_two_level_in_reexport_hub( ):
    ''' Two-level relative imports are allowed in re-export hub modules. '''
    code = '''
from .. import foo
from .. import bar
from ..baz import qux
'''
    violations = run_vbl202( code, filename = '__.py' )
    assert len( violations ) == 0


def test_230_mixed_valid_imports( ):
    ''' Mix of valid import types in regular module. '''
    code = '''
from foo import bar
from . import local
from .submodule import helper
import standard_lib
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 0


def test_240_two_level_in_nested_reexport_hub( ):
    ''' Two-level imports in nested re-export hub paths. '''
    code = '''
from .. import foo
'''
    violations = run_vbl202( code, filename = 'deeply/nested/path/__.py' )
    assert len( violations ) == 0


#-----------------------------------------------------------------------------
# Invalid Import Tests (300-399)
#-----------------------------------------------------------------------------


def test_300_three_level_violation( ):
    ''' Three-level relative imports trigger violations everywhere. '''
    code = '''
from ... import foo
'''
    # In regular module
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1
    assert violations[ 0 ].severity == 'error'
    assert '3' in violations[ 0 ].message

    # Even in re-export hub
    violations = run_vbl202( code, filename = '__.py' )
    assert len( violations ) == 1
    assert violations[ 0 ].severity == 'error'


def test_310_four_level_violation( ):
    ''' Four-level relative imports trigger violations. '''
    code = '''
from .... import foo
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1
    assert violations[ 0 ].severity == 'error'
    assert '4' in violations[ 0 ].message


def test_320_five_level_violation( ):
    ''' Five-level relative imports trigger violations. '''
    code = '''
from ..... import foo
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1
    assert violations[ 0 ].severity == 'error'
    assert '5' in violations[ 0 ].message


def test_330_two_level_in_regular_module( ):
    ''' Two-level relative imports in regular modules trigger warnings. '''
    code = '''
from .. import foo
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1
    assert violations[ 0 ].severity == 'warning'
    assert 're-export hub' in violations[ 0 ].message.lower( )


def test_340_two_level_with_module_path( ):
    ''' Two-level imports with module path in regular module. '''
    code = '''
from ..parent import something
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1
    assert violations[ 0 ].severity == 'warning'


def test_350_multiple_violations( ):
    ''' Multiple excessive imports in one file. '''
    code = '''
from ... import foo
from .... import bar
from ..... import baz
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 3
    for violation in violations:
        assert violation.severity == 'error'


def test_360_mixed_violations( ):
    ''' Mix of two-level and excessive-level violations. '''
    code = '''
from .. import foo
from ... import bar
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 2
    # First should be warning (2-level), second should be error (3-level)
    severities = [ v.severity for v in violations ]
    assert 'warning' in severities
    assert 'error' in severities


#-----------------------------------------------------------------------------
# Edge Cases and Complex Scenarios (400-499)
#-----------------------------------------------------------------------------


def test_400_import_with_multiple_names( ):
    ''' Relative import with multiple names. '''
    code = '''
from ... import foo, bar, baz
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1


def test_410_star_import_excessive_depth( ):
    ''' Star imports with excessive depth. '''
    code = '''
from ... import *
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1
    assert violations[ 0 ].severity == 'error'


def test_420_valid_and_invalid_mix( ):
    ''' Mix of valid and invalid imports in same file. '''
    code = '''
from . import valid_one
from .. import valid_in_hub_only
from ... import invalid
from foo import absolute_valid
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 2  # Two-level warning + three-level error


def test_430_nested_path_reexport_hub( ):
    ''' Re-export hub in nested directory structure. '''
    code = '''
from .. import parent_module
'''
    violations = run_vbl202(
        code,
        filename = 'package/subpackage/nested/__.py',
    )
    assert len( violations ) == 0


def test_440_deeply_nested_excessive_import( ):
    ''' Deeply nested file with excessive relative import. '''
    code = '''
from ........ import something
'''
    violations = run_vbl202(
        code,
        filename = 'a/b/c/d/e/f/regular.py',
    )
    assert len( violations ) == 1
    assert '8' in violations[ 0 ].message


#-----------------------------------------------------------------------------
# Violation Reporting Tests (500-599)
#-----------------------------------------------------------------------------


def test_500_violation_message_excessive( ):
    ''' Violation message format for excessive depth. '''
    code = '''
from ... import foo
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1
    assert 'excessive' in violations[ 0 ].message.lower( )
    assert '...' in violations[ 0 ].message or '3' in violations[ 0 ].message


def test_510_violation_message_two_level( ):
    ''' Violation message format for two-level in regular module. '''
    code = '''
from .. import foo
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1
    assert 'two-level' in violations[ 0 ].message.lower( )
    assert '__.py' in violations[ 0 ].message


def test_520_violation_severity_excessive( ):
    ''' Excessive depth violations are errors. '''
    code = '''
from ... import foo
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1
    assert violations[ 0 ].severity == 'error'


def test_530_violation_severity_two_level( ):
    ''' Two-level violations are warnings. '''
    code = '''
from .. import foo
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1
    assert violations[ 0 ].severity == 'warning'


def test_540_violation_positioning( ):
    ''' Violation line numbers are accurate. '''
    code = '''
# Line 1
# Line 2
from ... import foo
from .... import bar
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 2
    # First violation should be on line 4
    assert violations[ 0 ].line == 4
    # Second violation should be on line 5
    assert violations[ 1 ].line == 5


def test_550_violation_includes_depth( ):
    ''' Violation message includes the depth information. '''
    code = '''
from ..... import foo
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 1
    # Should mention 5 levels
    assert '5' in violations[ 0 ].message


#-----------------------------------------------------------------------------
# Configuration Tests (600-699)
#-----------------------------------------------------------------------------


def test_600_config_empty_hub_patterns( ):
    ''' Empty hub patterns means no modules are re-export hubs. '''
    code = '''
from .. import foo
'''
    # Even __.py should violate with empty patterns
    violations = run_vbl202(
        code,
        filename = '__.py',
        reexport_hub_patterns = ( ),
    )
    assert len( violations ) == 1


def test_610_config_multiple_hub_patterns( ):
    ''' Multiple hub patterns work correctly. '''
    code = '''
from .. import foo
'''
    patterns = ( '__.py', 'reexports.py', 'hub.py' )

    # __.py should be recognized
    violations = run_vbl202(
        code, filename = '__.py', reexport_hub_patterns = patterns
    )
    assert len( violations ) == 0

    # reexports.py should be recognized
    violations = run_vbl202(
        code, filename = 'reexports.py', reexport_hub_patterns = patterns
    )
    assert len( violations ) == 0

    # hub.py should be recognized
    violations = run_vbl202(
        code, filename = 'hub.py', reexport_hub_patterns = patterns
    )
    assert len( violations ) == 0

    # regular.py should not be recognized
    violations = run_vbl202(
        code, filename = 'regular.py', reexport_hub_patterns = patterns
    )
    assert len( violations ) == 1


def test_620_config_pattern_ordering( ):
    ''' Pattern order does not affect hub detection. '''
    code = '''
from .. import foo
'''
    patterns1 = ( '__.py', 'hub.py' )
    patterns2 = ( 'hub.py', '__.py' )

    violations1 = run_vbl202(
        code, filename = '__.py', reexport_hub_patterns = patterns1
    )
    violations2 = run_vbl202(
        code, filename = '__.py', reexport_hub_patterns = patterns2
    )

    assert len( violations1 ) == len( violations2 ) == 0


#-----------------------------------------------------------------------------
# Integration Tests (700-799)
#-----------------------------------------------------------------------------


def test_700_realistic_package_structure( ):
    ''' Test with realistic package re-export hub usage. '''
    # Re-export hub in subpackage
    reexport_code = '''
from .. import core
from .. import utils
from ..parent import helpers
'''
    violations = run_vbl202( reexport_code, filename = 'package/sub/__.py' )
    assert len( violations ) == 0

    # Regular module in same location
    regular_code = '''
from . import local
from .. import parent
'''
    violations = run_vbl202( regular_code, filename = 'package/sub/module.py' )
    assert len( violations ) == 1  # Two-level warning


def test_710_mixed_import_styles( ):
    ''' Test with various import styles in one file. '''
    code = '''
# Absolute imports - OK
import os
from pathlib import Path

# Single-level relative - OK
from . import sibling
from .submodule import helper

# Two-level relative - violation in regular module
from .. import parent

# Excessive depth - always violation
from ... import grandparent
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 2


def test_720_no_imports( ):
    ''' File with no imports generates no violations. '''
    code = '''
def my_function():
    return 42

class MyClass:
    pass
'''
    violations = run_vbl202( code, filename = 'regular.py' )
    assert len( violations ) == 0
