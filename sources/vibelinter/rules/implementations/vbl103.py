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


''' VBL103: Enforce bracket spacing.

    Category: Readability
    Subcategory: Formatting

    Enforces one space after opening delimiters (``(``, ``[``, ``{``)
    and one space before closing delimiters (``)``, ``]``, ``}``).
    Empty delimiters should have a single space: ``( )``, ``[ ]``, ``{ }``.

    F-string expressions are exempt from this rule.
'''


from . import __


class _BracketSpacingTransformer( __.libcst.CSTTransformer ):
    ''' Transforms CST to add proper bracket spacing. '''

    METADATA_DEPENDENCIES = (
        __.libcst.metadata.PositionProvider,
    )

    def __init__(
        self,
        target_line: int,
        target_column: int,
    ) -> None:
        super( ).__init__( )
        self.target_line = target_line
        self.target_column = target_column

    def _get_position(
        self, node: __.libcst.CSTNode
    ) -> tuple[ int, int ] | None:
        ''' Gets position of node if available. '''
        try:
            pos = self.get_metadata(
                __.libcst.metadata.PositionProvider, node )
            code_range = __.typx.cast(
                __.libcst.metadata.CodeRange, pos )
            return ( code_range.start.line, code_range.start.column + 1 )
        except KeyError:
            return None

    def _ensure_space_after_open(
        self,
        whitespace: __.libcst.BaseParenthesizableWhitespace
    ) -> __.libcst.BaseParenthesizableWhitespace:
        ''' Ensures at least one space after opening delimiter. '''
        if (
            isinstance( whitespace, __.libcst.SimpleWhitespace )
            and whitespace.value == ''
        ):
            return __.libcst.SimpleWhitespace( ' ' )
        return whitespace

    def _ensure_space_before_close(
        self,
        whitespace: __.libcst.BaseParenthesizableWhitespace
    ) -> __.libcst.BaseParenthesizableWhitespace:
        ''' Ensures at least one space before closing delimiter. '''
        if (
            isinstance( whitespace, __.libcst.SimpleWhitespace )
            and whitespace.value == ''
        ):
            return __.libcst.SimpleWhitespace( ' ' )
        return whitespace

    def leave_Arg(
        self,
        original_node: __.libcst.Arg,
        updated_node: __.libcst.Arg
    ) -> __.libcst.Arg:
        ''' Handles function call arguments. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        # Add space in whitespace_after_arg if it's a trailing arg
        return updated_node

    def leave_Tuple(
        self,
        original_node: __.libcst.Tuple,
        updated_node: __.libcst.Tuple
    ) -> __.libcst.Tuple:
        ''' Handles tuple literals. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        if updated_node.lpar and updated_node.rpar:
            new_lpar: list[ __.libcst.LeftParen ] = [ ]
            for lp in updated_node.lpar:
                new_lp = lp.with_changes(
                    whitespace_after = self._ensure_space_after_open(
                        lp.whitespace_after
                    )
                )
                new_lpar.append( new_lp )
            new_rpar: list[ __.libcst.RightParen ] = [ ]
            for rp in updated_node.rpar:
                new_rp = rp.with_changes(
                    whitespace_before = self._ensure_space_before_close(
                        rp.whitespace_before
                    )
                )
                new_rpar.append( new_rp )
            return updated_node.with_changes(
                lpar = new_lpar, rpar = new_rpar )
        return updated_node

    def leave_List(
        self,
        original_node: __.libcst.List,
        updated_node: __.libcst.List
    ) -> __.libcst.List:
        ''' Handles list literals. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        new_lbracket = updated_node.lbracket.with_changes(
            whitespace_after = self._ensure_space_after_open(
                updated_node.lbracket.whitespace_after
            )
        )
        new_rbracket = updated_node.rbracket.with_changes(
            whitespace_before = self._ensure_space_before_close(
                updated_node.rbracket.whitespace_before
            )
        )
        return updated_node.with_changes(
            lbracket = new_lbracket, rbracket = new_rbracket )

    def leave_Dict(
        self,
        original_node: __.libcst.Dict,
        updated_node: __.libcst.Dict
    ) -> __.libcst.Dict:
        ''' Handles dict literals. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        new_lbrace = updated_node.lbrace.with_changes(
            whitespace_after = self._ensure_space_after_open(
                updated_node.lbrace.whitespace_after
            )
        )
        new_rbrace = updated_node.rbrace.with_changes(
            whitespace_before = self._ensure_space_before_close(
                updated_node.rbrace.whitespace_before
            )
        )
        return updated_node.with_changes(
            lbrace = new_lbrace, rbrace = new_rbrace )

    def leave_Set(
        self,
        original_node: __.libcst.Set,
        updated_node: __.libcst.Set
    ) -> __.libcst.Set:
        ''' Handles set literals. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        new_lbrace = updated_node.lbrace.with_changes(
            whitespace_after = self._ensure_space_after_open(
                updated_node.lbrace.whitespace_after
            )
        )
        new_rbrace = updated_node.rbrace.with_changes(
            whitespace_before = self._ensure_space_before_close(
                updated_node.rbrace.whitespace_before
            )
        )
        return updated_node.with_changes(
            lbrace = new_lbrace, rbrace = new_rbrace )

    def leave_Call(
        self,
        original_node: __.libcst.Call,
        updated_node: __.libcst.Call
    ) -> __.libcst.Call:
        ''' Handles function calls. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        # Handle whitespace after opening paren
        new_lpar: list[ __.libcst.LeftParen ] = [ ]
        for lp in updated_node.lpar:
            new_lp = lp.with_changes(
                whitespace_after = self._ensure_space_after_open(
                    lp.whitespace_after
                )
            )
            new_lpar.append( new_lp )
        # Handle whitespace before closing paren
        new_rpar: list[ __.libcst.RightParen ] = [ ]
        for rp in updated_node.rpar:
            new_rp = rp.with_changes(
                whitespace_before = self._ensure_space_before_close(
                    rp.whitespace_before
                )
            )
            new_rpar.append( new_rp )
        return updated_node.with_changes( lpar = new_lpar, rpar = new_rpar )


class VBL103( __.FixableRule ):
    ''' Enforces bracket spacing conventions. '''

    METADATA_DEPENDENCIES = (
        __.libcst.metadata.PositionProvider,
        __.libcst.metadata.ScopeProvider,
        __.libcst.metadata.QualifiedNameProvider,
        __.libcst.metadata.ParentNodeProvider,
    )

    @property
    def rule_id( self ) -> str:
        return 'VBL103'

    def __init__(
        self,
        filename: str,
        wrapper: __.libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ],
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )
        self._violations_to_fix: list[
            tuple[ __.libcst.CSTNode, str, int, int ] ] = [ ]
        self._in_fstring: int = 0

    def visit_FormattedString( self, node: __.libcst.FormattedString ) -> bool:
        ''' Tracks entry into f-string. '''
        _ = node
        self._in_fstring += 1
        return True

    def leave_FormattedString(
        self, original_node: __.libcst.FormattedString
    ) -> None:
        ''' Tracks exit from f-string. '''
        _ = original_node
        self._in_fstring -= 1

    def _check_paren_spacing(
        self,
        node: __.libcst.CSTNode,
        lpar: __.cabc.Sequence[ __.libcst.LeftParen ],
        rpar: __.cabc.Sequence[ __.libcst.RightParen ],
        has_content: bool
    ) -> None:
        ''' Checks spacing for parentheses. '''
        if self._in_fstring > 0:
            return
        for lp in lpar:
            ws = lp.whitespace_after
            if isinstance( ws, __.libcst.SimpleWhitespace ):
                if ws.value == '' and has_content:
                    self._record_violation(
                        node, "Missing space after opening parenthesis." )
                elif ws.value == '' and not has_content:
                    self._record_violation(
                        node, "Empty parentheses should be '( )'." )

    def _check_bracket_spacing(
        self,
        node: __.libcst.CSTNode,
        lbracket: __.libcst.LeftSquareBracket,
        rbracket: __.libcst.RightSquareBracket,
        has_content: bool
    ) -> None:
        ''' Checks spacing for square brackets. '''
        if self._in_fstring > 0:
            return
        ws_after = lbracket.whitespace_after
        if isinstance( ws_after, __.libcst.SimpleWhitespace ):
            if ws_after.value == '' and has_content:
                self._record_violation(
                    node, "Missing space after opening bracket." )
            elif ws_after.value == '' and not has_content:
                self._record_violation(
                    node, "Empty brackets should be '[ ]'." )

    def _check_brace_spacing(
        self,
        node: __.libcst.CSTNode,
        lbrace: __.libcst.LeftCurlyBrace,
        rbrace: __.libcst.RightCurlyBrace,
        has_content: bool
    ) -> None:
        ''' Checks spacing for curly braces. '''
        if self._in_fstring > 0:
            return
        ws_after = lbrace.whitespace_after
        if isinstance( ws_after, __.libcst.SimpleWhitespace ):
            if ws_after.value == '' and has_content:
                self._record_violation(
                    node, "Missing space after opening brace." )
            elif ws_after.value == '' and not has_content:
                self._record_violation(
                    node, "Empty braces should be '{ }'." )

    def _record_violation(
        self, node: __.libcst.CSTNode, message: str
    ) -> None:
        ''' Records a violation for later processing. '''
        line, column = self._position_from_node( node )
        self._violations_to_fix.append( ( node, message, line, column ) )

    def visit_Call( self, node: __.libcst.Call ) -> bool:
        ''' Checks function call bracket spacing. '''
        has_args = len( node.args ) > 0
        self._check_paren_spacing( node, node.lpar, node.rpar, has_args )
        return True

    def visit_Tuple( self, node: __.libcst.Tuple ) -> bool:
        ''' Checks tuple bracket spacing. '''
        if node.lpar and node.rpar:
            has_elements = len( node.elements ) > 0
            self._check_paren_spacing(
                node, node.lpar, node.rpar, has_elements )
        return True

    def visit_List( self, node: __.libcst.List ) -> bool:
        ''' Checks list bracket spacing. '''
        has_elements = len( node.elements ) > 0
        self._check_bracket_spacing(
            node, node.lbracket, node.rbracket, has_elements )
        return True

    def visit_Dict( self, node: __.libcst.Dict ) -> bool:
        ''' Checks dict brace spacing. '''
        has_elements = len( node.elements ) > 0
        self._check_brace_spacing(
            node, node.lbrace, node.rbrace, has_elements )
        return True

    def visit_Set( self, node: __.libcst.Set ) -> bool:
        ''' Checks set brace spacing. '''
        has_elements = len( node.elements ) > 0
        self._check_brace_spacing(
            node, node.lbrace, node.rbrace, has_elements )
        return True

    def _analyze_collections( self ) -> None:
        ''' Generates violations and fixes from collected data. '''
        for node, message, line, column in self._violations_to_fix:
            self._produce_violation( node, message, severity = 'warning' )
            violation = self._violations[ -1 ]
            # Create transformer factory for this specific violation
            target_line = line
            target_column = column

            def make_transformer(
                tl: int, tc: int
            ) -> __.cabc.Callable[
                [ __.libcst.Module ], __.libcst.Module
            ]:
                def transform( module: __.libcst.Module ) -> __.libcst.Module:
                    wrapper = __.libcst.metadata.MetadataWrapper( module )
                    transformer = _BracketSpacingTransformer( tl, tc )
                    return wrapper.visit( transformer )
                return transform

            self._produce_fix(
                violation = violation,
                description = "Add proper bracket spacing.",
                transformer_factory = make_transformer(
                    target_line, target_column ),
                safety = __.FixSafety.Safe,
            )


# Self-register this rule
__.RULE_DESCRIPTORS[ 'VBL103' ] = __.RuleDescriptor(
    vbl_code = 'VBL103',
    descriptive_name = 'bracket-spacing',
    description = 'Enforces spaces inside parentheses, brackets, and braces.',
    category = 'readability',
    subcategory = 'formatting',
    rule_class = VBL103,
    violation_message = 'Missing bracket spacing',
    examples = (
        '# Violation\n'
        'func(arg)\n'
        'data = [1, 2, 3]\n'
        '\n'
        '# Fix\n'
        'func( arg )\n'
        'data = [ 1, 2, 3 ]'
    )
)
