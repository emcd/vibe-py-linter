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



''' VBL101: Detect blank lines between statements in function bodies.



    Category: Readability
    Subcategory: Compactness

    This rule detects blank lines between statements within function or
    method bodies and suggests their elimination to improve vertical
    compactness per the project coding standards. Blank lines inside
    string literals are allowed.
'''


from . import __


class VBL101( __.BaseRule ):
    ''' Detects blank lines between statements in function bodies. '''

    @property
    def rule_id( self ) -> str:
        return 'VBL101'

    def __init__(
        self,
        filename: str,
        wrapper: __.libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ],
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )
        # Collection: store function definitions and their line ranges
        self._function_ranges: list[
            tuple[ int, int, __.libcst.FunctionDef ] ] = [ ]

    def visit_FunctionDef( self, node: __.libcst.FunctionDef ) -> bool:
        ''' Collects function definitions for later analysis. '''
        # Get the position of the function
        try:
            position = self.wrapper.resolve(
                __.libcst.metadata.PositionProvider )[ node ]
            start_line = position.start.line
            end_line = position.end.line
            self._function_ranges.append( ( start_line, end_line, node ) )
        except KeyError:
            # Position not available, skip this function
            pass
        return True  # Continue visiting children

    def _analyze_collections( self ) -> None:
        ''' Analyzes collected functions for blank lines between statements.
            Blank lines inside string literals are allowed.
        '''
        for start_line, end_line, _func_node in self._function_ranges:
            # Get function body start (after the def line)
            body_start = start_line + 1
            in_string = False
            string_delimiter = None
            for line_num in range( body_start, end_line + 1 ):
                if line_num - 1 >= len( self.source_lines ): break
                line = self.source_lines[ line_num - 1 ]
                stripped = line.strip( )
                # Track triple-quoted string literal state
                if not in_string:
                    # Check if this line starts a triple-quoted string
                    starts_triple_double = stripped.startswith( '"""' )
                    starts_triple_single = stripped.startswith( "'''" )
                    if starts_triple_double or starts_triple_single:
                        string_delimiter = stripped[ :3 ]
                        in_string = True
                        # Check if string closes on same line
                        delimiter_count = stripped.count( string_delimiter )
                        if delimiter_count >= 2:  # noqa: PLR2004
                            in_string = False
                elif string_delimiter and string_delimiter in stripped:
                    # String ends on this line
                    in_string = False
                    string_delimiter = None
                # Report violation for blank lines between statements
                if not stripped and not in_string:
                    self._report_blank_line( line_num )

    def _report_blank_line( self, line_num: int ) -> None:
        ''' Reports a violation for a blank line in function body. '''
        from .. import violations as _violations
        violation = _violations.Violation(
            rule_id = self.rule_id,
            filename = self.filename,
            line = line_num,
            column = 1,
            message = "Blank line in function body.",
            severity = 'warning' )
        self._violations.append( violation )


# Self-register this rule
__.RULE_DESCRIPTORS[ 'VBL101' ] = __.RuleDescriptor(
    vbl_code = 'VBL101',
    descriptive_name = 'blank-line-elimination',
    description = 'Detects blank lines within function bodies.',
    category = 'readability',
    subcategory = 'compactness',
    rule_class = VBL101,
)
