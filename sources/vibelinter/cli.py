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


''' Command-line interface. '''

# ruff: noqa: F821


from appcore import cli as _appcore_cli

from . import __
from . import configuration as _configuration
from . import engine as _engine
from . import fixer as _fixer
from . import rules as _rules
# Ensure registry is available for type hints
from .rules import registry as _registry


class DiffFormats( __.enum.Enum ):
    ''' Diff visualization formats. '''

    Unified = 'unified'
    Context = 'context'


class DisplayFormats( __.enum.Enum ):
    ''' Output formats for reporting. '''

    Text = 'text'
    Json = 'json'


class DisplayOptions( _appcore_cli.DisplayOptions ):
    ''' Display options extending appcore.cli with output format selection.

        Adds format-specific output control for linter reporting.
    '''

    format: __.typx.Annotated[
        DisplayFormats,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Output format for reporting. ''' )
    ] = DisplayFormats.Text
    context: __.typx.Annotated[
        int,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Show context lines around violations. ''' )
    ] = 0


RuleSelectorArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ str ],
    __.tyro.conf.arg( prefix_name = False ),
    __.ddoc.Doc(
        ''' Comma-separated rule identifiers '''
        ''' (e.g. VBL101, function-ordering). '''
    )
]
PathsArgument: __.typx.TypeAlias = __.tyro.conf.Positional[
    tuple[ str, ... ]
]


class RenderableResult( __.immut.DataclassProtocol, __.typx.Protocol ):
    ''' Protocol for command results with format-specific rendering.

        Combines DataclassProtocol and Protocol to provide both structural
        typing and dataclass compatibility. Result classes should explicitly
        inherit from this base class.
    '''

    @__.abc.abstractmethod
    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ''' Renders result as JSON-compatible dictionary. '''
        raise NotImplementedError

    @__.abc.abstractmethod
    def render_as_text( self ) -> tuple[ str, ... ]:
        ''' Renders result as text lines. '''
        raise NotImplementedError


class CheckResult( RenderableResult ):
    ''' Result from check command execution. '''

    paths: tuple[ str, ... ]
    reports: tuple[ __.typx.Any, ... ]  # Engine Report objects
    total_violations: int
    total_files: int
    rule_selection: __.typx.Optional[ str ] = None

    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ''' Renders result as JSON-compatible dictionary. '''
        files_data: list[ dict[ str, __.typx.Any ] ] = [ ]
        for report_obj in self.reports:
            typed_report = __.typx.cast( _engine.Report, report_obj )
            violations_data = [
                v.render_as_json( ) for v in typed_report.violations
            ]
            files_data.append( {
                'filename': typed_report.filename,
                'violations': violations_data,
                'violation_count': len( typed_report.violations ),
                'rule_count': typed_report.rule_count,
                'analysis_duration_ms': typed_report.analysis_duration_ms,
            } )
        result: dict[ str, __.typx.Any ] = {
            'files': files_data,
            'total_violations': self.total_violations,
            'total_files': self.total_files,
        }
        if self.rule_selection is not None:
            result[ 'rule_selection' ] = self.rule_selection
        return result

    def render_as_text( self ) -> tuple[ str, ... ]:
        ''' Renders result as text lines. '''
        lines: list[ str ] = [ ]
        for report_obj in self.reports:
            typed_report = __.typx.cast( _engine.Report, report_obj )
            if typed_report.violations:
                lines.append( f"\n{typed_report.filename}:" )
                lines.extend(
                    v.render_as_text( )
                    for v in typed_report.violations )
        if not lines:
            lines.append( 'No violations found.' )
        else:
            lines.append(
                f"\nFound {self.total_violations} violations "
                f"in {self.total_files} files." )
        return tuple( lines )


class FixResult( RenderableResult ):
    ''' Result from fix command execution. '''

    paths: tuple[ str, ... ]
    simulate: bool
    diff_format: str
    apply_dangerous: bool
    file_results: tuple[ _fixer.FixApplicationResult, ... ]
    total_applied: int
    total_skipped: int
    total_conflicts: int
    rule_selection: __.typx.Optional[ str ] = None

    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ''' Renders result as JSON-compatible dictionary. '''
        files_data: list[ dict[ str, __.typx.Any ] ] = [ ]
        for file_result in self.file_results:
            file_data: dict[ str, __.typx.Any ] = {
                'filename': file_result.filename,
                'applied_count': len( file_result.applied_fixes ),
                'skipped_count': len( file_result.skipped_fixes ),
                'conflict_count': len( file_result.conflicts ),
                'has_changes': file_result.has_changes,
            }
            if file_result.has_changes and self.simulate:
                file_data[ 'diff' ] = file_result.generate_unified_diff( )
            files_data.append( file_data )
        result: dict[ str, __.typx.Any ] = {
            'paths': list( self.paths ),
            'simulate': self.simulate,
            'diff_format': self.diff_format,
            'apply_dangerous': self.apply_dangerous,
            'files': files_data,
            'total_applied': self.total_applied,
            'total_skipped': self.total_skipped,
            'total_conflicts': self.total_conflicts,
        }
        if self.rule_selection is not None:
            result[ 'rule_selection' ] = self.rule_selection
        return result

    def render_as_text( self ) -> tuple[ str, ... ]:
        ''' Renders result as text lines. '''
        lines: list[ str ] = [ ]
        for file_result in self.file_results:
            if not file_result.has_changes:
                continue
            lines.append( f"\n{file_result.filename}:" )
            if self.simulate:
                diff = (
                    file_result.generate_context_diff( )
                    if self.diff_format == 'context'
                    else file_result.generate_unified_diff( )
                )
                lines.append( diff )
            else:
                lines.extend(
                    fix.render_as_text( )
                    for fix in file_result.applied_fixes )
            # Report skipped fixes
            lines.extend(
                '  [skipped] {line}:{col} {reason}'.format(
                    line = skipped.fix.violation.line,
                    col = skipped.fix.violation.column,
                    reason = skipped.reason )
                for skipped in file_result.skipped_fixes )
        if not lines:
            lines.append( 'No fixes to apply.' )
        else:
            action = 'Would apply' if self.simulate else 'Applied'
            lines.append(
                f"\n{action} {self.total_applied} fixes "
                f"({self.total_skipped} skipped, "
                f"{self.total_conflicts} conflicts)."
            )
        return tuple( lines )


class ConfigureResult( RenderableResult ):
    ''' Result from configure command execution. '''

    validate: bool
    interactive: bool
    display_effective: bool

    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ''' Renders result as JSON-compatible dictionary. '''
        return {
            'validate': self.validate,
            'interactive': self.interactive,
            'display_effective': self.display_effective,
        }

    def render_as_text( self ) -> tuple[ str, ... ]:
        ''' Renders result as text lines. '''
        return (
            'Configure command',
            f"  Validate: {self.validate}",
            f"  Interactive: {self.interactive}",
            f"  Display effective: {self.display_effective}",
        )


class DescribeRulesResult( RenderableResult ):
    ''' Result from describe rules command execution. '''

    rules: tuple[ _registry.RuleDescriptor, ... ]
    details: bool

    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ''' Renders result as JSON-compatible dictionary. '''
        return {
            'rules': [
                {
                    'vbl_code': rule.vbl_code,
                    'descriptive_name': rule.descriptive_name,
                    'description': rule.description,
                    'category': rule.category,
                    'subcategory': rule.subcategory,
                }
                for rule in self.rules
            ],
            'details': self.details,
        }

    def render_as_text( self ) -> tuple[ str, ... ]:
        ''' Renders result as text lines. '''
        lines = [ 'Available rules:' ]
        for rule in sorted( self.rules, key = lambda r: r.descriptive_name ):
            if self.details:
                lines.append(
                    f"  {rule.descriptive_name} ({rule.vbl_code}) - "
                    f"{rule.category}/{rule.subcategory}" )
            else:
                lines.append(
                    f"  {rule.descriptive_name} ({rule.vbl_code})" )
        return tuple( lines )


class DescribeRuleResult( RenderableResult ):
    ''' Result from describe rule command execution. '''

    rule: _registry.RuleDescriptor
    details: bool

    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ''' Renders result as JSON-compatible dictionary. '''
        return {
            'vbl_code': self.rule.vbl_code,
            'descriptive_name': self.rule.descriptive_name,
            'description': self.rule.description,
            'category': self.rule.category,
            'subcategory': self.rule.subcategory,
            'violation_message': self.rule.violation_message,
            'examples': self.rule.examples,
            'details': self.details,
        }

    def render_as_text( self ) -> tuple[ str, ... ]:
        ''' Renders result as text lines. '''
        lines = [
            f"Rule: {self.rule.descriptive_name} ({self.rule.vbl_code})",
            '',
            f"Description: {self.rule.description}",
            '',
            f"Category: {self.rule.category}/{self.rule.subcategory}",
        ]
        if self.details:
            lines.extend( [
                '',
                'Configuration Status: '
                '(configuration display not yet implemented)',
            ] )
        lines.extend( [
            '',
            f"Violation Message: {self.rule.violation_message}",
            '',
            'Examples:',
        ] )
        # Split examples by lines and indent them
        if self.rule.examples:
            lines.extend(
                f"  {example_line}"
                for example_line in self.rule.examples.split( '\n' )
            )
        else:
            lines.append( '  (No examples provided)' )
        return tuple( lines )


class ServeResult( RenderableResult ):
    ''' Result from serve command execution. '''

    protocol: str

    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ''' Renders result as JSON-compatible dictionary. '''
        return {
            'protocol': self.protocol,
            'status': 'not_implemented',
        }

    def render_as_text( self ) -> tuple[ str, ... ]:
        ''' Renders result as text lines. '''
        return (
            f"Protocol server: {self.protocol}",
            '  (Not yet implemented)',
        )


class CheckCommand( __.immut.DataclassObject ):
    ''' Analyzes code and reports violations. '''

    paths: PathsArgument = ( '.', )
    select: RuleSelectorArgument = None
    jobs: __.typx.Annotated[
        __.typx.Union[ int, __.typx.Literal[ 'auto' ] ],
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Number of parallel processing jobs. ''' )
    ] = 'auto'

    async def __call__( self, display: DisplayOptions ) -> int:
        ''' Executes the check command. '''
        # TODO: Implement parallel processing with jobs parameter
        _ = self.jobs  # Suppress vulture warning
        config = _configuration.discover_configuration( )
        file_paths = _discover_python_files( self.paths )
        if not __.is_absent( config ):
            file_paths = _apply_path_filters( file_paths, config )
        if not file_paths:
            result = CheckResult(
                paths = self.paths,
                reports = ( ),
                total_violations = 0,
                total_files = 0,
                rule_selection = self.select,
            )
            async with __.ctxl.AsyncExitStack( ) as exits:
                await _render_and_print_result( result, display, exits )
            return 0
        select = self.select if self.select is not None else __.absent
        enabled_rules = _merge_rule_selection(
            select, config, _rules.create_registry_manager( ) )
        context_size = _merge_context_size( display.context, config )
        rule_parameters: __.immut.Dictionary[
            str, __.immut.Dictionary[ str, __.typx.Any ] ]
        per_file_ignores: __.immut.Dictionary[ str, tuple[ str, ... ] ]
        if __.is_absent( config ):
            rule_parameters = __.immut.Dictionary( )
            per_file_ignores = __.immut.Dictionary( )
        else:
            rule_parameters = config.rule_parameters
            per_file_ignores = config.per_file_ignores
        configuration = _engine.EngineConfiguration(
            enabled_rules = enabled_rules,
            context_size = context_size,
            include_context = context_size > 0,
            rule_parameters = rule_parameters,
            per_file_ignores = per_file_ignores,
        )
        registry_manager = _rules.create_registry_manager( )
        engine = _engine.Engine( registry_manager, configuration )
        reports = engine.lint_files( file_paths )
        total_violations = sum( len( r.violations ) for r in reports )
        result = CheckResult(
            paths = self.paths,
            reports = reports,
            total_violations = total_violations,
            total_files = len( reports ),
            rule_selection = self.select,
        )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, display, exits )
        return 1 if total_violations > 0 else 0


class FixCommand( __.immut.DataclassObject ):
    ''' Applies automated fixes with safety controls. '''

    paths: PathsArgument = ( '.', )
    select: RuleSelectorArgument = None
    simulate: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Preview changes without applying them. ''' )
    ] = False
    diff_format: __.typx.Annotated[
        DiffFormats,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Diff visualization format. ''' )
    ] = DiffFormats.Unified
    apply_dangerous: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Enable potentially unsafe fixes. ''' )
    ] = False

    async def __call__( self, display: DisplayOptions ) -> int:
        ''' Executes the fix command. '''
        config = _configuration.discover_configuration( )
        file_paths = _discover_python_files( self.paths )
        if not __.is_absent( config ):
            file_paths = _apply_path_filters( file_paths, config )
        select = self.select if self.select is not None else __.absent
        file_results = _collect_and_apply_fixes(
            file_paths, select, config,
            self.apply_dangerous, self.simulate )
        total_applied = sum(
            len( r.applied_fixes ) for r in file_results )
        total_skipped = sum(
            len( r.skipped_fixes ) for r in file_results )
        total_conflicts = sum(
            len( r.conflicts ) for r in file_results )
        result = FixResult(
            paths = self.paths,
            simulate = self.simulate,
            diff_format = self.diff_format.value,
            apply_dangerous = self.apply_dangerous,
            file_results = file_results,
            total_applied = total_applied,
            total_skipped = total_skipped,
            total_conflicts = total_conflicts,
            rule_selection = self.select,
        )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, display, exits )
        return 1 if total_applied > 0 and not self.simulate else 0


class ConfigureCommand( __.immut.DataclassObject ):
    ''' Manages configuration without destructive file editing. '''

    validate: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc(
            ''' Validate existing configuration without analysis. ''' )
    ] = False
    interactive: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Interactive configuration wizard. ''' )
    ] = False
    display_effective: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Display effective merged configuration. ''' )
    ] = False

    async def __call__( self, display: DisplayOptions ) -> int:
        ''' Executes the configure command. '''
        result = ConfigureResult(
            validate = self.validate,
            interactive = self.interactive,
            display_effective = self.display_effective,
        )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, display, exits )
        return 0


class DescribeRulesCommand( __.immut.DataclassObject ):
    ''' Lists all available rules with descriptions. '''

    details: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc(
            ''' Display detailed rule information including '''
            ''' configuration status. ''' )
    ] = False

    async def __call__( self, display: DisplayOptions ) -> int:
        ''' Executes the describe rules command. '''
        registry_manager = _rules.create_registry_manager( )
        rules = registry_manager.survey_available_rules( )
        result = DescribeRulesResult( rules = rules, details = self.details )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, display, exits )
        return 0


class DescribeRuleCommand( __.immut.DataclassObject ):
    ''' Displays detailed information for a specific rule. '''

    rule_id: __.tyro.conf.Positional[ str ]
    details: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc(
            ''' Display detailed rule information including '''
            ''' configuration status. ''' )
    ] = False

    async def __call__( self, display: DisplayOptions ) -> int:
        ''' Executes the describe rule command. '''
        registry_manager = _rules.create_registry_manager( )
        vbl_code = registry_manager.resolve_rule_identifier( self.rule_id )
        rule_descriptor = registry_manager.registry[ vbl_code ]
        result = DescribeRuleResult(
            rule = rule_descriptor,
            details = self.details,
        )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, display, exits )
        return 0


class DescribeCommand( __.immut.DataclassObject ):
    ''' Displays rule information and documentation. '''

    subcommand: __.typx.Union[
        __.typx.Annotated[
            DescribeRulesCommand,
            __.tyro.conf.subcommand( 'rules', prefix_name = False ),
        ],
        __.typx.Annotated[
            DescribeRuleCommand,
            __.tyro.conf.subcommand( 'rule', prefix_name = False ),
        ],
    ]

    async def __call__( self, display: DisplayOptions ) -> int:
        ''' Delegates to selected subcommand. '''
        return await self.subcommand( display )


class ServeCommand( __.immut.DataclassObject ):
    ''' Starts a protocol server (future implementation). '''

    protocol: __.typx.Annotated[
        __.typx.Literal[ 'lsp', 'mcp' ],
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Protocol server to start. ''' )
    ] = 'mcp'

    async def __call__( self, display: DisplayOptions ) -> int:
        ''' Executes the serve command. '''
        result = ServeResult( protocol = self.protocol )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, display, exits )
        return 0


class Cli( __.immut.DataclassObject ):
    ''' Linter command-line interface. '''

    command: __.typx.Union[
        __.typx.Annotated[
            CheckCommand,
            __.tyro.conf.subcommand(
                'check', prefix_name = False, default = True ),
        ],
        __.typx.Annotated[
            FixCommand,
            __.tyro.conf.subcommand( 'fix', prefix_name = False ),
        ],
        __.typx.Annotated[
            ConfigureCommand,
            __.tyro.conf.subcommand( 'configure', prefix_name = False ),
        ],
        __.typx.Annotated[
            DescribeCommand,
            __.tyro.conf.subcommand( 'describe', prefix_name = False ),
        ],
        __.typx.Annotated[
            ServeCommand,
            __.tyro.conf.subcommand( 'serve', prefix_name = False ),
        ],
    ]
    display: __.typx.Annotated[
        DisplayOptions,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = DisplayOptions )
    verbose: __.typx.Annotated[
        bool,
        __.ddoc.Doc( ''' Enable verbose output. ''' )
    ] = False

    async def __call__( self ) -> None:
        ''' Invokes selected subcommand after system preparation. '''
        # TODO: Implement verbose logging setup
        _ = self.verbose  # Suppress vulture warning
        async with intercept_errors( self.display ):
            exit_code = await self.command( self.display )
            raise SystemExit( exit_code )


def execute( ) -> None:
    ''' Entrypoint for CLI execution. '''
    from asyncio import run
    config = (
        __.tyro.conf.EnumChoicesFromValues,
        __.tyro.conf.HelptextFromCommentsOff,
    )
    try: run( __.tyro.cli( Cli, config = config )( ) ) # pyright: ignore
    except SystemExit: raise
    except BaseException:
        # TODO: Log exception with proper error handling
        raise SystemExit( 1 ) from None


@__.ctxl.asynccontextmanager
async def intercept_errors(
    display: DisplayOptions,
) -> __.cabc.AsyncIterator[ None ]:
    ''' Context manager that intercepts and renders exceptions.

        Catches Omnierror exceptions and renders them according to the
        display format. Handles unexpected exceptions by logging and
        formatting as errors.
    '''
    from . import exceptions as _exceptions
    try:
        yield
    except _exceptions.Omnierror as exc:
        async with __.ctxl.AsyncExitStack( ) as exits:
            stream = await display.provide_stream( exits )
            match display.format:
                case DisplayFormats.Json:
                    stream.write(
                        __.json.dumps( exc.render_as_json( ), indent = 2 ) )
                    stream.write( '\n' )
                case DisplayFormats.Text:
                    for line in exc.render_as_text( ):
                        stream.write( line )
                        stream.write( '\n' )
        raise SystemExit( 1 ) from exc
    except ( SystemExit, KeyboardInterrupt ):
        raise
    except BaseException as exc:
        # TODO: Log exception with proper error handling via scribe
        async with __.ctxl.AsyncExitStack( ) as exits:
            stream = await display.provide_stream( exits )
            match display.format:
                case DisplayFormats.Json:
                    error_data = {
                        'type': 'unexpected_error',
                        'message': str( exc ),
                    }
                    stream.write( __.json.dumps( error_data, indent = 2 ) )
                    stream.write( '\n' )
                case DisplayFormats.Text:
                    stream.write( '## Unexpected Error\n' )
                    stream.write( f"**Message**: {exc}\n" )
        raise SystemExit( 1 ) from exc


def _collect_and_apply_fixes(
    file_paths: tuple[ __.pathlib.Path, ... ],
    select: __.Absential[ str ],
    config: __.Absential[ __.typx.Any ],
    apply_dangerous: bool,
    simulate: bool,
) -> tuple[ _fixer.FixApplicationResult, ... ]:
    ''' Collects and applies fixes to files. '''
    if not file_paths:
        return ( )
    enabled_rules = _merge_rule_selection(
        select, config, _rules.create_registry_manager( ) )
    rule_parameters: __.immut.Dictionary[
        str, __.immut.Dictionary[ str, __.typx.Any ] ]
    per_file_ignores: __.immut.Dictionary[ str, tuple[ str, ... ] ]
    if __.is_absent( config ):
        rule_parameters = __.immut.Dictionary( )
        per_file_ignores = __.immut.Dictionary( )
    else:
        rule_parameters = config.rule_parameters
        per_file_ignores = config.per_file_ignores
    configuration = _engine.EngineConfiguration(
        enabled_rules = enabled_rules,
        context_size = 0,
        include_context = False,
        rule_parameters = rule_parameters,
        per_file_ignores = per_file_ignores,
    )
    registry_manager = _rules.create_registry_manager( )
    engine = _engine.Engine( registry_manager, configuration )
    fix_engine = _fixer.FixEngine( apply_dangerous = apply_dangerous )
    file_results: list[ _fixer.FixApplicationResult ] = [ ]
    for file_path in file_paths:
        try:
            fix_report = engine.collect_fixes_for_file( file_path )
            if not fix_report.fixes: continue
            file_result = fix_engine.apply_fixes_to_file(
                file_path, fix_report.fixes, simulate = simulate )
            file_results.append( file_result )
        except Exception: continue  # noqa: S112
    return tuple( file_results )


def _discover_python_files(
    paths: __.cabc.Sequence[ str ]
) -> tuple[ __.pathlib.Path, ... ]:
    ''' Discovers Python files from file paths or directories. '''
    python_files: list[ __.pathlib.Path ] = [ ]
    for path_str in paths:
        path = __.pathlib.Path( path_str )
        if not path.exists( ):
            continue
        if path.is_file( ) and path.suffix == '.py':
            python_files.append( path )
        elif path.is_dir( ):
            python_files.extend( path.rglob( '*.py' ) )
    return tuple( sorted( set( python_files ) ) )


def _apply_path_filters(
    file_paths: tuple[ __.pathlib.Path, ... ],
    config: __.typx.Any,
) -> tuple[ __.pathlib.Path, ... ]:
    ''' Applies include/exclude path filters from configuration. '''
    typed_config = __.typx.cast( _configuration.Configuration, config )
    filtered = list( file_paths )
    if not __.is_absent( typed_config.include_paths ):
        filtered = [
            fp for fp in filtered
            if _matches_any_pattern( fp, typed_config.include_paths )
        ]
    if not __.is_absent( typed_config.exclude_paths ):
        patterns = typed_config.exclude_paths
        filtered = [
            fp for fp in filtered
            if not _matches_any_pattern( fp, patterns )
        ]
    return tuple( filtered )


def _matches_any_pattern(
    file_path: __.pathlib.Path,
    patterns: tuple[ str, ... ],
) -> bool:
    ''' Checks if file path matches any glob pattern. '''
    path_str = str( file_path )
    for pattern in patterns:
        if __.wcglob.globmatch(
            path_str, pattern, flags = __.wcglob.GLOBSTAR ):
            return True
    return False


def _merge_context_size(
    cli_context: int,
    config: __.Absential[ __.typx.Any ],
) -> int:
    ''' Merges context size from CLI and configuration. '''
    if cli_context > 0:
        return cli_context
    if __.is_absent( config ):
        return 0
    typed_config = __.typx.cast( _configuration.Configuration, config )
    if __.is_absent( typed_config.context ):
        return 0
    return typed_config.context


def _resolve_rule_set(
    identifiers: __.cabc.Iterable[ str ],
    registry_manager: _registry.RuleRegistryManager,
) -> set[ str ]:
    ''' Resolves a sequence of rule identifiers to codes. '''
    codes: set[ str ] = set( )
    for raw_identifier in identifiers:
        identifier = raw_identifier.strip( )
        if not identifier:
            continue
        code = registry_manager.resolve_rule_identifier( identifier )
        codes.add( code )
    return codes


def _merge_rule_selection(
    cli_selection: __.Absential[ str ],
    config: __.Absential[ __.typx.Any ],
    registry_manager: _registry.RuleRegistryManager,
) -> frozenset[ str ]:
    ''' Merges rule selection from CLI and configuration. '''
    from .rules.implementations.__ import RULE_DESCRIPTORS
    all_rules = frozenset( RULE_DESCRIPTORS.keys( ) )
    if not __.is_absent( cli_selection ):
        return frozenset( _resolve_rule_set(
            cli_selection.split( ',' ), registry_manager ) )
    if __.is_absent( config ):
        return all_rules
    typed_config = __.typx.cast( _configuration.Configuration, config )
    if not __.is_absent( typed_config.select ):
        selected = _resolve_rule_set(
            typed_config.select, registry_manager )
    else:
        selected = set( all_rules )
    if not __.is_absent( typed_config.exclude_rules ):
        excluded = _resolve_rule_set(
            typed_config.exclude_rules, registry_manager )
        selected -= excluded
    return frozenset( selected )


async def _render_and_print_result(
    result: RenderableResult,
    display: DisplayOptions,
    exits: __.ctxl.AsyncExitStack,
) -> None:
    ''' Renders and prints a result object based on display options. '''
    stream = await display.provide_stream( exits )
    match display.format:
        case DisplayFormats.Json:
            stream.write( __.json.dumps( result.render_as_json( ) ) )
            stream.write( '\n' )
        case DisplayFormats.Text:
            for line in result.render_as_text( ):
                stream.write( line )
                stream.write( '\n' )
