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


''' Filtering and suppression tests. '''


import frigid as immut

from . import __


# =============================================================================
# Test Helpers
# =============================================================================

def create_engine_with_config( **kwargs ):
    ''' Creates an engine instance with specified configuration. '''
    engine_module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    registry_module = __.cache_import_module(
        f"{__.PACKAGE_NAME}.rules.registry" )
    config = engine_module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] ),
        **kwargs
    )
    # Empty registry is fine for these tests as we won't execute rules
    registry = registry_module.RuleRegistryManager( { } )
    return engine_module.Engine( registry, config )


def create_violation( rule_id, line, filename='test.py' ):
    ''' Creates a mock violation. '''
    violations_module = __.cache_import_module(
        f"{__.PACKAGE_NAME}.rules.violations" )
    return violations_module.Violation(
        rule_id = rule_id,
        filename = filename,
        line = line,
        column = 1,
        message = 'Test violation',
        severity = 'error'
    )


# =============================================================================
# Suppression Extraction Tests
# =============================================================================

def test_010_extract_suppressions_noqa_line( ):
    ''' Extracts generic noqa suppression. '''
    engine = create_engine_with_config( )
    source_lines = (
        'x = 1',
        'y = 2  # noqa',
        'z = 3'
    )
    suppressions = engine._extract_suppressions( source_lines )
    assert 2 in suppressions
    assert suppressions[ 2 ] is True


def test_015_extract_suppressions_noqa_specific( ):
    ''' Extracts specific rule suppression. '''
    engine = create_engine_with_config( )
    source_lines = (
        'x = 1  # noqa: VBL101',
        'y = 2  # noqa: VBL101,VBL102',
        'z = 3'
    )
    suppressions = engine._extract_suppressions( source_lines )
    assert 1 in suppressions
    assert suppressions[ 1 ] == { 'VBL101' }
    assert 2 in suppressions
    assert suppressions[ 2 ] == { 'VBL101', 'VBL102' }


def test_020_extract_suppressions_ignores_comments_without_noqa( ):
    ''' Ignores comments that are not noqa. '''
    engine = create_engine_with_config( )
    source_lines = (
        'x = 1  # regular comment',
        'y = 2'
    )
    suppressions = engine._extract_suppressions( source_lines )
    assert len( suppressions ) == 0


def test_025_extract_suppressions_handles_whitespace( ):
    ''' Handles whitespace in noqa comments. '''
    engine = create_engine_with_config( )
    source_lines = (
        'x = 1  #   noqa:   VBL101  ,  VBL102   ',
    )
    suppressions = engine._extract_suppressions( source_lines )
    assert 1 in suppressions
    assert suppressions[ 1 ] == { 'VBL101', 'VBL102' }


# =============================================================================
# Violation Filtering Tests
# =============================================================================

def test_050_filter_violations_inline_generic( ):
    ''' Filters violations with generic noqa. '''
    engine = create_engine_with_config( )
    violations = [
        create_violation( 'VBL101', 1 ),
        create_violation( 'VBL102', 2 ),
    ]
    suppressions = {
        1: True,  # All rules suppressed on line 1
    }
    filtered = engine._filter_violations(
        violations, suppressions, 'test.py' )
    assert len( filtered ) == 1
    assert filtered[ 0 ].rule_id == 'VBL102'


def test_055_filter_violations_inline_specific( ):
    ''' Filters violations with specific rule suppression. '''
    engine = create_engine_with_config( )
    violations = [
        create_violation( 'VBL101', 1 ),
        create_violation( 'VBL102', 1 ),
    ]
    suppressions = {
        1: { 'VBL101' },
    }
    filtered = engine._filter_violations(
        violations, suppressions, 'test.py' )
    assert len( filtered ) == 1
    assert filtered[ 0 ].rule_id == 'VBL102'


def test_060_filter_violations_per_file_ignores( ):
    ''' Filters violations based on per-file ignores. '''
    ignores = immut.Dictionary( {
        'test.py': ( 'VBL101', ),
        '**/*.py': ( 'VBL201', ),
    } )
    engine = create_engine_with_config( per_file_ignores = ignores )
    violations = [
        create_violation( 'VBL101', 1, 'test.py' ),
        create_violation( 'VBL102', 1, 'test.py' ),
        create_violation( 'VBL201', 1, 'test.py' ),
    ]
    # Empty suppressions
    filtered = engine._filter_violations(
        violations, { }, 'test.py' )
    assert len( filtered ) == 1
    assert filtered[ 0 ].rule_id == 'VBL102'


def test_065_filter_violations_per_file_ignores_glob( ):
    ''' Filters violations using glob patterns. '''
    ignores = immut.Dictionary( {
        'tests/**/*.py': ( 'VBL101', ),
    } )
    engine = create_engine_with_config( per_file_ignores = ignores )
    violations = [
        create_violation( 'VBL101', 1, 'tests/unit/test_foo.py' ),
        create_violation( 'VBL102', 1, 'tests/unit/test_foo.py' ),
    ]
    filtered = engine._filter_violations(
        violations, { }, 'tests/unit/test_foo.py' )
    assert len( filtered ) == 1
    assert filtered[ 0 ].rule_id == 'VBL102'


def test_067_filter_violations_per_file_ignores_descriptive_names( ):
    ''' Filters violations using descriptive rule names. '''
    engine_module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    registry_module = __.cache_import_module(
        f"{__.PACKAGE_NAME}.rules.registry" )
    mock_descriptor = registry_module.RuleDescriptor(
        vbl_code = 'VBL101',
        descriptive_name = 'blank-line-elimination',
        description = 'Test rule',
        category = 'test',
        subcategory = 'test',
        rule_class = object,
    )
    registry = registry_module.RuleRegistryManager( {
        'VBL101': mock_descriptor,
    } )
    ignores = immut.Dictionary( {
        'test.py': ( 'blank-line-elimination', ),
    } )
    config = engine_module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] ),
        per_file_ignores = ignores,
    )
    engine = engine_module.Engine( registry, config )
    violations = [
        create_violation( 'VBL101', 1, 'test.py' ),
        create_violation( 'VBL102', 1, 'test.py' ),
    ]
    filtered = engine._filter_violations(
        violations, { }, 'test.py' )
    assert len( filtered ) == 1
    assert filtered[ 0 ].rule_id == 'VBL102'


def test_070_filter_violations_combined( ):
    ''' Filters violations using both inline and per-file methods. '''
    ignores = immut.Dictionary( {
        'test.py': ( 'VBL101', ),
    } )
    engine = create_engine_with_config( per_file_ignores = ignores )
    violations = [
        create_violation( 'VBL101', 1 ),  # Ignored by file config
        create_violation( 'VBL102', 2 ),  # Suppressed inline
        create_violation( 'VBL103', 3 ),  # Kept
    ]
    suppressions = {
        2: True,
    }
    filtered = engine._filter_violations(
        violations, suppressions, 'test.py' )
    assert len( filtered ) == 1
    assert filtered[ 0 ].rule_id == 'VBL103'
