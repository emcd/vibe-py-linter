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


from . import __


class DiffFormats( __.enum.Enum ):
    ''' Diff visualization formats. '''

    Unified = 'unified'
    Context = 'context'


class OutputFormats( __.enum.Enum ):
    ''' Output formats for reporting. '''

    Text = 'text'
    Json = 'json'
    Structured = 'structured'


class TargetStreams( __.enum.Enum ):
    ''' Standard output streams. '''

    Stdout = 'stdout'
    Stderr = 'stderr'


class DisplayOptions( __.immut.DataclassObject ):
    ''' Display and output options for CLI commands.

        Provides standardized handling of output streams, formats,
        and terminal capabilities following appcore.cli patterns.
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
    colorize: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Enable colored output and terminal formatting. ''' )
    ] = True
    target_stream: __.typx.Annotated[
        TargetStreams,
        __.tyro.conf.arg( prefix_name = False ),
        __.ddoc.Doc( ''' Render output on stdout or stderr. ''' )
    ] = TargetStreams.Stdout

    def determine_colorization( self, stream: __.typx.TextIO ) -> bool:
        ''' Determines whether colorized output should be used.

            Respects NO_COLOR environment variable and TTY capabilities.
        '''
        if not self.colorize:
            return False
        if 'NO_COLOR' in __.os.environ:
            return False
        return hasattr( stream, 'isatty' ) and stream.isatty( )

    @__.contextlib.asynccontextmanager
    async def provide_stream(
        self,
        _exits: __.typx.Any = None
    ) -> __.cabc.AsyncIterator[ __.typx.TextIO ]:
        ''' Provides the appropriate output stream.

            Yields stdout or stderr based on target_stream setting.
        '''
        match self.target_stream:
            case TargetStreams.Stdout:
                yield __.sys.stdout
            case TargetStreams.Stderr:
                yield __.sys.stderr


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


async def _render_result(
    display: DisplayOptions,
    data: dict[ str, __.typx.Any ],
) -> None:
    ''' Centralizes output rendering logic across all commands.

        Dispatches to format-specific renderers based on display options.
        This prevents duplication of match/case statements in each command.
    '''
    async with display.provide_stream( ) as stream:
        match display.format:
            case OutputFormats.Json:
                import json
                stream.write( json.dumps( data ) )
                stream.write( '\n' )
            case OutputFormats.Structured:
                # TODO: Implement structured output
                stream.write( 'Structured output placeholder\n' )
                for key, value in data.items( ):
                    stream.write( f"  {key}: {value}\n" )
            case OutputFormats.Text:
                for key, value in data.items( ):
                    if key == '_title':
                        stream.write( f"{value}\n" )
                    else:
                        stream.write( f"  {key}: {value}\n" )


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
        data: dict[ str, __.typx.Any ] = {
            '_title': f'Checking paths: {self.paths}',
            'Context lines': self.display.context,
            'Jobs': self.jobs,
        }
        if not __.is_absent( self.select ):
            data[ 'Rule selection' ] = self.select
        await _render_result( self.display, data )
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
        data: dict[ str, __.typx.Any ] = {
            '_title': f'Fixing paths: {self.paths}',
            'Simulate': self.simulate,
            'Diff format': self.diff_format.value,
            'Apply dangerous': self.apply_dangerous,
        }
        if not __.is_absent( self.select ):
            data[ 'Rule selection' ] = self.select
        await _render_result( self.display, data )
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
        data: dict[ str, __.typx.Any ] = {
            '_title': 'Configure command',
            'Validate': self.validate,
            'Interactive': self.interactive,
            'Display effective': self.display_effective,
        }
        await _render_result( self.display, data )
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
        data: dict[ str, __.typx.Any ] = {
            '_title': 'Available rules',
            'Details': self.details,
        }
        await _render_result( self.display, data )
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
        data: dict[ str, __.typx.Any ] = {
            '_title': f'Rule: {self.rule_id}',
            'Details': self.details,
        }
        await _render_result( self.display, data )
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
        data = {
            '_title': f'Protocol server: {self.protocol}',
            'Status': '(Not yet implemented)',
        }
        await _render_result( self.display, data )
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
