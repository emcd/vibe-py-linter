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


''' VBL108: Enforce docstring formatting.

    Category: Readability
    Subcategory: Documentation

    Enforces triple single-quote docstrings with proper spacing.
    Single-line docstrings should have form ``' Text. '``
    (space after opening, space before closing).
'''


import textwrap as _textwrap
from . import __


MIN_MULTILINE_LINES = 2
SUMMARY_CONTINUATION_INDEX = 1


class _DocstringTransformer( __.libcst.CSTTransformer ):
    ''' Transforms CST to fix docstring formatting. '''

    METADATA_DEPENDENCIES = (
        __.libcst.metadata.PositionProvider,
    )

    def __init__(
        self,
        target_line: int,
        target_column: int,
        fix_type: str,
    ) -> None:
        super( ).__init__( )
        self.target_line = target_line
        self.target_column = target_column
        self.fix_type = fix_type

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

    def leave_SimpleString(
        self,
        original_node: __.libcst.SimpleString,
        updated_node: __.libcst.SimpleString
    ) -> __.libcst.SimpleString:
        ''' Transforms docstring to use triple single quotes with spacing. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        value = updated_node.value
        new_value: str | None = None
        prefix = ''
        content_start = 0
        for i, char in enumerate( value ):
            if char in ( '"', "'" ):
                prefix = value[ :i ]
                content_start = i
                break
        rest = value[ content_start: ]
        if rest.startswith( '"""' ):
            content = rest[ 3:-3 ]
            if self.fix_type == 'quotes':
                new_value = f"{prefix}'''{content}'''"
            elif self.fix_type == 'spacing' and '\n' not in content:
                content = content.strip( )
                new_value = f"{prefix}''' {content} '''"
            elif self.fix_type == 'multiline' and '\n' in content:
                new_value = self._normalize_multiline(
                    content, prefix, self.target_column )
        elif rest.startswith( "'''" ):
            content = rest[ 3:-3 ]
            if self.fix_type == 'spacing' and '\n' not in content:
                content = content.strip( )
                new_value = f"{prefix}''' {content} '''"
            elif self.fix_type == 'multiline' and '\n' in content:
                new_value = self._normalize_multiline(
                    content, prefix, self.target_column )
        if new_value is None:
            return updated_node
        return updated_node.with_changes( value = new_value )

    def _normalize_multiline(
        self,
        content: str,
        prefix: str,
        target_column: int,
    ) -> str:
        ''' Normalizes multi-line docstring indentation and layout. '''
        indent = ' ' * ( max( target_column - 1, 0 ) )
        trimmed = content.strip( '\n' )
        dedented = _textwrap.dedent( trimmed )
        raw_lines = [ line.rstrip( ) for line in dedented.split( '\n' ) ]
        if not raw_lines:
            raw_lines = [ '' ]
        summary = raw_lines[ 0 ].strip( )
        remainder = raw_lines[ 1: ]
        new_lines: list[ str ] = [ f"{indent}{prefix}''' {summary}" ]
        if remainder:
            new_lines.append( f"{indent}" )
            new_lines.extend( f"{indent}{line}" for line in remainder )
        new_lines.append( f"{indent}'''" )
        return '\n'.join( new_lines )


class VBL108( __.FixableRule ):
    ''' Enforces docstring formatting conventions. '''

    METADATA_DEPENDENCIES = (
        __.libcst.metadata.PositionProvider,
        __.libcst.metadata.ScopeProvider,
        __.libcst.metadata.QualifiedNameProvider,
        __.libcst.metadata.ParentNodeProvider,
    )

    @property
    def rule_id( self ) -> str:
        return 'VBL108'

    def __init__(
        self,
        filename: str,
        wrapper: __.libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ],
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )
        self._violations_to_fix: list[
            tuple[ __.libcst.CSTNode, str, int, int, str ] ] = [ ]

    def _is_docstring_position( self, node: __.libcst.CSTNode ) -> bool:
        ''' Checks if node is in a docstring position. '''
        try:
            parent = self.get_metadata(
                __.libcst.metadata.ParentNodeProvider, node )
            # Check if parent is an expression statement
            if isinstance( parent, __.libcst.Expr ):
                grandparent = self.get_metadata(
                    __.libcst.metadata.ParentNodeProvider, parent )
                # Check if grandparent is a block
                gp_types = ( __.libcst.FunctionDef, __.libcst.ClassDef,
                             __.libcst.Module, __.libcst.IndentedBlock )
                if isinstance( grandparent, gp_types ):
                    # Check if this is the first statement
                    if isinstance(
                        grandparent, ( __.libcst.IndentedBlock,
                                       __.libcst.Module )
                    ):
                        body = grandparent.body
                        if body and body[ 0 ] is parent: return True
                    elif isinstance(
                        grandparent,
                        ( __.libcst.FunctionDef, __.libcst.ClassDef )
                    ):
                        body = grandparent.body
                        if isinstance( body, __.libcst.IndentedBlock ):
                            first = body.body[ 0 ] if body.body else None
                            if first is parent: return True
        except KeyError:
            pass
        return False

    def _is_multiline_misformatted(
        self,
        value: str,
        indent: str,
    ) -> bool:
        ''' Checks multi-line docstring formatting and indentation. '''
        lines = value.split( '\n' )
        if len( lines ) < MIN_MULTILINE_LINES:
            return False
        first = lines[ 0 ]
        last = lines[ -1 ].rstrip( )
        expects_body = len( lines ) > MIN_MULTILINE_LINES
        misformatted = (
            not first.startswith( f"{indent}'''" )
            or not last.startswith( f"{indent}'''" )
            or last != f"{indent}'''"
            or not first.startswith( f"{indent}''' " )
        )
        if not misformatted and expects_body:
            misformatted = lines[ SUMMARY_CONTINUATION_INDEX ].strip( ) != ''
        return misformatted

    def visit_SimpleString( self, node: __.libcst.SimpleString ) -> bool:
        ''' Checks docstring formatting. '''
        value = node.value
        # Only check triple-quoted strings
        if not ( value.startswith( '"""' ) or value.startswith( "'''" ) ):
            return True
        # Check if this is in a docstring position
        if not self._is_docstring_position( node ):
            return True
        line, column = self._position_from_node( node )
        # Check quote style
        if value.startswith( '"""' ):
            self._violations_to_fix.append( (
                node,
                "Docstrings should use triple single-quotes.",
                line,
                column,
                'quotes'
            ) )
        # Check spacing for single-line docstrings
        if value.startswith( "'''" ):
            content = value[ 3:-3 ]
            if '\n' not in content:
                # Single-line docstring - check spacing
                no_start = not content.startswith( ' ' )
                no_end = not content.endswith( ' ' )
                if no_start or no_end:
                    self._violations_to_fix.append( (
                        node,
                        "Single-line docstrings need spaces: ''' Text. '''",
                        line,
                        column,
                        'spacing'
                    ) )
        elif value.startswith( '"""' ):
            content = value[ 3:-3 ]
            if '\n' not in content:
                # Also check spacing for double-quote single-line docstrings
                # (will be converted, so spacing matters)
                no_start = not content.startswith( ' ' )
                no_end = not content.endswith( ' ' )
                if no_start or no_end:
                    self._violations_to_fix.append( (
                        node,
                        "Single-line docstrings need spaces: ''' Text. '''",
                        line,
                column,
                'spacing'
            ) )
        # Multi-line formatting
        if '\n' in content:
            indent = ' ' * ( max( column - 1, 0 ) )
            if self._is_multiline_misformatted( value, indent ):
                self._violations_to_fix.append( (
                    node,
                    "Multi-line docstring formatting/indentation is invalid.",
                    line,
                    column,
                    'multiline'
                ) )
        return True

    def _analyze_collections( self ) -> None:
        ''' Generates violations and fixes from collected data. '''
        for node, message, line, column, fix_type in self._violations_to_fix:
            self._produce_violation( node, message, severity = 'warning' )
            violation = self._violations[ -1 ]
            target_line = line
            target_column = column
            ft = fix_type

            def make_transformer(
                tl: int, tc: int, ftype: str
            ) -> __.cabc.Callable[
                [ __.libcst.Module ], __.libcst.Module
            ]:
                def transform( module: __.libcst.Module ) -> __.libcst.Module:
                    wrapper = __.libcst.metadata.MetadataWrapper( module )
                    transformer = _DocstringTransformer( tl, tc, ftype )
                    return wrapper.visit( transformer )
                return transform

            desc = (
                "Change to triple single-quotes."
                if fix_type == 'quotes' else
                "Add proper docstring spacing."
            )
            self._produce_fix(
                violation = violation,
                description = desc,
                transformer_factory = make_transformer(
                    target_line, target_column, ft ),
                safety = __.FixSafety.Safe,
            )


# Self-register this rule
__.RULE_DESCRIPTORS[ 'VBL108' ] = __.RuleDescriptor(
    vbl_code = 'VBL108',
    descriptive_name = 'docstring-formatting',
    description = "Enforces triple single-quote docstrings with spacing.",
    category = 'readability',
    subcategory = 'documentation',
    rule_class = VBL108,
    violation_message = 'Docstring formatting issue',
    examples = (
        '# Violation\n'
        '"""Example docstring."""\n'
        "'''No spacing.'''\n"
        '\n'
        '# Fix\n'
        "''' Example docstring. '''\n"
        "''' Proper spacing. '''"
    )
)
