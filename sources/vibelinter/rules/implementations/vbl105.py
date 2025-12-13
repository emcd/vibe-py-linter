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


''' VBL105: Enforce quote normalization.

    Category: Readability
    Subcategory: Formatting

    Enforces single quotes for data strings and double quotes for
    f-strings, format strings, and exception/log messages.
    Strings containing the opposite quote character are exempt.
'''


from . import __


class _QuoteNormalizationTransformer( __.libcst.CSTTransformer ):
    ''' Transforms CST to normalize quote styles. '''

    METADATA_DEPENDENCIES = (
        __.libcst.metadata.PositionProvider,
    )

    def __init__(
        self,
        target_line: int,
        target_column: int,
        target_quote: str,
    ) -> None:
        super( ).__init__( )
        self.target_line = target_line
        self.target_column = target_column
        self.target_quote = target_quote

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
        ''' Transforms simple string quote style. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        value = updated_node.value
        # Determine prefix (e.g., 'r', 'b', 'f', 'rf')
        prefix = ''
        content_start = 0
        for i, char in enumerate( value ):
            if char in ( '"', "'" ):
                prefix = value[ :i ]
                content_start = i
                break
        rest = value[ content_start: ]
        # Determine current quote style (single/triple)
        if rest.startswith( '"""' ) or rest.startswith( "'''" ):
            # Triple-quoted string
            new_quote = self.target_quote * 3
            content = rest[ 3:-3 ]
        else:
            # Single-quoted string
            new_quote = self.target_quote
            content = rest[ 1:-1 ]
        new_value = f"{prefix}{new_quote}{content}{new_quote}"
        return updated_node.with_changes( value = new_value )

    def leave_FormattedString(
        self,
        original_node: __.libcst.FormattedString,
        updated_node: __.libcst.FormattedString
    ) -> __.libcst.FormattedString:
        ''' Transforms f-string quote style to double quotes. '''
        pos = self._get_position( original_node )
        if pos is None or pos != ( self.target_line, self.target_column ):
            return updated_node
        # Change quote style to double quotes
        return updated_node.with_changes( quote = '"' )


class VBL105( __.FixableRule ):
    ''' Enforces quote normalization conventions. '''

    METADATA_DEPENDENCIES = (
        __.libcst.metadata.PositionProvider,
        __.libcst.metadata.ScopeProvider,
        __.libcst.metadata.QualifiedNameProvider,
        __.libcst.metadata.ParentNodeProvider,
    )

    # Functions whose string arguments should use double quotes
    MESSAGE_FUNCTIONS = frozenset( {
        'ValueError', 'TypeError', 'RuntimeError', 'KeyError',
        'AttributeError', 'IndexError', 'OSError', 'IOError',
        'Exception', 'AssertionError', 'NotImplementedError',
        'StopIteration', 'GeneratorExit', 'SystemExit',
        'logging.debug', 'logging.info', 'logging.warning',
        'logging.error', 'logging.critical', 'logging.exception',
        'print', 'warn', 'warnings.warn',
    } )

    @property
    def rule_id( self ) -> str:
        return 'VBL105'

    def __init__(
        self,
        filename: str,
        wrapper: __.libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ],
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )
        self._violations_to_fix: list[
            tuple[ __.libcst.CSTNode, str, int, int, str ] ] = [ ]
        self._in_message_context: int = 0

    def _string_contains_quote(
        self, value: str, quote: str
    ) -> bool:
        ''' Checks if string content contains the given quote. '''
        # Extract content (remove prefix and quotes)
        content_start = 0
        for i, char in enumerate( value ):
            if char in ( '"', "'" ):
                content_start = i
                break
        rest = value[ content_start: ]
        if rest.startswith( '"""' ) or rest.startswith( "'''" ):
            content = rest[ 3:-3 ]
        else:
            content = rest[ 1:-1 ]
        return quote in content

    def _get_current_quote( self, value: str ) -> str:
        ''' Extracts the current quote character from string value. '''
        for char in value:
            if char in ( '"', "'" ):
                return char
        return '"'

    def visit_Call( self, node: __.libcst.Call ) -> bool:
        ''' Tracks entry into message function calls. '''
        func = node.func
        func_name = None
        if isinstance( func, __.libcst.Name ):
            func_name = func.value
        elif (
            isinstance( func, __.libcst.Attribute )
            and isinstance( func.value, __.libcst.Name )
        ):
            func_name = f"{func.value.value}.{func.attr.value}"
        if func_name in self.MESSAGE_FUNCTIONS:
            self._in_message_context += 1
        return True

    def leave_Call( self, original_node: __.libcst.Call ) -> None:
        ''' Tracks exit from message function calls. '''
        func = original_node.func
        func_name = None
        if isinstance( func, __.libcst.Name ):
            func_name = func.value
        elif (
            isinstance( func, __.libcst.Attribute )
            and isinstance( func.value, __.libcst.Name )
        ):
            func_name = f"{func.value.value}.{func.attr.value}"
        if func_name in self.MESSAGE_FUNCTIONS:
            self._in_message_context -= 1

    def visit_Raise( self, node: __.libcst.Raise ) -> bool:
        ''' Tracks entry into raise statements. '''
        _ = node
        self._in_message_context += 1
        return True

    def leave_Raise( self, original_node: __.libcst.Raise ) -> None:
        ''' Tracks exit from raise statements. '''
        _ = original_node
        self._in_message_context -= 1

    def visit_SimpleString( self, node: __.libcst.SimpleString ) -> bool:
        ''' Checks simple string quote style. '''
        value = node.value
        current_quote = self._get_current_quote( value )
        # Determine target quote based on context
        if self._in_message_context > 0:
            # Message context: prefer double quotes
            target_quote = '"'
            context = 'message string'
        else:
            # Data context: prefer single quotes
            target_quote = "'"
            context = 'data string'
        # Skip if already using correct quote
        if current_quote == target_quote:
            return True
        # Skip if string contains target quote (would require escaping)
        if self._string_contains_quote( value, target_quote ):
            return True
        # Skip byte strings and raw strings in certain cases
        if value.startswith( ( 'b', 'B' ) ):
            return True
        line, column = self._position_from_node( node )
        self._violations_to_fix.append( (
            node,
            f"Use {target_quote} for {context}.",
            line,
            column,
            target_quote
        ) )
        return True

    def visit_FormattedString(
        self, node: __.libcst.FormattedString
    ) -> bool:
        ''' Checks f-string quote style. '''
        current_quote = node.quote
        # F-strings should always use double quotes
        if current_quote == '"':
            return True
        # Skip if f-string content contains double quote
        for part in node.parts:
            is_text = isinstance( part, __.libcst.FormattedStringText )
            if is_text and '"' in part.value:
                return True
        line, column = self._position_from_node( node )
        self._violations_to_fix.append( (
            node,
            'Use " for f-strings.',
            line,
            column,
            '"'
        ) )
        return True

    def _analyze_collections( self ) -> None:
        ''' Generates violations and fixes from collected data. '''
        for entry in self._violations_to_fix:
            node, message, line, column, target_quote = entry
            self._produce_violation( node, message, severity = 'warning' )
            violation = self._violations[ -1 ]
            target_line = line
            target_column = column
            tq = target_quote

            def make_transformer(
                tl: int, tc: int, quote: str
            ) -> __.cabc.Callable[
                [ __.libcst.Module ], __.libcst.Module
            ]:
                def transform( module: __.libcst.Module ) -> __.libcst.Module:
                    wrapper = __.libcst.metadata.MetadataWrapper( module )
                    transformer = _QuoteNormalizationTransformer(
                        tl, tc, quote )
                    return wrapper.visit( transformer )
                return transform

            self._produce_fix(
                violation = violation,
                description = f"Change quotes to {target_quote}.",
                transformer_factory = make_transformer(
                    target_line, target_column, tq ),
                safety = __.FixSafety.Safe,
            )


# Self-register this rule
__.RULE_DESCRIPTORS[ 'VBL105' ] = __.RuleDescriptor(
    vbl_code = 'VBL105',
    descriptive_name = 'quote-normalization',
    description = (
        "Enforces single quotes for data, double for f-strings and messages."
    ),
    category = 'readability',
    subcategory = 'formatting',
    rule_class = VBL105,
    violation_message = 'Incorrect quote style',
    examples = (
        '# Violation\n'
        'name = "Alice"\n'
        "message = f'Hello {name}'\n"
        '\n'
        '# Fix\n'
        "name = 'Alice'\n"
        'message = f"Hello {name}"'
    )
)
