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


''' VBL107: Enforce trailing comma in multi-line collections.

    Category: Readability
    Subcategory: Formatting

    Enforces trailing commas in multi-line collection literals
    (lists, dicts, sets, tuples). Function call arguments are
    exempt from this rule per project style guide.
'''


from . import __


class _TrailingCommaTransformer( __.libcst.CSTTransformer ):
    ''' Transforms CST to add trailing commas to multi-line collections. '''

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

    def _add_trailing_comma_to_elements(
        self,
        elements: __.cabc.Sequence[ __.libcst.BaseElement ]
    ) -> list[ __.libcst.BaseElement ]:
        ''' Adds trailing comma to last element if missing. '''
        if not elements:
            return list( elements )
        new_elements = list( elements )
        last_elem = new_elements[ -1 ]
        if isinstance( last_elem.comma, __.libcst.MaybeSentinel ):
            new_last = last_elem.with_changes(
                comma = __.libcst.Comma(
                    whitespace_after = __.libcst.SimpleWhitespace( '' )
                )
            )
            new_elements[ -1 ] = new_last
        return new_elements

    def _add_trailing_comma_to_dict_elements(
        self,
        elements: __.cabc.Sequence[ __.libcst.BaseDictElement ]
    ) -> list[ __.libcst.BaseDictElement ]:
        ''' Adds trailing comma to last dict element if missing. '''
        if not elements:
            return list( elements )
        new_elements = list( elements )
        last_elem = new_elements[ -1 ]
        if isinstance( last_elem.comma, __.libcst.MaybeSentinel ):
            new_last = last_elem.with_changes(
                comma = __.libcst.Comma(
                    whitespace_after = __.libcst.SimpleWhitespace( '' )
                )
            )
            new_elements[ -1 ] = new_last
        return new_elements

    def leave_List(
        self,
        original_node: __.libcst.List,
        updated_node: __.libcst.List
    ) -> __.libcst.List:
        ''' Adds trailing comma to multi-line list. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        new_elements = self._add_trailing_comma_to_elements(
            updated_node.elements )
        return updated_node.with_changes( elements = new_elements )

    def leave_Tuple(
        self,
        original_node: __.libcst.Tuple,
        updated_node: __.libcst.Tuple
    ) -> __.libcst.Tuple:
        ''' Adds trailing comma to multi-line tuple. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        new_elements = self._add_trailing_comma_to_elements(
            updated_node.elements )
        return updated_node.with_changes( elements = new_elements )

    def leave_Set(
        self,
        original_node: __.libcst.Set,
        updated_node: __.libcst.Set
    ) -> __.libcst.Set:
        ''' Adds trailing comma to multi-line set. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        new_elements = self._add_trailing_comma_to_elements(
            updated_node.elements )
        return updated_node.with_changes( elements = new_elements )

    def leave_Dict(
        self,
        original_node: __.libcst.Dict,
        updated_node: __.libcst.Dict
    ) -> __.libcst.Dict:
        ''' Adds trailing comma to multi-line dict. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        new_elements = self._add_trailing_comma_to_dict_elements(
            updated_node.elements )
        return updated_node.with_changes( elements = new_elements )


class VBL107( __.FixableRule ):
    ''' Enforces trailing commas in multi-line collection literals. '''

    METADATA_DEPENDENCIES = (
        __.libcst.metadata.PositionProvider,
        __.libcst.metadata.ScopeProvider,
        __.libcst.metadata.QualifiedNameProvider,
        __.libcst.metadata.ParentNodeProvider,
    )

    @property
    def rule_id( self ) -> str:
        return 'VBL107'

    def __init__(
        self,
        filename: str,
        wrapper: __.libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ],
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )
        self._violations_to_fix: list[
            tuple[ __.libcst.CSTNode, str, int, int ] ] = [ ]

    def _is_multiline( self, node: __.libcst.CSTNode ) -> bool:
        ''' Checks if a node spans multiple lines. '''
        try:
            pos = self.get_metadata(
                __.libcst.metadata.PositionProvider, node )
            code_range = __.typx.cast(
                __.libcst.metadata.CodeRange, pos )
        except KeyError:
            return False
        else:
            return code_range.end.line > code_range.start.line

    def _has_trailing_comma(
        self,
        elements: __.cabc.Sequence[
            __.libcst.BaseElement | __.libcst.BaseDictElement ]
    ) -> bool:
        ''' Checks if last element has a trailing comma. '''
        if not elements:
            return True
        last_elem = elements[ -1 ]
        return not isinstance( last_elem.comma, __.libcst.MaybeSentinel )

    def _check_collection(
        self,
        node: __.libcst.CSTNode,
        elements: __.cabc.Sequence[
            __.libcst.BaseElement | __.libcst.BaseDictElement ],
        collection_type: str
    ) -> None:
        ''' Checks collection for missing trailing comma. '''
        if not self._is_multiline( node ):
            return
        if not elements:
            return
        if self._has_trailing_comma( elements ):
            return
        line, column = self._position_from_node( node )
        self._violations_to_fix.append( (
            node,
            f"Multi-line {collection_type} missing trailing comma.",
            line,
            column,
        ) )

    def visit_List( self, node: __.libcst.List ) -> bool:
        ''' Checks list for trailing comma. '''
        self._check_collection( node, node.elements, 'list' )
        return True

    def visit_Tuple( self, node: __.libcst.Tuple ) -> bool:
        ''' Checks tuple for trailing comma. '''
        # Only check tuples with parentheses
        if node.lpar and node.rpar:
            self._check_collection( node, node.elements, 'tuple' )
        return True

    def visit_Set( self, node: __.libcst.Set ) -> bool:
        ''' Checks set for trailing comma. '''
        self._check_collection( node, node.elements, 'set' )
        return True

    def visit_Dict( self, node: __.libcst.Dict ) -> bool:
        ''' Checks dict for trailing comma. '''
        self._check_collection( node, node.elements, 'dict' )
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
                    transformer = _TrailingCommaTransformer( tl, tc )
                    return wrapper.visit( transformer )
                return transform

            self._produce_fix(
                violation = violation,
                description = 'Add trailing comma.',
                transformer_factory = make_transformer(
                    target_line, target_column ),
                safety = __.FixSafety.Safe,
            )


# Self-register this rule
__.RULE_DESCRIPTORS[ 'VBL107' ] = __.RuleDescriptor(
    vbl_code = 'VBL107',
    descriptive_name = 'trailing-comma',
    description = 'Enforces trailing commas in multi-line collections.',
    category = 'readability',
    subcategory = 'formatting',
    rule_class = VBL107,
    violation_message = 'Missing trailing comma',
    examples = (
        '# Violation\n'
        'items = [\n'
        '    1,\n'
        '    2,\n'
        '    3\n'
        ']\n'
        '\n'
        '# Fix\n'
        'items = [\n'
        '    1,\n'
        '    2,\n'
        '    3,\n'
        ']'
    )
)
