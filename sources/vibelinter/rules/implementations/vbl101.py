# type: ignore
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


# ruff: noqa

''' VBL101: Detect consecutive blank lines within function bodies.

# ruff: noqa: E501, F403


    Category: Readability
    Subcategory: Compactness

    This rule detects multiple consecutive blank lines within function or method bodies
    and suggests their elimination to improve code compactness.
'''


from .. import __
from ..base import BaseRule


class VBL101( BaseRule ):
    ''' Detects consecutive blank lines within function bodies. '''

    @property
    def rule_id( self ) -> str:
        return 'VBL101'

    def __init__(
        self,
        filename: str,
        wrapper: __.libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ],
        max_consecutive_blanks: int = 1,
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )
        self.max_consecutive_blanks = max_consecutive_blanks
        # Collection: store function definitions and their line ranges
        self._function_ranges: list[ tuple[ int, int, __.libcst.FunctionDef ] ] = [ ]

    def visit_FunctionDef( self, node: __.libcst.FunctionDef ) -> bool:
        ''' Collects function definitions for later analysis. '''
        # Get the position of the function
        try:
            position = self.wrapper.resolve( __.libcst.metadata.PositionProvider )[ node ]
            start_line = position.start.line
            end_line = position.end.line
            self._function_ranges.append( ( start_line, end_line, node ) )
        except KeyError:
            # Position not available, skip this function
            pass
        return True  # Continue visiting children

    def _analyze_collections( self ) -> None:
        ''' Analyzes collected function definitions for consecutive blank lines. '''
        for start_line, end_line, func_node in self._function_ranges:
            # Analyze blank lines within function body
            # Skip function signature lines and focus on body
            # Get function body start (after the def line and any decorators)
            body_start = start_line + 1  # Start checking after the def line

            # Track consecutive blank lines
            consecutive_blanks = 0
            blank_start_line = 0

            for line_num in range( body_start, end_line + 1 ):
                # Get the line (0-indexed access)
                if line_num - 1 >= len( self.source_lines ):
                    break

                line = self.source_lines[ line_num - 1 ]

                # Check if line is blank (empty or only whitespace)
                if not line.strip( ):
                    if consecutive_blanks == 0:
                        blank_start_line = line_num
                    consecutive_blanks += 1
                else:
                    # Non-blank line found
                    if consecutive_blanks > self.max_consecutive_blanks:
                        # Report violation at the start of the excessive blank lines
                        self._report_consecutive_blanks(
                            func_node,
                            blank_start_line,
                            consecutive_blanks
                        )
                    consecutive_blanks = 0

            # Check if function ends with excessive blank lines
            if consecutive_blanks > self.max_consecutive_blanks:
                self._report_consecutive_blanks(
                    func_node,
                    blank_start_line,
                    consecutive_blanks
                )

    def _report_consecutive_blanks(
        self,
        func_node: __.libcst.FunctionDef,
        line_num: int,
        count: int
    ) -> None:
        ''' Reports a violation for consecutive blank lines. '''
        # Create a violation at the first excessive blank line
        # We'll use a SimpleStatementLine node if available, otherwise the function node
        message = (
            f'Found {count} consecutive blank lines in function body. '
            f'Maximum allowed is {self.max_consecutive_blanks}. '
            f'Consider removing {count - self.max_consecutive_blanks} blank line(s).'
        )

        # Since we're reporting based on line number, we need to create a violation manually
        # with the specific line number rather than using a node
        violation = __.violations.Violation(
            rule_id = self.rule_id,
            filename = self.filename,
            line = line_num,
            column = 1,  # Blank lines start at column 1
            message = message,
            severity = 'warning',  # Use warning for style issues
        )
        self._violations.append( violation )
