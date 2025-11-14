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


# Type aliases for CLI parameters
OutputFormat: __.typx.TypeAlias = (
    __.typx.Literal[ 'text', 'json', 'structured' ] )
DiffFormat: __.typx.TypeAlias = (
    __.typx.Literal[ 'unified', 'context' ] )
RuleSelectorArgument: __.typx.TypeAlias = __.typx.Annotated[
    str,
    __.ddoc.Doc( "Comma-separated VBL rule codes (e.g. VBL101,VBL201)." )
]
PathsArgument: __.typx.TypeAlias = __.typx.Annotated[
    tuple[ str, ... ],
    __.ddoc.Doc( "Files or directories to analyze." )
]


class CheckCommand( __.immut.DataclassObject ):
    ''' Analyzes code and reports violations. '''

    paths: PathsArgument = ( '.',)
    select: __.Absential[ RuleSelectorArgument ] = __.absent
    report_format: __.typx.Annotated[
        OutputFormat,
        __.ddoc.Doc( "Output format for violation reporting." )
    ] = 'text'
    context: __.typx.Annotated[
        int,
        __.ddoc.Doc( "Show context lines around violations." )
    ] = 0
    jobs: __.typx.Annotated[
        __.typx.Union[ int, __.typx.Literal[ 'auto' ] ],
        __.ddoc.Doc( "Number of parallel processing jobs." )
    ] = 'auto'

    async def __call__( self ) -> int:
        ''' Executes the check command. '''
        print( f"Check command called with paths: {self.paths}" )
        if not __.is_absent( self.select ):
            print( f"  Rule selection: {self.select}" )
        print( f"  Report format: {self.report_format}" )
        print( f"  Context lines: {self.context}" )
        print( f"  Jobs: {self.jobs}" )
        return 0


class FixCommand( __.immut.DataclassObject ):
    ''' Applies automated fixes with safety controls. '''

    paths: PathsArgument = ( '.',)
    select: __.Absential[ RuleSelectorArgument ] = __.absent
    simulate: __.typx.Annotated[
        bool,
        __.ddoc.Doc( "Preview changes without applying them." )
    ] = False
    diff_format: __.typx.Annotated[
        DiffFormat,
        __.ddoc.Doc( "Diff visualization format." )
    ] = 'unified'
    apply_dangerous: __.typx.Annotated[
        bool,
        __.ddoc.Doc( "Enable potentially unsafe fixes." )
    ] = False

    async def __call__( self ) -> int:
        ''' Executes the fix command. '''
        print( f"Fix command called with paths: {self.paths}" )
        if not __.is_absent( self.select ):
            print( f"  Rule selection: {self.select}" )
        print( f"  Simulate: {self.simulate}" )
        print( f"  Diff format: {self.diff_format}" )
        print( f"  Apply dangerous: {self.apply_dangerous}" )
        return 0


class ConfigureCommand( __.immut.DataclassObject ):
    ''' Manages configuration without destructive file editing. '''

    validate: __.typx.Annotated[
        bool,
        __.ddoc.Doc( "Validate existing configuration without analysis." )
    ] = False
    interactive: __.typx.Annotated[
        bool,
        __.ddoc.Doc( "Interactive configuration wizard." )
    ] = False
    display_effective: __.typx.Annotated[
        bool,
        __.ddoc.Doc( "Display effective merged configuration." )
    ] = False

    async def __call__( self ) -> int:
        ''' Executes the configure command. '''
        print( "Configure command called" )
        print( f"  Validate: {self.validate}" )
        print( f"  Interactive: {self.interactive}" )
        print( f"  Display effective: {self.display_effective}" )
        return 0


class DescribeRulesCommand( __.immut.DataclassObject ):
    ''' Lists all available rules with descriptions. '''

    details: __.typx.Annotated[
        bool,
        __.ddoc.Doc(
            "Display detailed rule information including "
            "configuration status." )
    ] = False

    async def __call__( self ) -> int:
        ''' Executes the describe rules command. '''
        print( "Describe rules command called" )
        print( f"  Details: {self.details}" )
        return 0


class DescribeRuleCommand( __.immut.DataclassObject ):
    ''' Displays detailed information for a specific rule. '''

    rule_id: __.tyro.conf.Positional[ str ]
    details: __.typx.Annotated[
        bool,
        __.ddoc.Doc(
            "Display detailed rule information including "
            "configuration status." )
    ] = False

    async def __call__( self ) -> int:
        ''' Executes the describe rule command. '''
        print( f"Describe rule command called for: {self.rule_id}" )
        print( f"  Details: {self.details}" )
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

    protocol: __.typx.Annotated[
        __.typx.Literal[ 'lsp', 'mcp' ],
        __.ddoc.Doc( "Protocol server to start." )
    ] = 'mcp'

    async def __call__( self ) -> int:
        ''' Executes the serve command. '''
        print( f"Serve command called with protocol: {self.protocol}" )
        print( "  (Not yet implemented)" )
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
        __.ddoc.Doc( "Enable verbose output." )
    ] = False

    async def __call__( self ) -> None:
        ''' Invokes selected subcommand after system preparation. '''
        if self.verbose:
            print( "Verbose mode enabled" )
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
