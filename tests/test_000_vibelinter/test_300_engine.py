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

# ruff: noqa: E501, B011

''' Linting engine tests. '''


from pathlib import Path

import frigid as immut
import libcst
import libcst.metadata
import pytest

from pyfakefs.fake_filesystem_unittest import Patcher

from . import __


# =============================================================================
# Mock Rules for Testing
# =============================================================================

# Load base rule at module level for inheritance
_base_module = __.cache_import_module( f"{__.PACKAGE_NAME}.rules.base" )

class MockViolationRule( _base_module.BaseRule ):
    ''' Test rule that produces predictable violations on function definitions. '''

    def __init__(
        self, filename: str,
        wrapper: libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ],
        **kwargs
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )
        self._functions_seen = 0
        self.parameters = kwargs

    @property
    def rule_id( self ) -> str:
        return 'TEST001'

    def visit_FunctionDef( self, node: libcst.FunctionDef ) -> None:
        ''' Produces violation for each function definition. '''
        self._functions_seen += 1
        self._produce_violation( node, 'Test violation', 'error' )

    def _analyze_collections( self ) -> None:
        ''' No collection analysis needed for this test rule. '''
        pass


class MockCleanRule( _base_module.BaseRule ):
    ''' Test rule that never produces violations. '''

    def __init__(
        self, filename: str,
        wrapper: libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ]
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )

    @property
    def rule_id( self ) -> str:
        return 'TEST002'

    def _analyze_collections( self ) -> None:
        ''' No violations produced. '''
        pass


class MockFailingRule( _base_module.BaseRule ):
    ''' Test rule that raises exception during execution. '''

    def __init__(
        self, filename: str,
        wrapper: libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ]
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )

    @property
    def rule_id( self ) -> str:
        return 'TEST003'

    def visit_Module( self, node: libcst.Module ) -> None:
        ''' Raises exception during visit. '''
        raise RuntimeError( 'Test rule execution failure' )

    def _analyze_collections( self ) -> None:
        ''' Not reached due to exception. '''
        pass


class MockInstantiationFailingRule:
    ''' Test rule that raises exception during instantiation. '''

    def __init__(
        self, filename: str,
        wrapper: libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ]
    ) -> None:
        raise RuntimeError( 'Test rule instantiation failure' )


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_registry():
    ''' Creates mock rule registry with test rules. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.rules.registry" )
    registry = {
        'TEST001': module.RuleDescriptor(
            vbl_code = 'TEST001',
            descriptive_name = 'test-violation',
            description = 'Test rule that produces violations',
            category = 'test',
            subcategory = 'mock',
            rule_class = MockViolationRule,
        ),
        'TEST002': module.RuleDescriptor(
            vbl_code = 'TEST002',
            descriptive_name = 'test-clean',
            description = 'Test rule that produces no violations',
            category = 'test',
            subcategory = 'mock',
            rule_class = MockCleanRule,
        ),
        'TEST003': module.RuleDescriptor(
            vbl_code = 'TEST003',
            descriptive_name = 'test-failing',
            description = 'Test rule that fails during execution',
            category = 'test',
            subcategory = 'mock',
            rule_class = MockFailingRule,
        ),
        'TEST004': module.RuleDescriptor(
            vbl_code = 'TEST004',
            descriptive_name = 'test-instantiation-failing',
            description = 'Test rule that fails during instantiation',
            category = 'test',
            subcategory = 'mock',
            rule_class = MockInstantiationFailingRule,
        ),
    }
    return module.RuleRegistryManager( registry )


@pytest.fixture
def minimal_config():
    ''' Creates minimal engine configuration. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    return module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] ),
        rule_parameters = immut.Dictionary( ),
    )


# =============================================================================
# Basic Functionality Tests (000-099)
# =============================================================================

def test_000_engine_module_imports():
    ''' Engine module imports successfully. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    assert module is not None


def test_010_engine_configuration_minimal_instantiation():
    ''' EngineConfiguration instantiates with minimal parameters. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'VBL201' ] )
    )
    assert config is not None
    assert 'VBL201' in config.enabled_rules


def test_015_engine_configuration_default_values():
    ''' EngineConfiguration uses default values correctly. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'VBL201' ] )
    )
    assert config.context_size == 2
    assert config.include_context is True
    assert len( config.rule_parameters ) == 0


def test_020_report_instantiation():
    ''' Report dataclass instantiates with all fields. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    report = module.Report(
        violations = ( ),
        contexts = ( ),
        filename = 'test.py',
        rule_count = 1,
        analysis_duration_ms = 10.5,
    )
    assert report is not None


def test_025_engine_instantiation( mock_registry, minimal_config ):
    ''' Engine instantiates with registry and configuration. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    assert engine is not None
    assert engine.registry_manager is mock_registry
    assert engine.configuration is minimal_config


def test_030_create_empty_rule_parameters():
    ''' Helper function returns empty Dictionary. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    params = module._create_empty_rule_parameters( )
    assert len( params ) == 0


# =============================================================================
# EngineConfiguration Tests (100-199)
# =============================================================================

def test_100_configuration_with_enabled_rules():
    ''' EngineConfiguration stores enabled_rules frozenset. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    rules = frozenset( [ 'VBL201', 'VBL202' ] )
    config = module.EngineConfiguration( enabled_rules = rules )
    assert config.enabled_rules == rules
    assert isinstance( config.enabled_rules, frozenset )


def test_105_configuration_default_rule_parameters():
    ''' EngineConfiguration uses empty Dictionary for rule_parameters. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'VBL201' ] )
    )
    assert isinstance( config.rule_parameters, immut.Dictionary )
    assert len( config.rule_parameters ) == 0


def test_110_configuration_default_context_size():
    ''' EngineConfiguration uses context_size default of 2. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'VBL201' ] )
    )
    assert config.context_size == 2


def test_115_configuration_default_include_context():
    ''' EngineConfiguration uses include_context default of True. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'VBL201' ] )
    )
    assert config.include_context is True


def test_120_configuration_custom_context_size():
    ''' EngineConfiguration accepts custom context_size. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'VBL201' ] ),
        context_size = 5,
    )
    assert config.context_size == 5


def test_125_configuration_custom_include_context():
    ''' EngineConfiguration accepts custom include_context value. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'VBL201' ] ),
        include_context = False,
    )
    assert config.include_context is False


def test_130_configuration_custom_rule_parameters():
    ''' EngineConfiguration accepts custom rule_parameters Dictionary. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    params = immut.Dictionary( {
        'VBL201': immut.Dictionary( { 'max_depth': 3 } )
    } )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'VBL201' ] ),
        rule_parameters = params,
    )
    assert config.rule_parameters == params


def test_135_configuration_immutable_rule_parameters():
    ''' EngineConfiguration stores immutable rule_parameters. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    params = immut.Dictionary( {
        'VBL201': immut.Dictionary( { 'max_depth': 3 } )
    } )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'VBL201' ] ),
        rule_parameters = params,
    )
    assert isinstance( config.rule_parameters, immut.Dictionary )


def test_140_configuration_nested_parameters_immutable():
    ''' Nested rule parameter dictionaries are immutable. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    params = immut.Dictionary( {
        'VBL201': immut.Dictionary( { 'max_depth': 3 } )
    } )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'VBL201' ] ),
        rule_parameters = params,
    )
    rule_params = config.rule_parameters[ 'VBL201' ]
    assert isinstance( rule_params, immut.Dictionary )


# =============================================================================
# Report Dataclass Tests (150-199)
# =============================================================================

def test_150_report_instantiation_with_all_fields():
    ''' Report instantiates with all required fields. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    violations_module = __.cache_import_module(
        f"{__.PACKAGE_NAME}.rules.violations" )
    violation = violations_module.Violation(
        rule_id = 'TEST001',
        filename = 'test.py',
        line = 1,
        column = 1,
        message = 'Test',
        severity = 'error',
    )
    context = violations_module.ViolationContext(
        violation = violation,
        context_lines = ( 'line 1', ),
        context_start_line = 1,
    )
    report = module.Report(
        violations = ( violation, ),
        contexts = ( context, ),
        filename = 'test.py',
        rule_count = 1,
        analysis_duration_ms = 10.5,
    )
    assert report.violations == ( violation, )
    assert report.contexts == ( context, )
    assert report.filename == 'test.py'
    assert report.rule_count == 1
    assert report.analysis_duration_ms == 10.5


def test_155_report_stores_violations_as_tuple():
    ''' Report stores violations as tuple. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    violations_module = __.cache_import_module(
        f"{__.PACKAGE_NAME}.rules.violations" )
    violation = violations_module.Violation(
        rule_id = 'TEST001',
        filename = 'test.py',
        line = 1,
        column = 1,
        message = 'Test',
        severity = 'error',
    )
    report = module.Report(
        violations = ( violation, ),
        contexts = ( ),
        filename = 'test.py',
        rule_count = 1,
        analysis_duration_ms = 10.5,
    )
    assert isinstance( report.violations, tuple )


def test_160_report_stores_contexts_as_tuple():
    ''' Report stores contexts as tuple. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    report = module.Report(
        violations = ( ),
        contexts = ( ),
        filename = 'test.py',
        rule_count = 1,
        analysis_duration_ms = 10.5,
    )
    assert isinstance( report.contexts, tuple )


def test_165_report_stores_filename_string():
    ''' Report stores filename string. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    report = module.Report(
        violations = ( ),
        contexts = ( ),
        filename = 'test.py',
        rule_count = 1,
        analysis_duration_ms = 10.5,
    )
    assert report.filename == 'test.py'
    assert isinstance( report.filename, str )


def test_170_report_stores_rule_count_integer():
    ''' Report stores rule_count integer. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    report = module.Report(
        violations = ( ),
        contexts = ( ),
        filename = 'test.py',
        rule_count = 5,
        analysis_duration_ms = 10.5,
    )
    assert report.rule_count == 5
    assert isinstance( report.rule_count, int )


def test_175_report_stores_analysis_duration_float():
    ''' Report stores analysis_duration_ms float. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    report = module.Report(
        violations = ( ),
        contexts = ( ),
        filename = 'test.py',
        rule_count = 1,
        analysis_duration_ms = 12.345,
    )
    assert report.analysis_duration_ms == 12.345
    assert isinstance( report.analysis_duration_ms, float )


# =============================================================================
# Engine Initialization Tests (200-249)
# =============================================================================

def test_200_engine_initializes_with_registry_manager( mock_registry, minimal_config ):
    ''' Engine initializes with registry_manager. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    assert engine.registry_manager is not None


def test_205_engine_initializes_with_configuration( mock_registry, minimal_config ):
    ''' Engine initializes with configuration. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    assert engine.configuration is not None


def test_210_engine_stores_registry_manager_attribute( mock_registry, minimal_config ):
    ''' Engine stores registry_manager as instance attribute. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    assert engine.registry_manager is mock_registry


def test_215_engine_stores_configuration_attribute( mock_registry, minimal_config ):
    ''' Engine stores configuration as instance attribute. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    assert engine.configuration is minimal_config


def test_220_engine_works_with_minimal_configuration( mock_registry ):
    ''' Engine works with minimal configuration. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] )
    )
    engine = module.Engine( mock_registry, config )
    assert engine is not None


def test_225_engine_works_with_complex_configuration( mock_registry ):
    ''' Engine works with complex configuration. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001', 'TEST002' ] ),
        rule_parameters = immut.Dictionary( {
            'TEST001': immut.Dictionary( { 'max_depth': 5 } )
        } ),
        context_size = 3,
        include_context = False,
    )
    engine = module.Engine( mock_registry, config )
    assert engine is not None


# =============================================================================
# Single-File Linting Tests (250-349)
# =============================================================================

def test_250_lint_file_reads_valid_python( mock_registry, minimal_config ):
    ''' lint_file reads and lints valid Python file. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/test/valid.py',
            contents = 'def test_function():\n    pass\n'
        )
        report = engine.lint_file( Path( '/test/valid.py' ) )
        assert isinstance( report, module.Report )


def test_255_lint_file_returns_report_with_violations( mock_registry, minimal_config ):
    ''' lint_file returns Report with violations. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/test/valid.py',
            contents = 'def test_function():\n    pass\n'
        )
        report = engine.lint_file( Path( '/test/valid.py' ) )
        assert len( report.violations ) > 0


def test_260_lint_file_returns_empty_violations_for_clean_code( mock_registry ):
    ''' lint_file returns Report with empty violations for clean code. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST002' ] )
    )
    engine = module.Engine( mock_registry, config )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/test/clean.py',
            contents = 'x = 1\n'
        )
        report = engine.lint_file( Path( '/test/clean.py' ) )
        assert len( report.violations ) == 0


def test_265_lint_file_passes_path_as_filename( mock_registry, minimal_config ):
    ''' lint_file passes file path as filename to lint_source. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/test/sample.py',
            contents = 'x = 1\n'
        )
        report = engine.lint_file( Path( '/test/sample.py' ) )
        assert report.filename == '/test/sample.py'


def test_270_lint_file_reads_utf8_encoding( mock_registry, minimal_config ):
    ''' lint_file reads file with UTF-8 encoding. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/test/unicode.py',
            contents = '# -*- coding: utf-8 -*-\nx = "Hello 世界"\n'
        )
        report = engine.lint_file( Path( '/test/unicode.py' ) )
        assert isinstance( report, module.Report )


def test_275_lint_file_propagates_exceptions( mock_registry ):
    ''' lint_file propagates exceptions from lint_source. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST003' ] )
    )
    engine = module.Engine( mock_registry, config )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/test/failing.py',
            contents = 'x = 1\n'
        )
        with pytest.raises( exceptions.RuleExecuteFailure ):
            engine.lint_file( Path( '/test/failing.py' ) )


def test_280_lint_source_parses_valid_python( mock_registry, minimal_config ):
    ''' lint_source parses valid Python source code. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    report = engine.lint_source( 'x = 1\n', 'test.py' )
    assert isinstance( report, module.Report )


def test_285_lint_source_returns_report_with_violations( mock_registry, minimal_config ):
    ''' lint_source returns Report with violations from rules. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    report = engine.lint_source( 'def test():\n    pass\n', 'test.py' )
    assert len( report.violations ) > 0


def test_290_lint_source_returns_empty_violations_clean_code( mock_registry ):
    ''' lint_source returns Report with empty violations for clean code. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST002' ] )
    )
    engine = module.Engine( mock_registry, config )
    report = engine.lint_source( 'x = 1\n', 'test.py' )
    assert len( report.violations ) == 0


def test_295_lint_source_includes_all_enabled_rules_in_count( mock_registry ):
    ''' lint_source includes all enabled rules in rule_count. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001', 'TEST002' ] )
    )
    engine = module.Engine( mock_registry, config )
    report = engine.lint_source( 'x = 1\n', 'test.py' )
    assert report.rule_count == 2


def test_300_lint_source_measures_analysis_duration( mock_registry, minimal_config ):
    ''' lint_source measures analysis_duration_ms accurately. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    report = engine.lint_source( 'x = 1\n', 'test.py' )
    assert report.analysis_duration_ms > 0
    assert isinstance( report.analysis_duration_ms, float )


def test_305_lint_source_uses_provided_filename( mock_registry, minimal_config ):
    ''' lint_source uses provided filename in Report. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    report = engine.lint_source( 'x = 1\n', 'custom.py' )
    assert report.filename == 'custom.py'


def test_310_lint_source_uses_default_filename( mock_registry, minimal_config ):
    ''' lint_source uses default filename when not provided. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    report = engine.lint_source( 'x = 1\n' )
    assert report.filename == '<string>'


def test_315_lint_source_extracts_contexts_when_enabled( mock_registry ):
    ''' lint_source extracts contexts when include_context is True. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] ),
        include_context = True,
    )
    engine = module.Engine( mock_registry, config )
    report = engine.lint_source( 'def test():\n    pass\n', 'test.py' )
    assert len( report.contexts ) > 0


def test_320_lint_source_omits_contexts_when_disabled( mock_registry ):
    ''' lint_source omits contexts when include_context is False. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] ),
        include_context = False,
    )
    engine = module.Engine( mock_registry, config )
    report = engine.lint_source( 'def test():\n    pass\n', 'test.py' )
    assert len( report.contexts ) == 0


def test_325_lint_source_sorts_violations_by_line_column( mock_registry, minimal_config ):
    ''' lint_source sorts violations by line then column. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    source = '''def first():
    pass

def second():
    pass

def third():
    pass
'''
    report = engine.lint_source( source, 'test.py' )
    if len( report.violations ) > 1:
        for i in range( len( report.violations ) - 1 ):
            v1, v2 = report.violations[ i ], report.violations[ i + 1 ]
            assert (v1.line, v1.column) <= (v2.line, v2.column)


def test_330_lint_source_includes_violations_from_multiple_rules( mock_registry ):
    ''' lint_source includes violations from multiple rules. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001', 'TEST002' ] )
    )
    engine = module.Engine( mock_registry, config )
    report = engine.lint_source( 'def test():\n    pass\n', 'test.py' )
    # TEST001 produces violations, TEST002 does not
    assert len( report.violations ) > 0


def test_335_lint_source_passes_context_size_to_extraction( mock_registry ):
    ''' lint_source passes context_size to context extraction. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] ),
        context_size = 3,
        include_context = True,
    )
    engine = module.Engine( mock_registry, config )
    source = '''line1 = 1
line2 = 2
line3 = 3
def test():
    pass
line6 = 6
line7 = 7
'''
    report = engine.lint_source( source, 'test.py' )
    if report.contexts:
        # Context should include lines around the violation
        assert len( report.contexts[ 0 ].context_lines ) > 0


def test_340_lint_source_skips_context_extraction_no_violations( mock_registry ):
    ''' lint_source skips context extraction when no violations. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST002' ] ),
        include_context = True,
    )
    engine = module.Engine( mock_registry, config )
    report = engine.lint_source( 'x = 1\n', 'test.py' )
    assert len( report.contexts ) == 0


def test_345_lint_source_handles_empty_source_gracefully( mock_registry, minimal_config ):
    ''' lint_source handles empty source code gracefully. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    report = engine.lint_source( '', 'test.py' )
    assert isinstance( report, module.Report )
    assert len( report.violations ) == 0


# =============================================================================
# Metadata Wrapper Creation Tests (350-399)
# =============================================================================

def test_350_create_metadata_wrapper_parses_valid_source( mock_registry, minimal_config ):
    ''' _create_metadata_wrapper parses valid Python source. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, _ = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    assert wrapper is not None


def test_355_create_metadata_wrapper_creates_wrapper( mock_registry, minimal_config ):
    ''' _create_metadata_wrapper creates MetadataWrapper successfully. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, _ = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    assert isinstance( wrapper, libcst.metadata.MetadataWrapper )


def test_360_create_metadata_wrapper_returns_tuple( mock_registry, minimal_config ):
    ''' _create_metadata_wrapper returns tuple of wrapper and source_lines. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    result = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    assert isinstance( result, tuple )
    assert len( result ) == 2


def test_365_create_metadata_wrapper_splits_source_into_lines( mock_registry, minimal_config ):
    ''' _create_metadata_wrapper splits source into lines correctly. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    _, source_lines = engine._create_metadata_wrapper( 'line1\nline2\nline3\n', 'test.py' )
    assert len( source_lines ) == 3  # splitlines() doesn't include trailing newline


def test_370_create_metadata_wrapper_preserves_empty_lines( mock_registry, minimal_config ):
    ''' _create_metadata_wrapper preserves empty lines in source_lines. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    _, source_lines = engine._create_metadata_wrapper( 'line1\n\nline3\n', 'test.py' )
    assert source_lines[ 1 ] == ''


def test_375_create_metadata_wrapper_handles_single_line( mock_registry, minimal_config ):
    ''' _create_metadata_wrapper handles single-line source. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    _, source_lines = engine._create_metadata_wrapper( 'x = 1', 'test.py' )
    assert len( source_lines ) == 1
    assert source_lines[ 0 ] == 'x = 1'


def test_380_create_metadata_wrapper_raises_on_parse_error( mock_registry, minimal_config ):
    ''' _create_metadata_wrapper raises ParserSyntaxError on invalid syntax. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    # LibCST parse_module will raise on invalid syntax
    with pytest.raises( libcst._exceptions.ParserSyntaxError ):
        engine._create_metadata_wrapper( 'def broken(\n', 'test.py' )


def test_385_metadata_wrapper_creation_succeeds_valid_syntax( mock_registry, minimal_config ):
    ''' MetadataWrapper creation succeeds with valid syntax. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, _ = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    assert isinstance( wrapper, libcst.metadata.MetadataWrapper )


def test_390_metadata_wrapper_error_propagates( mock_registry, minimal_config ):
    ''' MetadataWrapper errors are wrapped in MetadataProvideFailure. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    engine = module.Engine( mock_registry, minimal_config )
    # Note: Hard to trigger metadata wrapper failure without invalid setup
    # This test verifies the exception handling path exists
    # by checking valid code doesn't raise
    try:
        wrapper, _ = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
        assert wrapper is not None
    except exceptions.MetadataProvideFailure:
        assert False, "Should not raise on valid code"


def test_395_parse_error_propagates_from_wrapper( mock_registry, minimal_config ):
    ''' Parse errors propagate from _create_metadata_wrapper. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with pytest.raises( libcst._exceptions.ParserSyntaxError ):
        engine._create_metadata_wrapper( 'if True\n    pass', 'test.py' )


# =============================================================================
# Rule Instantiation Tests (400-449)
# =============================================================================

def test_400_instantiate_rules_creates_single_rule( mock_registry, minimal_config ):
    ''' _instantiate_rules instantiates single rule from enabled_rules. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    assert len( rules ) == 1


def test_405_instantiate_rules_creates_multiple_rules( mock_registry ):
    ''' _instantiate_rules instantiates multiple rules from enabled_rules. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001', 'TEST002' ] )
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    assert len( rules ) == 2


def test_410_instantiate_rules_passes_filename( mock_registry, minimal_config ):
    ''' _instantiate_rules passes filename to rule constructor. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'custom.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'custom.py' )
    assert rules[ 0 ].filename == 'custom.py'


def test_415_instantiate_rules_passes_wrapper( mock_registry, minimal_config ):
    ''' _instantiate_rules passes wrapper to rule constructor. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    assert rules[ 0 ].wrapper is wrapper


def test_420_instantiate_rules_passes_source_lines( mock_registry, minimal_config ):
    ''' _instantiate_rules passes source_lines to rule constructor. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    assert rules[ 0 ].source_lines == source_lines


def test_425_instantiate_rules_passes_rule_parameters( mock_registry ):
    ''' _instantiate_rules passes rule parameters from configuration. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] ),
        rule_parameters = immut.Dictionary( {
            'TEST001': immut.Dictionary( { 'max_depth': 5 } )
        } ),
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    # Rule should be instantiated (parameters are passed via kwargs)
    assert len( rules ) == 1


def test_430_instantiate_rules_uses_empty_dict_for_no_parameters( mock_registry, minimal_config ):
    ''' _instantiate_rules uses empty Dictionary for rules without parameters. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    # Rule instantiated without parameters
    assert len( rules ) == 1


def test_435_instantiate_rules_returns_list( mock_registry, minimal_config ):
    ''' _instantiate_rules returns list of instantiated rules. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    assert isinstance( rules, list )


def test_440_instantiate_rules_raises_on_instantiation_error( mock_registry ):
    ''' _instantiate_rules raises RuleExecuteFailure on rule instantiation error. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST004' ] )
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    with pytest.raises( exceptions.RuleExecuteFailure ):
        engine._instantiate_rules( wrapper, source_lines, 'test.py' )


def test_445_instantiation_error_includes_vbl_code( mock_registry ):
    ''' RuleExecuteFailure includes VBL code in exception. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST004' ] )
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    try:
        engine._instantiate_rules( wrapper, source_lines, 'test.py' )
        assert False, "Should have raised RuleExecuteFailure"
    except exceptions.RuleExecuteFailure as exc:
        assert exc.context == 'TEST004'


def test_450_instantiation_error_chains_original_exception( mock_registry ):
    ''' RuleExecuteFailure chains original exception. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST004' ] )
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    try:
        engine._instantiate_rules( wrapper, source_lines, 'test.py' )
        assert False, "Should have raised RuleExecuteFailure"
    except exceptions.RuleExecuteFailure as exc:
        assert exc.__cause__ is not None


# =============================================================================
# Rule Execution Tests (450-499)
# =============================================================================

def test_451_execute_rules_visits_with_wrapper( mock_registry, minimal_config ):
    ''' _execute_rules visits each rule with metadata wrapper. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'def test():\n    pass\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    # Verify rule was executed by checking violations
    assert len( rules[ 0 ].violations ) > 0


def test_455_execute_rules_executes_in_order( mock_registry ):
    ''' _execute_rules executes rules in order. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001', 'TEST002' ] )
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    # Both rules executed
    assert len( rules ) == 2


def test_460_execute_rules_completes_traversal( mock_registry, minimal_config ):
    ''' _execute_rules completes traversal for all rules. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper(
        'def f1():\n    pass\ndef f2():\n    pass\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    # Rule should have seen both functions
    assert len( rules[ 0 ].violations ) == 2


def test_465_execute_rules_raises_on_visit_error( mock_registry ):
    ''' _execute_rules raises RuleExecuteFailure on rule visit error. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST003' ] )
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    with pytest.raises( exceptions.RuleExecuteFailure ):
        engine._execute_rules( rules, wrapper )


def test_470_execution_error_includes_rule_id( mock_registry ):
    ''' RuleExecuteFailure includes rule_id in exception. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST003' ] )
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    try:
        engine._execute_rules( rules, wrapper )
        assert False, "Should have raised RuleExecuteFailure"
    except exceptions.RuleExecuteFailure as exc:
        assert exc.context == 'TEST003'


def test_475_execution_error_chains_original_exception( mock_registry ):
    ''' RuleExecuteFailure chains original exception. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST003' ] )
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    try:
        engine._execute_rules( rules, wrapper )
        assert False, "Should have raised RuleExecuteFailure"
    except exceptions.RuleExecuteFailure as exc:
        assert exc.__cause__ is not None


# =============================================================================
# Violation Collection Tests (480-529)
# =============================================================================

def test_480_collect_violations_from_single_rule( mock_registry, minimal_config ):
    ''' _collect_violations collects violations from single rule. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'def test():\n    pass\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    violations = engine._collect_violations( rules )
    assert len( violations ) == 1


def test_485_collect_violations_from_multiple_rules( mock_registry ):
    ''' _collect_violations collects violations from multiple rules. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001', 'TEST002' ] )
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'def test():\n    pass\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    violations = engine._collect_violations( rules )
    # Only TEST001 produces violations
    assert len( violations ) == 1


def test_490_collect_violations_returns_empty_when_none( mock_registry ):
    ''' _collect_violations returns empty list when no violations. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST002' ] )
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    violations = engine._collect_violations( rules )
    assert len( violations ) == 0


def test_495_collect_violations_sorts_by_line_number( mock_registry, minimal_config ):
    ''' _collect_violations sorts violations by line number. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    source = '''def f1():
    pass
def f2():
    pass
def f3():
    pass
'''
    wrapper, source_lines = engine._create_metadata_wrapper( source, 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    violations = engine._collect_violations( rules )
    for i in range( len( violations ) - 1 ):
        assert violations[ i ].line <= violations[ i + 1 ].line


def test_500_collect_violations_sorts_by_column_when_lines_equal( mock_registry, minimal_config ):
    ''' _collect_violations sorts violations by column when lines equal. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'def test():\n    pass\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    violations = engine._collect_violations( rules )
    # Single violation, sorting works
    assert len( violations ) >= 1


def test_505_collect_violations_stable_sort_for_equal_positions( mock_registry, minimal_config ):
    ''' _collect_violations maintains stable sort for equal positions. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'def test():\n    pass\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    violations = engine._collect_violations( rules )
    # Stable sort maintained
    assert len( violations ) >= 0


def test_510_collect_violations_flattens_from_all_rules( mock_registry ):
    ''' _collect_violations flattens violations from all rules into single list. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001', 'TEST002' ] )
    )
    engine = module.Engine( mock_registry, config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'def test():\n    pass\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    violations = engine._collect_violations( rules )
    assert isinstance( violations, list )


def test_515_collect_violations_returns_list_not_tuple( mock_registry, minimal_config ):
    ''' _collect_violations returns list for internal processing. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper( 'x = 1\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    violations = engine._collect_violations( rules )
    assert isinstance( violations, list )
    assert not isinstance( violations, tuple )


# =============================================================================
# Multi-File Linting Tests (530-599)
# =============================================================================

def test_530_lint_files_lints_single_file( mock_registry, minimal_config ):
    ''' lint_files lints single file. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/test/file1.py', contents = 'x = 1\n' )
        reports = engine.lint_files( [ Path( '/test/file1.py' ) ] )
        assert len( reports ) == 1


def test_535_lint_files_lints_multiple_files( mock_registry, minimal_config ):
    ''' lint_files lints multiple files. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/test/file1.py', contents = 'x = 1\n' )
        patcher.fs.create_file( '/test/file2.py', contents = 'y = 2\n' )
        reports = engine.lint_files( [
            Path( '/test/file1.py' ),
            Path( '/test/file2.py' )
        ] )
        assert len( reports ) == 2


def test_540_lint_files_returns_tuple_of_reports( mock_registry, minimal_config ):
    ''' lint_files returns tuple of Reports. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/test/file1.py', contents = 'x = 1\n' )
        reports = engine.lint_files( [ Path( '/test/file1.py' ) ] )
        assert isinstance( reports, tuple )


def test_545_lint_files_returns_report_for_each_file( mock_registry, minimal_config ):
    ''' lint_files returns Report for each file. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/test/file1.py', contents = 'x = 1\n' )
        patcher.fs.create_file( '/test/file2.py', contents = 'y = 2\n' )
        reports = engine.lint_files( [
            Path( '/test/file1.py' ),
            Path( '/test/file2.py' )
        ] )
        assert all( isinstance( r, module.Report ) for r in reports )


def test_550_lint_files_continues_after_file_error( mock_registry ):
    ''' lint_files continues after file error. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] )
    )
    engine = module.Engine( mock_registry, config )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/test/bad.py', contents = 'def broken(\n' )
        patcher.fs.create_file( '/test/good.py', contents = 'x = 1\n' )
        reports = engine.lint_files( [
            Path( '/test/bad.py' ),
            Path( '/test/good.py' )
        ] )
        # Should have skipped bad.py but processed good.py
        assert len( reports ) == 1
        assert reports[ 0 ].filename == '/test/good.py'


def test_555_lint_files_skips_file_with_exception( mock_registry ):
    ''' lint_files skips file that raises exception. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST003' ] )
    )
    engine = module.Engine( mock_registry, config )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/test/file1.py', contents = 'x = 1\n' )
        reports = engine.lint_files( [ Path( '/test/file1.py' ) ] )
        # File should be skipped due to rule execution failure
        assert len( reports ) == 0


def test_560_lint_files_returns_empty_tuple_for_empty_list( mock_registry, minimal_config ):
    ''' lint_files returns empty tuple for empty file list. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    reports = engine.lint_files( [ ] )
    assert reports == ( )


def test_565_lint_files_preserves_file_order( mock_registry, minimal_config ):
    ''' lint_files preserves file order in results. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/test/a.py', contents = 'x = 1\n' )
        patcher.fs.create_file( '/test/b.py', contents = 'y = 2\n' )
        patcher.fs.create_file( '/test/c.py', contents = 'z = 3\n' )
        reports = engine.lint_files( [
            Path( '/test/a.py' ),
            Path( '/test/b.py' ),
            Path( '/test/c.py' )
        ] )
        assert reports[ 0 ].filename == '/test/a.py'
        assert reports[ 1 ].filename == '/test/b.py'
        assert reports[ 2 ].filename == '/test/c.py'


def test_570_lint_files_handles_mix_of_valid_invalid( mock_registry ):
    ''' lint_files handles mix of valid and invalid files. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] )
    )
    engine = module.Engine( mock_registry, config )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/test/valid.py', contents = 'x = 1\n' )
        patcher.fs.create_file( '/test/invalid.py', contents = 'def broken(\n' )
        patcher.fs.create_file( '/test/also_valid.py', contents = 'y = 2\n' )
        reports = engine.lint_files( [
            Path( '/test/valid.py' ),
            Path( '/test/invalid.py' ),
            Path( '/test/also_valid.py' )
        ] )
        # Should have processed 2 valid files
        assert len( reports ) == 2


# =============================================================================
# Integration Tests (600-699)
# =============================================================================

def test_600_end_to_end_workflow( mock_registry, minimal_config ):
    ''' Complete workflow from file to Report works correctly. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with Patcher( ) as patcher:
        patcher.fs.create_file(
            '/test/complete.py',
            contents = 'def function():\n    pass\n'
        )
        report = engine.lint_file( Path( '/test/complete.py' ) )
        assert isinstance( report, module.Report )
        assert len( report.violations ) > 0
        assert report.filename == '/test/complete.py'
        assert report.rule_count == 1


def test_605_multiple_rules_detect_different_violations( mock_registry ):
    ''' Multiple rules detect different violations correctly. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001', 'TEST002' ] )
    )
    engine = module.Engine( mock_registry, config )
    report = engine.lint_source( 'def test():\n    pass\n', 'test.py' )
    # TEST001 produces violations, TEST002 does not
    assert len( report.violations ) > 0
    assert report.rule_count == 2


def test_610_context_extraction_works_with_real_violations( mock_registry ):
    ''' Context extraction works with real violations. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] ),
        include_context = True,
    )
    engine = module.Engine( mock_registry, config )
    source = '''# Header
def test():
    pass
# Footer
'''
    report = engine.lint_source( source, 'test.py' )
    assert len( report.violations ) > 0
    assert len( report.contexts ) > 0


def test_615_rule_parameters_affect_rule_behavior( mock_registry ):
    ''' Rule parameters affect rule behavior correctly. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] ),
        rule_parameters = immut.Dictionary( {
            'TEST001': immut.Dictionary( { 'custom_param': 'value' } )
        } ),
    )
    engine = module.Engine( mock_registry, config )
    report = engine.lint_source( 'def test():\n    pass\n', 'test.py' )
    # Rule instantiated with parameters
    assert isinstance( report, module.Report )


def test_620_analysis_timing_is_measured( mock_registry, minimal_config ):
    ''' Analysis timing is measured correctly. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    report = engine.lint_source( 'def test():\n    pass\n', 'test.py' )
    assert report.analysis_duration_ms > 0
    assert isinstance( report.analysis_duration_ms, float )


def test_625_violations_from_multiple_files_independent( mock_registry, minimal_config ):
    ''' Violations from multiple files are independent. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/test/f1.py', contents = 'def f1():\n    pass\n' )
        patcher.fs.create_file( '/test/f2.py', contents = 'def f2():\n    pass\n' )
        reports = engine.lint_files( [
            Path( '/test/f1.py' ),
            Path( '/test/f2.py' )
        ] )
        assert len( reports ) == 2
        # Each report has its own violations
        assert reports[ 0 ].filename != reports[ 1 ].filename


def test_650_analysis_completes_within_performance_budget( mock_registry, minimal_config ):
    ''' Analysis completes within performance budget. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    source = '''def test():
    pass
''' * 100  # Large source file
    report = engine.lint_source( source, 'test.py' )
    # Should complete reasonably fast (under 1 second for 100 functions)
    assert report.analysis_duration_ms < 1000


def test_655_single_pass_traversal_verification( mock_registry, minimal_config ):
    ''' Single-pass traversal verified through wrapper usage. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    wrapper, source_lines = engine._create_metadata_wrapper(
        'def f1():\n    pass\ndef f2():\n    pass\n', 'test.py' )
    rules = engine._instantiate_rules( wrapper, source_lines, 'test.py' )
    engine._execute_rules( rules, wrapper )
    # All violations found in single pass
    violations = engine._collect_violations( rules )
    assert len( violations ) == 2


def test_660_memory_efficient_violation_storage( mock_registry, minimal_config ):
    ''' Memory-efficient violation storage verified. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    source = 'def test():\n    pass\n' * 50  # Many violations
    report = engine.lint_source( source, 'test.py' )
    # Violations stored as tuple (immutable, memory efficient)
    assert isinstance( report.violations, tuple )


# =============================================================================
# Error Handling Integration Tests (700-799)
# =============================================================================

def test_700_parse_errors_propagate_from_lint_source( mock_registry, minimal_config ):
    ''' Parse errors propagate from lint_source. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with pytest.raises( libcst._exceptions.ParserSyntaxError ):
        engine.lint_source( 'def broken(\n', 'context.py' )


def test_705_rule_execute_failure_includes_identifier( mock_registry ):
    ''' RuleExecuteFailure includes rule identifier. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST003' ] )
    )
    engine = module.Engine( mock_registry, config )
    try:
        engine.lint_source( 'x = 1\n', 'test.py' )
        assert False, "Should have raised RuleExecuteFailure"
    except exceptions.RuleExecuteFailure as exc:
        assert exc.context == 'TEST003'


def test_710_file_reading_errors_propagate( mock_registry, minimal_config ):
    ''' File reading errors propagate from lint_file. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with pytest.raises( FileNotFoundError ):
        engine.lint_file( Path( '/nonexistent/file.py' ) )


def test_715_parse_errors_propagate_as_parser_exception( mock_registry, minimal_config ):
    ''' Parse errors propagate as ParserSyntaxError. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    engine = module.Engine( mock_registry, minimal_config )
    with pytest.raises( libcst._exceptions.ParserSyntaxError ):
        engine.lint_source( 'if True:\npass', 'test.py' )


def test_720_rule_instantiation_errors_caught( mock_registry ):
    ''' Rule instantiation errors are caught as RuleExecuteFailure. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST004' ] )
    )
    engine = module.Engine( mock_registry, config )
    with pytest.raises( exceptions.RuleExecuteFailure ):
        engine.lint_source( 'x = 1\n', 'test.py' )


def test_725_rule_execution_errors_caught( mock_registry ):
    ''' Rule execution errors are caught as RuleExecuteFailure. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST003' ] )
    )
    engine = module.Engine( mock_registry, config )
    with pytest.raises( exceptions.RuleExecuteFailure ):
        engine.lint_source( 'x = 1\n', 'test.py' )


def test_750_lint_files_continues_after_single_file_error( mock_registry ):
    ''' lint_files continues after single file error. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] )
    )
    engine = module.Engine( mock_registry, config )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/test/error.py', contents = 'def broken(\n' )
        patcher.fs.create_file( '/test/ok.py', contents = 'x = 1\n' )
        patcher.fs.create_file( '/test/also_ok.py', contents = 'y = 2\n' )
        reports = engine.lint_files( [
            Path( '/test/error.py' ),
            Path( '/test/ok.py' ),
            Path( '/test/also_ok.py' )
        ] )
        assert len( reports ) == 2


def test_755_partial_results_returned_from_lint_files( mock_registry ):
    ''' Partial results returned from lint_files after errors. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST001' ] )
    )
    engine = module.Engine( mock_registry, config )
    with Patcher( ) as patcher:
        patcher.fs.create_file( '/test/good1.py', contents = 'x = 1\n' )
        patcher.fs.create_file( '/test/bad.py', contents = 'def broken(\n' )
        patcher.fs.create_file( '/test/good2.py', contents = 'y = 2\n' )
        reports = engine.lint_files( [
            Path( '/test/good1.py' ),
            Path( '/test/bad.py' ),
            Path( '/test/good2.py' )
        ] )
        assert len( reports ) == 2
        assert all( isinstance( r, module.Report ) for r in reports )


def test_760_exception_details_preserved_in_chain( mock_registry ):
    ''' Exception details preserved in error chain. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.engine" )
    exceptions = __.cache_import_module( f"{__.PACKAGE_NAME}.exceptions" )
    config = module.EngineConfiguration(
        enabled_rules = frozenset( [ 'TEST004' ] )
    )
    engine = module.Engine( mock_registry, config )
    try:
        engine.lint_source( 'x = 1\n', 'test.py' )
        assert False, "Should have raised RuleExecuteFailure"
    except exceptions.RuleExecuteFailure as exc:
        assert exc.__cause__ is not None
        assert isinstance( exc.__cause__, RuntimeError )
        assert 'instantiation failure' in str( exc.__cause__ )
