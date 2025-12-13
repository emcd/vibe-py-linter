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


''' VBL104: Enforce keyword argument spacing.

    Category: Readability
    Subcategory: Formatting

    Enforces spaces around ``=`` in keyword arguments and default
    parameter values. For example, ``func(arg=value)`` should be
    ``func( arg = value )`` and ``def func(param=default)`` should
    be ``def func( param = default )``.
'''


from . import __


class _KeywordSpacingTransformer( __.libcst.CSTTransformer ):
    ''' Transforms CST to add proper keyword argument spacing. '''

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

    def _ensure_space( self ) -> __.libcst.SimpleWhitespace:
        ''' Returns a single space whitespace node. '''
        return __.libcst.SimpleWhitespace( ' ' )

    def leave_Arg(
        self,
        original_node: __.libcst.Arg,
        updated_node: __.libcst.Arg
    ) -> __.libcst.Arg:
        ''' Handles function call arguments. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        if updated_node.keyword is None:
            return updated_node
        if isinstance( updated_node.equal, __.libcst.MaybeSentinel ):
            return updated_node
        # Add spaces around the equal sign
        new_equal = updated_node.equal.with_changes(
            whitespace_before = self._ensure_space( ),
            whitespace_after = self._ensure_space( ),
        )
        return updated_node.with_changes( equal = new_equal )

    def leave_Param(
        self,
        original_node: __.libcst.Param,
        updated_node: __.libcst.Param
    ) -> __.libcst.Param:
        ''' Handles function parameter defaults. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        if updated_node.default is None:
            return updated_node
        if isinstance( updated_node.equal, __.libcst.MaybeSentinel ):
            return updated_node
        # Add spaces around the equal sign
        new_equal = updated_node.equal.with_changes(
            whitespace_before = self._ensure_space( ),
            whitespace_after = self._ensure_space( ),
        )
        return updated_node.with_changes( equal = new_equal )


class VBL104( __.FixableRule ):
    ''' Enforces keyword argument spacing conventions. '''

    METADATA_DEPENDENCIES = (
        __.libcst.metadata.PositionProvider,
        __.libcst.metadata.ScopeProvider,
        __.libcst.metadata.QualifiedNameProvider,
        __.libcst.metadata.ParentNodeProvider,
    )

    @property
    def rule_id( self ) -> str:
        return 'VBL104'

    def __init__(
        self,
        filename: str,
        wrapper: __.libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ],
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )
        self._violations_to_fix: list[
            tuple[ __.libcst.CSTNode, str, int, int ] ] = [ ]

    def _whitespace_needs_fix(
        self,
        ws: __.libcst.BaseParenthesizableWhitespace,
    ) -> bool:
        ''' Checks if whitespace is not a single space. '''
        if isinstance( ws, __.libcst.SimpleWhitespace ):
            return ws.value != ' '
        return False

    def _check_equal_spacing(
        self,
        node: __.libcst.CSTNode,
        equal: __.libcst.AssignEqual | __.libcst.MaybeSentinel,
        context: str
    ) -> None:
        ''' Checks spacing around an equals sign. '''
        if isinstance( equal, __.libcst.MaybeSentinel ):
            return
        ws_before = equal.whitespace_before
        ws_after = equal.whitespace_after
        needs_fix = self._whitespace_needs_fix(
            ws_before ) or self._whitespace_needs_fix( ws_after )
        if needs_fix:
            line, column = self._position_from_node( node )
            self._violations_to_fix.append( (
                node,
                f"Missing spaces around '=' in {context}.",
                line,
                column
            ) )

    def visit_Arg( self, node: __.libcst.Arg ) -> bool:
        ''' Checks keyword argument spacing. '''
        if node.keyword is not None:
            self._check_equal_spacing(
                node, node.equal, 'keyword argument' )
        return True

    def visit_Param( self, node: __.libcst.Param ) -> bool:
        ''' Checks default parameter spacing. '''
        if node.default is not None:
            self._check_equal_spacing(
                node, node.equal, 'default parameter' )
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
                    transformer = _KeywordSpacingTransformer( tl, tc )
                    return wrapper.visit( transformer )
                return transform

            self._produce_fix(
                violation = violation,
                description = "Add spaces around '=' sign.",
                transformer_factory = make_transformer(
                    target_line, target_column ),
                safety = __.FixSafety.Safe,
            )


# Self-register this rule
__.RULE_DESCRIPTORS[ 'VBL104' ] = __.RuleDescriptor(
    vbl_code = 'VBL104',
    descriptive_name = 'keyword-argument-spacing',
    description = 'Enforces spaces around = in keyword arguments.',
    category = 'readability',
    subcategory = 'formatting',
    rule_class = VBL104,
    violation_message = 'Missing keyword argument spacing',
    examples = (
        '# Violation\n'
        'func(arg=value)\n'
        'def foo(param=default):\n'
        '\n'
        '# Fix\n'
        'func( arg = value )\n'
        'def foo( param = default ):'
    )
)
