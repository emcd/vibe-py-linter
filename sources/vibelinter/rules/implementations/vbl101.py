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



''' VBL101: Detect blank lines within function bodies.



    Category: Readability
    Subcategory: Compactness

    This rule detects any blank lines within function or method bodies and
    suggests their elimination to improve vertical compactness per the
    project coding standards.
'''


from .. import __
from ..base import BaseRule


class VBL101( BaseRule ):
    ''' Detects any blank lines within function bodies. '''

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
        ''' Analyzes collected functions for any blank lines. '''
        for start_line, end_line, _func_node in self._function_ranges:
            # Get function body start (after the def line)
            body_start = start_line + 1
            for line_num in range( body_start, end_line + 1 ):
                if line_num - 1 >= len( self.source_lines ): break
                line = self.source_lines[ line_num - 1 ]
                # Report violation for any blank line
                if not line.strip( ):
                    self._report_blank_line( line_num )

    def _report_blank_line( self, line_num: int ) -> None:
        ''' Reports a violation for a blank line in function body. '''
        violation = __.violations.Violation(
            rule_id = self.rule_id,
            filename = self.filename,
            line = line_num,
            column = 1,
            message = "Blank line in function body.",
            severity = 'warning' )
        self._violations.append( violation )
