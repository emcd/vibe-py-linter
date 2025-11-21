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
