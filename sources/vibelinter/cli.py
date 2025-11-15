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


class DiffFormats( __.enum.Enum ):
    ''' Diff visualization formats. '''

    Unified = 'unified'
    Context = 'context'


class OutputFormats( __.enum.Enum ):
    ''' Output formats for reporting. '''

    Text = 'text'
    Json = 'json'


class DisplayOptions( _appcore_cli.DisplayOptions ):
    ''' Display options extending appcore.cli with output format selection.

        Adds format-specific output control for linter reporting.
    '''

    format: __.typx.Annotated[
        OutputFormats,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Output format for reporting. ''' )
    ] = OutputFormats.Text
    context: __.typx.Annotated[
        int,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Show context lines around violations. ''' )
    ] = 0


# Type aliases for CLI parameters
RuleSelectorArgument: __.typx.TypeAlias = __.typx.Annotated[
    str,
    __.tyro.conf.arg( prefix_name = False ),
    __.ddoc.Doc( ''' Comma-separated VBL rule codes (e.g. VBL101,VBL201). ''' )
]
PathsArgument: __.typx.TypeAlias = __.typx.Annotated[
    tuple[ str, ... ],
    __.tyro.conf.arg( prefix_name = False ),
    __.ddoc.Doc( ''' Files or directories to analyze. ''' )
]


# Result classes for self-rendering output


class CheckResult( __.immut.DataclassObject ):
    ''' Result from check command execution. '''

    paths: tuple[ str, ... ]
    context_lines: int
    jobs: __.typx.Union[ int, str ]
    rule_selection: __.Absential[ str ] = __.absent

    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ''' Renders result as JSON-compatible dictionary. '''
        result: dict[ str, __.typx.Any ] = {
            'paths': list( self.paths ),
            'context_lines': self.context_lines,
            'jobs': self.jobs,
        }
        if not __.is_absent( self.rule_selection ):
            result[ 'rule_selection' ] = self.rule_selection
        return result

    def render_as_text( self ) -> tuple[ str, ... ]:
        ''' Renders result as text lines. '''
        lines = [ f'Checking paths: {self.paths}' ]
        if not __.is_absent( self.rule_selection ):
            lines.append( f'  Rule selection: {self.rule_selection}' )
        lines.append( f'  Context lines: {self.context_lines}' )
        lines.append( f'  Jobs: {self.jobs}' )
        return tuple( lines )


class FixResult( __.immut.DataclassObject ):
    ''' Result from fix command execution. '''

    paths: tuple[ str, ... ]
    simulate: bool
    diff_format: str
    apply_dangerous: bool
    rule_selection: __.Absential[ str ] = __.absent

    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ''' Renders result as JSON-compatible dictionary. '''
        result: dict[ str, __.typx.Any ] = {
            'paths': list( self.paths ),
            'simulate': self.simulate,
            'diff_format': self.diff_format,
            'apply_dangerous': self.apply_dangerous,
        }
        if not __.is_absent( self.rule_selection ):
            result[ 'rule_selection' ] = self.rule_selection
        return result

    def render_as_text( self ) -> tuple[ str, ... ]:
        ''' Renders result as text lines. '''
        lines = [ f'Fixing paths: {self.paths}' ]
        if not __.is_absent( self.rule_selection ):
            lines.append( f'  Rule selection: {self.rule_selection}' )
        lines.append( f'  Simulate: {self.simulate}' )
        lines.append( f'  Diff format: {self.diff_format}' )
        lines.append( f'  Apply dangerous: {self.apply_dangerous}' )
        return tuple( lines )


class ConfigureResult( __.immut.DataclassObject ):
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
            f'  Validate: {self.validate}',
            f'  Interactive: {self.interactive}',
            f'  Display effective: {self.display_effective}',
        )


class DescribeRulesResult( __.immut.DataclassObject ):
    ''' Result from describe rules command execution. '''

    details: bool

    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ''' Renders result as JSON-compatible dictionary. '''
        return { 'details': self.details }

    def render_as_text( self ) -> tuple[ str, ... ]:
        ''' Renders result as text lines. '''
        return (
            'Available rules',
            f'  Details: {self.details}',
        )


class DescribeRuleResult( __.immut.DataclassObject ):
    ''' Result from describe rule command execution. '''

    rule_id: str
    details: bool

    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ''' Renders result as JSON-compatible dictionary. '''
        return {
            'rule_id': self.rule_id,
            'details': self.details,
        }

    def render_as_text( self ) -> tuple[ str, ... ]:
        ''' Renders result as text lines. '''
        return (
            f'Rule: {self.rule_id}',
            f'  Details: {self.details}',
        )


class ServeResult( __.immut.DataclassObject ):
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
            f'Protocol server: {self.protocol}',
            '  (Not yet implemented)',
        )


async def _render_and_print_result(
    result: __.typx.Union[
        CheckResult, FixResult, ConfigureResult,
        DescribeRulesResult, DescribeRuleResult, ServeResult
    ],
    display: DisplayOptions,
    exits: __.ctxl.AsyncExitStack,
) -> None:
    ''' Renders and prints a result object based on display options.

        Follows the pattern from librovore for centralized rendering dispatch.
    '''
    stream = await display.provide_stream( exits )
    match display.format:
        case OutputFormats.Json:
            import json
            stream.write( json.dumps( result.render_as_json( ) ) )
            stream.write( '\n' )
        case OutputFormats.Text:
            for line in result.render_as_text( ):
                stream.write( line )
                stream.write( '\n' )


class CheckCommand( __.immut.DataclassObject ):
    ''' Analyzes code and reports violations. '''

    paths: PathsArgument = ( '.',)
    select: __.Absential[ RuleSelectorArgument ] = __.absent
    display: __.typx.Annotated[
        DisplayOptions,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = DisplayOptions )
    jobs: __.typx.Annotated[
        __.typx.Union[ int, __.typx.Literal[ 'auto' ] ],
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Number of parallel processing jobs. ''' )
    ] = 'auto'

    async def __call__( self ) -> int:
        ''' Executes the check command. '''
        result = CheckResult(
            paths = self.paths,
            context_lines = self.display.context,
            jobs = self.jobs,
            rule_selection = self.select,
        )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, self.display, exits )
        return 0


class FixCommand( __.immut.DataclassObject ):
    ''' Applies automated fixes with safety controls. '''

    paths: PathsArgument = ( '.',)
    select: __.Absential[ RuleSelectorArgument ] = __.absent
    display: __.typx.Annotated[
        DisplayOptions,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = DisplayOptions )
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

    async def __call__( self ) -> int:
        ''' Executes the fix command. '''
        result = FixResult(
            paths = self.paths,
            simulate = self.simulate,
            diff_format = self.diff_format.value,
            apply_dangerous = self.apply_dangerous,
            rule_selection = self.select,
        )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, self.display, exits )
        return 0


class ConfigureCommand( __.immut.DataclassObject ):
    ''' Manages configuration without destructive file editing. '''

    display: __.typx.Annotated[
        DisplayOptions,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = DisplayOptions )
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

    async def __call__( self ) -> int:
        ''' Executes the configure command. '''
        result = ConfigureResult(
            validate = self.validate,
            interactive = self.interactive,
            display_effective = self.display_effective,
        )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, self.display, exits )
        return 0


class DescribeRulesCommand( __.immut.DataclassObject ):
    ''' Lists all available rules with descriptions. '''

    display: __.typx.Annotated[
        DisplayOptions,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = DisplayOptions )
    details: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc(
            ''' Display detailed rule information including '''
            ''' configuration status. ''' )
    ] = False

    async def __call__( self ) -> int:
        ''' Executes the describe rules command. '''
        result = DescribeRulesResult( details = self.details )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, self.display, exits )
        return 0


class DescribeRuleCommand( __.immut.DataclassObject ):
    ''' Displays detailed information for a specific rule. '''

    rule_id: __.tyro.conf.Positional[ str ]
    display: __.typx.Annotated[
        DisplayOptions,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = DisplayOptions )
    details: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc(
            ''' Display detailed rule information including '''
            ''' configuration status. ''' )
    ] = False

    async def __call__( self ) -> int:
        ''' Executes the describe rule command. '''
        result = DescribeRuleResult(
            rule_id = self.rule_id,
            details = self.details,
        )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, self.display, exits )
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

    async def __call__( self ) -> int:
        ''' Delegates to selected subcommand. '''
        return await self.subcommand( )


class ServeCommand( __.immut.DataclassObject ):
    ''' Starts a protocol server (future implementation). '''

    display: __.typx.Annotated[
        DisplayOptions,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = DisplayOptions )
    protocol: __.typx.Annotated[
        __.typx.Literal[ 'lsp', 'mcp' ],
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Protocol server to start. ''' )
    ] = 'mcp'

    async def __call__( self ) -> int:
        ''' Executes the serve command. '''
        result = ServeResult( protocol = self.protocol )
        async with __.ctxl.AsyncExitStack( ) as exits:
            await _render_and_print_result( result, self.display, exits )
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
    verbose: __.typx.Annotated[
        bool,
        __.ddoc.Doc( ''' Enable verbose output. ''' )
    ] = False

    async def __call__( self ) -> None:
        ''' Invokes selected subcommand after system preparation. '''
        # TODO: Implement verbose logging setup
        exit_code = await self.command( )
        raise SystemExit( exit_code )


def execute( ) -> None:
    ''' Entrypoint for CLI execution. '''
    from asyncio import run
    config = (
        __.tyro.conf.EnumChoicesFromValues,
        __.tyro.conf.HelptextFromCommentsOff,
    )
    try:
        run( __.tyro.cli( Cli, config = config )( ) ) # pyright: ignore
    except SystemExit:
        raise
    except BaseException:
        # TODO: Log exception with proper error handling
        raise SystemExit( 1 ) from None
