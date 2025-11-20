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


''' Configuration reader tests. '''


import os

from pathlib import Path

import pytest

from pyfakefs.fake_filesystem_unittest import Patcher

from . import __


# =============================================================================
# Basic Functionality Tests (000-099)
# =============================================================================

def test_000_module_imports( ):
    ''' Configuration module imports successfully. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    assert module is not None


def test_010_configuration_instantiation( ):
    ''' Configuration dataclass instantiates with default values. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    config = module.Configuration( )
    assert absence.is_absent( config.select )
    assert absence.is_absent( config.exclude_rules )
    assert absence.is_absent( config.include_paths )
    assert absence.is_absent( config.exclude_paths )
    assert absence.is_absent( config.context )
    assert len( config.rule_parameters ) == 0


def test_020_pathlike_type_with_str( ):
    ''' PathLike type alias works with str. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    location: module.PathLike = '/path/to/file'
    assert isinstance( location, str )


def test_030_pathlike_type_with_path( ):
    ''' PathLike type alias works with Path. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    location: module.PathLike = Path( '/path/to/file' )
    assert isinstance( location, Path )


def test_040_configuration_invalidity_inheritance( ):
    ''' ConfigurationInvalidity inherits correctly from Omnierror. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    exc = module.ConfigurationInvalidity( '/test', 'test reason' )
    assert isinstance( exc, exceptions.Omnierror )
    assert isinstance( exc, ValueError )


def test_050_configuration_absence_inheritance( ):
    ''' ConfigurationAbsence inherits correctly from Omnierror. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    exc = module.ConfigurationAbsence( )
    assert isinstance( exc, exceptions.Omnierror )
    assert isinstance( exc, FileNotFoundError )


# =============================================================================
# Configuration Discovery Tests (100-199)
# =============================================================================

def test_100_discover_in_current_directory( ):
    ''' Configuration discovery finds pyproject.toml in current directory. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/project/pyproject.toml',
            contents = '[tool.vibelinter]\nselect = ["VBL101"]' )
        patcher.fs.create_dir( '/project/subdir' )
        result = module.discover_configuration( Path( '/project/subdir' ) )
        assert not absence.is_absent( result )
        assert result.select == ( 'VBL101', )


def test_110_discover_in_parent_directory( ):
    ''' Configuration discovery finds pyproject.toml in parent directory. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/project/pyproject.toml',
            contents = '[tool.vibelinter]\ncontext = 3' )
        patcher.fs.create_dir( '/project/src' )
        result = module.discover_configuration( Path( '/project/src' ) )
        assert not absence.is_absent( result )
        assert result.context == 3


def test_115_discover_multiple_levels_up( ):
    ''' Configuration discovery finds pyproject.toml multiple levels up. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/project/pyproject.toml',
            contents = '[tool.vibelinter]\ncontext = 5' )
        patcher.fs.create_dir( '/project/src/package/subpackage' )
        result = module.discover_configuration(
            Path( '/project/src/package/subpackage' ) )
        assert not absence.is_absent( result )
        assert result.context == 5


def test_120_returns_absent_when_not_found( ):
    ''' Configuration discovery returns absent when not found. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_dir( '/empty/project' )
        result = module.discover_configuration( Path( '/empty/project' ) )
        assert absence.is_absent( result )


def test_125_returns_absent_from_root( ):
    ''' Configuration discovery returns absent when starting from root. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_dir( '/no-config' )
        result = module.discover_configuration( Path( '/no-config' ) )
        assert absence.is_absent( result )


def test_130_discover_from_file_path( ):
    ''' Configuration discovery from file path checks parent directory. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/project/pyproject.toml',
            contents = '[tool.vibelinter]\ncontext = 2' )
        patcher.fs.create_file( '/project/src/main.py', contents = '' )
        result = module.discover_configuration(
            Path( '/project/src/main.py' ) )
        assert not absence.is_absent( result )
        assert result.context == 2


def test_135_handles_absent_start_directory( ):
    ''' Configuration discovery handles absent start_directory parameter. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/fake-cwd/pyproject.toml',
            contents = '[tool.vibelinter]\ncontext = 1' )
        os.chdir( '/fake-cwd' )
        result = module.discover_configuration( absence.absent )
        assert not absence.is_absent( result )
        assert result.context == 1


def test_140_stops_search_at_filesystem_root( ):
    ''' Configuration discovery stops search at filesystem root. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_dir( '/deep/nested/path' )
        result = module.discover_configuration(
            Path( '/deep/nested/path' ) )
        assert absence.is_absent( result )


def test_145_returns_loaded_configuration( ):
    ''' Configuration discovery returns loaded Configuration object. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/project/pyproject.toml',
            contents = '[tool.vibelinter]\nselect = ["VBL101", "VBL201"]' )
        result = module.discover_configuration( Path( '/project' ) )
        assert isinstance( result, module.Configuration )
        assert result.select == ( 'VBL101', 'VBL201' )


def test_150_loads_valid_minimal_configuration( ):
    ''' Configuration loading works with minimal valid configuration. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/valid', lazy_read = True )
        config = module.load_configuration(
            'tests/data/configuration/valid/minimal.toml' )
        assert isinstance( config, module.Configuration )


def test_155_loads_complete_configuration( ):
    ''' Configuration loading works with all fields populated. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/valid', lazy_read = True )
        config = module.load_configuration(
            'tests/data/configuration/valid/complete.toml' )
        assert config.select == ( 'VBL101', 'VBL201' )
        assert config.exclude_rules == ( 'VBL102', )
        assert config.include_paths == ( 'sources/**/*.py', )
        assert config.exclude_paths == ( 'tests/**', )
        assert config.context == 5
        assert 'VBL101' in config.rule_parameters


def test_160_loads_configuration_with_select_rules( ):
    ''' Configuration loading works with select rules. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/valid', lazy_read = True )
        config = module.load_configuration(
            'tests/data/configuration/valid/select-exclude.toml' )
        assert config.select == ( 'VBL1', 'VBL2' )


def test_165_loads_configuration_with_exclude_rules( ):
    ''' Configuration loading works with exclude rules. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/valid', lazy_read = True )
        config = module.load_configuration(
            'tests/data/configuration/valid/select-exclude.toml' )
        assert config.exclude_rules == ( 'VBL102', 'VBL201' )


def test_170_loads_configuration_with_path_filters( ):
    ''' Configuration loading works with path filters. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/valid', lazy_read = True )
        config = module.load_configuration(
            'tests/data/configuration/valid/paths-only.toml' )
        assert config.include_paths == ( 'sources/**', )
        assert config.exclude_paths == ( 'tests/**', 'build/**' )


def test_175_loads_configuration_with_context( ):
    ''' Configuration loading works with context setting. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/valid', lazy_read = True )
        config = module.load_configuration(
            'tests/data/configuration/valid/complete.toml' )
        assert config.context == 5


def test_180_loads_configuration_with_rule_parameters( ):
    ''' Configuration loading works with rule parameters. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/valid', lazy_read = True )
        config = module.load_configuration(
            'tests/data/configuration/valid/rules-only.toml' )
        assert 'VBL101' in config.rule_parameters
        assert 'VBL201' in config.rule_parameters


def test_185_raises_absence_for_missing_file( ):
    ''' Configuration loading raises ConfigurationAbsence for missing file. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.create_dir( '/empty' )
        with pytest.raises( module.ConfigurationAbsence ):
            module.load_configuration( '/empty/nonexistent.toml' )


def test_190_raises_invalidity_for_invalid_toml( ):
    ''' Configuration loading raises invalidity for invalid TOML. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/invalid', lazy_read = True )
        with pytest.raises(
            module.ConfigurationInvalidity,
            match = 'Invalid TOML syntax' ):
            module.load_configuration(
                'tests/data/configuration/invalid/invalid-toml-syntax.toml' )


def test_195_raises_invalidity_for_invalid_structure( ):
    ''' Configuration loading raises invalidity for invalid structure. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/invalid', lazy_read = True )
        with pytest.raises(
            module.ConfigurationInvalidity,
            match = 'Invalid TOML structure' ):
            module.load_configuration(
                'tests/data/configuration/invalid/invalid-structure.toml' )


# =============================================================================
# TOML Parsing Tests (200-399)
# =============================================================================

def test_200_parse_empty_configuration( ):
    ''' Configuration parsing works with empty dictionary. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    config = module._parse_configuration( { }, '/test' )
    assert isinstance( config, module.Configuration )


def test_205_parse_absent_optional_fields( ):
    ''' Configuration parsing works with all optional fields absent. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    config = module._parse_configuration( { }, '/test' )
    assert absence.is_absent( config.select )
    assert absence.is_absent( config.exclude_rules )


def test_210_parse_select_field( ):
    ''' Configuration parsing converts select field to tuple. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'select': [ 'VBL101', 'VBL201' ] }
    config = module._parse_configuration( data, '/test' )
    assert config.select == ( 'VBL101', 'VBL201' )


def test_215_parse_exclude_rules_field( ):
    ''' Configuration parsing maps exclude key to exclude_rules field. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'exclude': [ 'VBL102' ] }
    config = module._parse_configuration( data, '/test' )
    assert config.exclude_rules == ( 'VBL102', )


def test_220_parse_include_paths_field( ):
    ''' Configuration parsing maps include key to include_paths field. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'include': [ 'sources/**' ] }
    config = module._parse_configuration( data, '/test' )
    assert config.include_paths == ( 'sources/**', )


def test_225_parse_exclude_paths_field( ):
    ''' Configuration parsing processes exclude_paths field correctly. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'exclude_paths': [ 'tests/**', 'build/**' ] }
    config = module._parse_configuration( data, '/test' )
    assert config.exclude_paths == ( 'tests/**', 'build/**' )


def test_230_parse_context_as_integer( ):
    ''' Configuration parsing processes context as integer. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'context': 5 }
    config = module._parse_configuration( data, '/test' )
    assert config.context == 5


def test_235_parse_rule_parameters_dictionary( ):
    ''' Configuration parsing processes rule_parameters dictionary. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'rules': { 'VBL101': { 'max_depth': 3 } } }
    config = module._parse_configuration( data, '/test' )
    assert 'VBL101' in config.rule_parameters
    assert config.rule_parameters[ 'VBL101' ][ 'max_depth' ] == 3


def test_240_handles_missing_rule_parameters( ):
    ''' Configuration parsing handles missing rule_parameters gracefully. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'select': [ 'VBL101' ] }
    config = module._parse_configuration( data, '/test' )
    assert len( config.rule_parameters ) == 0


def test_245_passes_location_for_error_reporting( ):
    ''' Configuration parsing passes location for error reporting. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'context': -5 }
    with pytest.raises(
        module.ConfigurationInvalidity,
        match = '/test/path' ):
        module._parse_configuration( data, '/test/path' )


def test_250_string_sequence_returns_absent( ):
    ''' String sequence parsing returns absent for missing key. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    result = module._parse_string_sequence( { }, 'select', '/test' )
    assert absence.is_absent( result )


def test_255_string_sequence_single_string( ):
    ''' String sequence parsing converts single string to tuple. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'select': 'VBL101' }
    result = module._parse_string_sequence( data, 'select', '/test' )
    assert result == ( 'VBL101', )


def test_260_string_sequence_list_of_strings( ):
    ''' String sequence parsing converts list of strings to tuple. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'select': [ 'VBL101', 'VBL201' ] }
    result = module._parse_string_sequence( data, 'select', '/test' )
    assert result == ( 'VBL101', 'VBL201' )


def test_265_string_sequence_empty_list( ):
    ''' String sequence parsing converts empty list to empty tuple. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'select': [ ] }
    result = module._parse_string_sequence( data, 'select', '/test' )
    assert result == ( )


def test_270_string_sequence_invalid_type( ):
    ''' String sequence parsing raises for non-string/non-list value. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'select': 123 }
    with pytest.raises(
        module.ConfigurationInvalidity,
        match = 'must be a string or list of strings' ):
        module._parse_string_sequence( data, 'select', '/test' )


def test_275_string_sequence_list_with_non_strings( ):
    ''' String sequence parsing raises for list with non-string elements. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'select': [ 'VBL101', 123 ] }
    with pytest.raises(
        module.ConfigurationInvalidity,
        match = 'must be a string' ):
        module._parse_string_sequence( data, 'select', '/test' )


def test_280_string_sequence_includes_index_in_error( ):
    ''' String sequence parsing includes item index in error message. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'select': [ 'VBL101', 456 ] }
    with pytest.raises(
        module.ConfigurationInvalidity,
        match = r'\[1\]' ):
        module._parse_string_sequence( data, 'select', '/test' )


def test_285_string_sequence_handles_unicode( ):
    ''' String sequence parsing handles unicode strings correctly. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'select': [ 'VBL101-ñ', 'VBL201-日本語' ] }
    result = module._parse_string_sequence( data, 'select', '/test' )
    assert result == ( 'VBL101-ñ', 'VBL201-日本語' )


def test_290_string_sequence_preserves_order( ):
    ''' String sequence parsing preserves order of strings in list. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'select': [ 'Z', 'A', 'M' ] }
    result = module._parse_string_sequence( data, 'select', '/test' )
    assert result == ( 'Z', 'A', 'M' )


def test_300_optional_int_returns_absent( ):
    ''' Optional int parsing returns absent for missing key. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    result = module._parse_optional_int( { }, 'context', '/test' )
    assert absence.is_absent( result )


def test_305_optional_int_parses_zero( ):
    ''' Optional int parsing accepts zero as valid integer. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'context': 0 }
    result = module._parse_optional_int( data, 'context', '/test' )
    assert result == 0


def test_310_optional_int_parses_positive( ):
    ''' Optional int parsing accepts positive integer. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'context': 10 }
    result = module._parse_optional_int( data, 'context', '/test' )
    assert result == 10


def test_315_optional_int_rejects_negative( ):
    ''' Optional int parsing raises for negative integer. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'context': -5 }
    with pytest.raises(
        module.ConfigurationInvalidity,
        match = 'must be non-negative' ):
        module._parse_optional_int( data, 'context', '/test' )


def test_320_optional_int_rejects_float( ):
    ''' Optional int parsing raises for non-integer float value. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'context': 3.14 }
    with pytest.raises(
        module.ConfigurationInvalidity,
        match = 'must be an integer' ):
        module._parse_optional_int( data, 'context', '/test' )


def test_325_optional_int_rejects_string( ):
    ''' Optional int parsing raises for non-integer string value. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'context': 'five' }
    with pytest.raises(
        module.ConfigurationInvalidity,
        match = 'must be an integer' ):
        module._parse_optional_int( data, 'context', '/test' )


def test_330_optional_int_includes_typename_in_error( ):
    ''' Optional int parsing includes type name in error message. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'context': [ 1, 2, 3 ] }
    with pytest.raises(
        module.ConfigurationInvalidity,
        match = 'list' ):
        module._parse_optional_int( data, 'context', '/test' )


def test_335_optional_int_includes_value_in_error( ):
    ''' Optional int parsing includes actual value in error for negatives. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'context': -10 }
    with pytest.raises(
        module.ConfigurationInvalidity,
        match = '-10' ):
        module._parse_optional_int( data, 'context', '/test' )


def test_350_rule_parameters_returns_empty_for_missing( ):
    ''' Rule parameters parsing returns empty for missing section. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    result = module._parse_rule_parameters( { }, '/test' )
    assert len( result ) == 0


def test_355_rule_parameters_parses_single_rule( ):
    ''' Rule parameters parsing works with single rule. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'rules': { 'VBL101': { 'max_depth': 3 } } }
    result = module._parse_rule_parameters( data, '/test' )
    assert 'VBL101' in result
    assert result[ 'VBL101' ][ 'max_depth' ] == 3


def test_360_rule_parameters_parses_multiple_rules( ):
    ''' Rule parameters parsing works with multiple rules. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = {
        'rules': {
            'VBL101': { 'max_depth': 3 },
            'VBL201': { 'enforce': True },
        }
    }
    result = module._parse_rule_parameters( data, '/test' )
    assert 'VBL101' in result
    assert 'VBL201' in result


def test_365_rule_parameters_returns_immutable( ):
    ''' Rule parameters parsing returns immutable Dictionary instances. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'rules': { 'VBL101': { 'key': 'value' } } }
    result = module._parse_rule_parameters( data, '/test' )
    immut = __.cache_import_module( 'frigid' )
    assert isinstance( result, immut.Dictionary )


def test_370_rule_parameters_rejects_non_dict_section( ):
    ''' Rule parameters parsing raises for non-dict rules section. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'rules': 'not a dictionary' }
    with pytest.raises(
        module.ConfigurationInvalidity,
        match = 'must be a table' ):
        module._parse_rule_parameters( data, '/test' )


@pytest.mark.skip( reason = 'TOML always produces string keys' )
def test_375_rule_parameters_rejects_non_string_code( ):
    ''' Rule parameters parsing raises for non-string rule code. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/invalid', lazy_read = True )
        with pytest.raises(
            module.ConfigurationInvalidity,
            match = 'must be string' ):
            module.load_configuration(
                'tests/data/configuration/invalid/'
                'invalid-rule-code-not-string.toml' )


def test_380_rule_parameters_rejects_non_dict_params( ):
    ''' Rule parameters parsing raises for non-dict rule parameters. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/invalid', lazy_read = True )
        with pytest.raises(
            module.ConfigurationInvalidity,
            match = 'must be a table' ):
            module.load_configuration(
                'tests/data/configuration/invalid/'
                'invalid-rule-params-not-dict.toml' )


def test_385_rule_parameters_includes_code_in_error( ):
    ''' Rule parameters parsing includes rule code in error messages. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.add_real_directory(
            'tests/data/configuration/invalid', lazy_read = True )
        with pytest.raises(
            module.ConfigurationInvalidity,
            match = 'VBL101' ):
            module.load_configuration(
                'tests/data/configuration/invalid/'
                'invalid-rule-params-not-dict.toml' )


def test_390_rule_parameters_handles_empty_params( ):
    ''' Rule parameters parsing handles empty parameters dictionary. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = { 'rules': { 'VBL101': { } } }
    result = module._parse_rule_parameters( data, '/test' )
    assert 'VBL101' in result
    assert len( result[ 'VBL101' ] ) == 0


def test_395_rule_parameters_preserves_types( ):
    ''' Rule parameters parsing preserves parameter types. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    data = {
        'rules': {
            'VBL101': {
                'int_val': 42,
                'float_val': 3.14,
                'str_val': 'test',
                'list_val': [ 1, 2, 3 ],
                'dict_val': { 'nested': 'value' },
            }
        }
    }
    result = module._parse_rule_parameters( data, '/test' )
    params = result[ 'VBL101' ]
    assert params[ 'int_val' ] == 42
    assert params[ 'float_val' ] == 3.14
    assert params[ 'str_val' ] == 'test'
    assert params[ 'list_val' ] == [ 1, 2, 3 ]
    assert params[ 'dict_val' ][ 'nested' ] == 'value'


def test_400_discover_pyproject_in_current_dir( ):
    ''' Pyproject discovery finds pyproject.toml in current directory. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/project/pyproject.toml' )
        result = module._discover_pyproject_toml(
            Path( '/project' ) )
        assert result.name == 'pyproject.toml'
        assert result.parent.name == 'project'


def test_405_discover_pyproject_in_parent( ):
    ''' Pyproject discovery finds pyproject.toml in parent directory. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/project/pyproject.toml' )
        patcher.fs.create_dir( '/project/src' )
        result = module._discover_pyproject_toml(
            Path( '/project/src' ) )
        assert result.name == 'pyproject.toml'
        assert result.parent.name == 'project'


def test_410_discover_pyproject_multiple_levels( ):
    ''' Pyproject discovery traverses multiple parent levels. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/project/pyproject.toml' )
        patcher.fs.create_dir( '/project/src/package/deep' )
        result = module._discover_pyproject_toml(
            Path( '/project/src/package/deep' ) )
        assert result.name == 'pyproject.toml'
        assert result.parent.name == 'project'


def test_415_discover_pyproject_returns_absent_at_root( ):
    ''' Pyproject discovery returns absent when reaching filesystem root. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_dir( '/no-config' )
        result = module._discover_pyproject_toml(
            Path( '/no-config' ) )
        assert absence.is_absent( result )


def test_420_discover_pyproject_returns_absent_when_missing( ):
    ''' Pyproject discovery returns absent when no pyproject.toml exists. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_dir( '/empty/project' )
        result = module._discover_pyproject_toml(
            Path( '/empty/project' ) )
        assert absence.is_absent( result )


def test_425_discover_pyproject_resolves_to_absolute( ):
    ''' Pyproject discovery resolves start_directory to absolute path. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/project/pyproject.toml' )
        patcher.fs.create_dir( '/project/src' )
        os.chdir( '/project' )
        result = module._discover_pyproject_toml(
            Path( 'src' ) )
        assert result.name == 'pyproject.toml'
        assert result.parent.name == 'project'


def test_430_discover_pyproject_from_file_path( ):
    ''' Pyproject discovery handles file path by checking parent. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/project/pyproject.toml' )
        patcher.fs.create_file( '/project/src/main.py' )
        result = module._discover_pyproject_toml(
            Path( '/project/src/main.py' ) )
        assert result.name == 'pyproject.toml'
        assert result.parent.name == 'project'


def test_435_discover_pyproject_uses_cwd_when_absent( ):
    ''' Pyproject discovery uses cwd when start_directory is absent. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/working/pyproject.toml' )
        os.chdir( '/working' )
        result = module._discover_pyproject_toml( absence.absent )
        assert result.name == 'pyproject.toml'
        assert result.parent.name == 'working'


def test_440_discover_pyproject_stops_at_root( ):
    ''' Pyproject discovery stops at root without infinite loop. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_dir( '/test' )
        result = module._discover_pyproject_toml( Path( '/test' ) )
        assert absence.is_absent( result )


def test_445_discover_pyproject_ignores_directories( ):
    ''' Pyproject discovery ignores directories named pyproject.toml. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    with Patcher( ) as patcher:
        patcher.fs.create_dir( '/project/pyproject.toml' )
        result = module._discover_pyproject_toml(
            Path( '/project' ) )
        assert absence.is_absent( result )


# =============================================================================
# Exception Handling Tests (450-499)
# =============================================================================

def test_450_configuration_invalidity_instantiation( ):
    ''' ConfigurationInvalidity instantiates with location and reason. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    exc = module.ConfigurationInvalidity( '/test/path', 'test reason' )
    assert exc is not None


def test_455_configuration_invalidity_inheritance( ):
    ''' ConfigurationInvalidity inherits from Omnierror and ValueError. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    exc = module.ConfigurationInvalidity( '/test', 'reason' )
    assert isinstance( exc, exceptions.Omnierror )
    assert isinstance( exc, ValueError )


def test_460_configuration_invalidity_formats_message( ):
    ''' ConfigurationInvalidity formats message with location and reason. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    exc = module.ConfigurationInvalidity( '/test/config.toml', 'bad format' )
    assert '/test/config.toml' in str( exc )
    assert 'bad format' in str( exc )


def test_465_configuration_invalidity_stores_location( ):
    ''' ConfigurationInvalidity stores location as string attribute. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    exc = module.ConfigurationInvalidity( '/test/path', 'reason' )
    assert exc.location == '/test/path'


def test_470_configuration_invalidity_stores_reason( ):
    ''' ConfigurationInvalidity stores reason as string attribute. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    exc = module.ConfigurationInvalidity( '/test', 'test reason' )
    assert exc.reason == 'test reason'


def test_475_configuration_absence_instantiation_absent( ):
    ''' ConfigurationAbsence instantiates with absent location. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    exc = module.ConfigurationAbsence( absence.absent )
    assert exc is not None


def test_480_configuration_absence_instantiation_specific( ):
    ''' ConfigurationAbsence instantiates with specific location. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    exc = module.ConfigurationAbsence( '/specific/path' )
    assert exc is not None


def test_485_configuration_absence_inheritance( ):
    ''' ConfigurationAbsence inherits from Omnierror and FileNotFoundError. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    exc = module.ConfigurationAbsence( )
    assert isinstance( exc, exceptions.Omnierror )
    assert isinstance( exc, FileNotFoundError )


def test_490_configuration_absence_message_absent( ):
    ''' ConfigurationAbsence formats message for absent location. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    exc = module.ConfigurationAbsence( absence.absent )
    assert 'No pyproject.toml found' in str( exc )


def test_495_configuration_absence_message_specific( ):
    ''' ConfigurationAbsence formats message for specific location. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    exc = module.ConfigurationAbsence( '/test/config.toml' )
    assert '/test/config.toml' in str( exc )


def test_500_configuration_absence_stores_location_none( ):
    ''' ConfigurationAbsence stores location as None for absent. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    absence = __.cache_import_module( 'absence' )
    exc = module.ConfigurationAbsence( absence.absent )
    assert exc.location is None


def test_505_configuration_absence_stores_location_string( ):
    ''' ConfigurationAbsence stores location as string otherwise. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.configuration" )
    exc = module.ConfigurationAbsence( '/test/path' )
    assert exc.location == '/test/path'
