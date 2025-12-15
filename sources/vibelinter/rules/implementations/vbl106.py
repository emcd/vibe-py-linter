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


''' VBL106: Enforce single-line body compaction.

    Category: Readability
    Subcategory: Formatting

    Enforces single-line form for simple control flow bodies.
    For example, an if statement with a single short statement like
    ``if not data: return None`` instead of multi-line form.

    Bodies that are too long or contain multiple statements are
    not flagged.
'''


from . import __


# Default threshold for single-line form (percentage of max line length)
SINGLE_LINE_THRESHOLD_RATIO = 0.70
MAX_LINE_LENGTH = 79


class _SingleLineBodyTransformer( __.libcst.CSTTransformer ):
    ''' Transforms CST to compact simple bodies to single line. '''

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

    def _make_simple_body(
        self, stmt: __.libcst.BaseStatement
    ) -> __.libcst.SimpleStatementSuite:
        ''' Converts a statement to simple statement suite. '''
        if isinstance( stmt, __.libcst.SimpleStatementLine ):
            return __.libcst.SimpleStatementSuite(
                body = stmt.body,
                leading_whitespace = __.libcst.SimpleWhitespace( ' ' ),
            )
        return __.libcst.SimpleStatementSuite(
            body = [ ],
            leading_whitespace = __.libcst.SimpleWhitespace( ' ' ),
        )

    def leave_If(
        self,
        original_node: __.libcst.If,
        updated_node: __.libcst.If
    ) -> __.libcst.If:
        ''' Transforms if statement to single-line form. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        body = updated_node.body
        is_indented = isinstance( body, __.libcst.IndentedBlock )
        if is_indented and len( body.body ) == 1:
            stmt = body.body[ 0 ]
            new_body = self._make_simple_body( stmt )
            return updated_node.with_changes( body = new_body )
        return updated_node

    def leave_For(
        self,
        original_node: __.libcst.For,
        updated_node: __.libcst.For
    ) -> __.libcst.For:
        ''' Transforms for loop to single-line form. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        body = updated_node.body
        is_indented = isinstance( body, __.libcst.IndentedBlock )
        if is_indented and len( body.body ) == 1:
            stmt = body.body[ 0 ]
            new_body = self._make_simple_body( stmt )
            return updated_node.with_changes( body = new_body )
        return updated_node

    def leave_While(
        self,
        original_node: __.libcst.While,
        updated_node: __.libcst.While
    ) -> __.libcst.While:
        ''' Transforms while loop to single-line form. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        body = updated_node.body
        is_indented = isinstance( body, __.libcst.IndentedBlock )
        if is_indented and len( body.body ) == 1:
            stmt = body.body[ 0 ]
            new_body = self._make_simple_body( stmt )
            return updated_node.with_changes( body = new_body )
        return updated_node

    def leave_With(
        self,
        original_node: __.libcst.With,
        updated_node: __.libcst.With
    ) -> __.libcst.With:
        ''' Transforms with statement to single-line form. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        body = updated_node.body
        is_indented = isinstance( body, __.libcst.IndentedBlock )
        if is_indented and len( body.body ) == 1:
            stmt = body.body[ 0 ]
            new_body = self._make_simple_body( stmt )
            return updated_node.with_changes( body = new_body )
        return updated_node


class VBL106( __.FixableRule ):
    ''' Enforces single-line body compaction for simple control flow. '''

    METADATA_DEPENDENCIES = (
        __.libcst.metadata.PositionProvider,
        __.libcst.metadata.ScopeProvider,
        __.libcst.metadata.QualifiedNameProvider,
        __.libcst.metadata.ParentNodeProvider,
    )

    @property
    def rule_id( self ) -> str:
        return 'VBL106'

    def __init__(
        self,
        filename: str,
        wrapper: __.libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ],
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )
        self._violations_to_fix: list[
            tuple[ __.libcst.CSTNode, str, int, int ] ] = [ ]
        self._threshold = int(
            MAX_LINE_LENGTH * SINGLE_LINE_THRESHOLD_RATIO )

    def _is_simple_body(
        self, body: __.libcst.BaseSuite
    ) -> bool:
        ''' Checks if body is a simple single-statement suite. '''
        if isinstance( body, __.libcst.SimpleStatementSuite ):
            return False  # Already single-line
        if isinstance( body, __.libcst.IndentedBlock ):
            if len( body.body ) != 1:
                return False
            stmt = body.body[ 0 ]
            return isinstance( stmt, __.libcst.SimpleStatementLine )
        return False

    def _estimate_single_line_length(
        self,
        header_code: str,
        body: __.libcst.BaseSuite
    ) -> int:
        ''' Estimates length if converted to single line. '''
        if not isinstance( body, __.libcst.IndentedBlock ):
            return 999
        if len( body.body ) != 1:
            return 999
        stmt = body.body[ 0 ]
        if not isinstance( stmt, __.libcst.SimpleStatementLine ):
            return 999
        body_code = __.libcst.Module( body = [ stmt ] ).code.strip( )
        # header + colon + space + body
        return len( header_code ) + len( body_code )

    def _get_header_code(
        self, node: __.libcst.CSTNode, node_type: str
    ) -> str:
        ''' Extracts header portion (before body) of control statement. '''
        line, _ = self._position_from_node( node )
        if 1 <= line <= len( self.source_lines ):
            header = self.source_lines[ line - 1 ].strip( )
            # Remove trailing colon if present
            if header.endswith( ':' ):
                header = header[ :-1 ]
            return header
        return node_type

    def _check_single_line_potential(
        self,
        node: __.libcst.CSTNode,
        body: __.libcst.BaseSuite,
        node_type: str
    ) -> None:
        ''' Checks if body could be compacted to single line. '''
        if not self._is_simple_body( body ):
            return
        header = self._get_header_code( node, node_type )
        estimated_length = self._estimate_single_line_length( header, body )
        if estimated_length > self._threshold:
            return
        # Check that body doesn't contain nested control flow
        if isinstance( body, __.libcst.IndentedBlock ):
            stmt = body.body[ 0 ]
            if isinstance( stmt, __.libcst.SimpleStatementLine ):
                for small_stmt in stmt.body:
                    # Don't compact if it has complex elements
                    if isinstance(
                        small_stmt,
                        ( __.libcst.Assert, __.libcst.Global,
                          __.libcst.Nonlocal )
                    ):
                        return
        line, column = self._position_from_node( node )
        self._violations_to_fix.append( (
            node,
            f"Simple {node_type} body can be written on single line.",
            line,
            column
        ) )

    def visit_If( self, node: __.libcst.If ) -> bool:
        ''' Checks if statement for single-line potential. '''
        # Only check main if, not elif (handled separately)
        # Skip if there's an else/elif clause
        if node.orelse is not None:
            return True
        self._check_single_line_potential( node, node.body, 'if' )
        return True

    def visit_For( self, node: __.libcst.For ) -> bool:
        ''' Checks for loop for single-line potential. '''
        if node.orelse is not None:
            return True
        self._check_single_line_potential( node, node.body, 'for' )
        return True

    def visit_While( self, node: __.libcst.While ) -> bool:
        ''' Checks while loop for single-line potential. '''
        if node.orelse is not None:
            return True
        self._check_single_line_potential( node, node.body, 'while' )
        return True

    def visit_With( self, node: __.libcst.With ) -> bool:
        ''' Checks with statement for single-line potential. '''
        self._check_single_line_potential( node, node.body, 'with' )
        return True

    def visit_Try( self, node: __.libcst.Try ) -> bool:
        ''' Checks try block for single-line potential. '''
        self._check_single_line_potential( node, node.body, 'try' )
        return True

    def _analyze_collections( self ) -> None:
        ''' Generates violations and fixes from collected data. '''
        for node, message, line, column in self._violations_to_fix:
            self._produce_violation( node, message, severity = 'warning' )
            violation = self._violations[ -1 ]
            target_line = line
            target_column = column

            def make_transformer(
                tl: int, tc: int
            ) -> __.cabc.Callable[
                [ __.libcst.Module ], __.libcst.Module
            ]:
                def transform( module: __.libcst.Module ) -> __.libcst.Module:
                    wrapper = __.libcst.metadata.MetadataWrapper( module )
                    transformer = _SingleLineBodyTransformer( tl, tc )
                    return wrapper.visit( transformer )
                return transform

            self._produce_fix(
                violation = violation,
                description = "Compact to single-line form.",
                transformer_factory = make_transformer(
                    target_line, target_column ),
                safety = __.FixSafety.Safe,
            )


# Self-register this rule
__.RULE_DESCRIPTORS[ 'VBL106' ] = __.RuleDescriptor(
    vbl_code = 'VBL106',
    descriptive_name = 'single-line-body',
    description = 'Enforces single-line form for simple control flow bodies.',
    category = 'readability',
    subcategory = 'formatting',
    rule_class = VBL106,
    violation_message = 'Simple body can be single line',
    examples = (
        '# Violation\n'
        'if not data:\n'
        '    return None\n'
        '\n'
        '# Fix\n'
        'if not data: return None'
    )
)
