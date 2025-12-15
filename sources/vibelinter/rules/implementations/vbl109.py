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


''' VBL109: Enforce maximum line length.

    Category: Readability
    Subcategory: Formatting

    Detects lines exceeding the maximum line length (79 characters).
    This rule currently provides detection only; automated reformatting
    via the LineReformatter algorithm is planned for a future release.
'''


from . import __


# Default maximum line length per style guide
MAX_LINE_LENGTH = 79


class VBL109( __.BaseRule ):
    ''' Detects lines exceeding maximum length. '''

    METADATA_DEPENDENCIES = (
        __.libcst.metadata.PositionProvider,
        __.libcst.metadata.ScopeProvider,
        __.libcst.metadata.QualifiedNameProvider,
    )

    @property
    def rule_id( self ) -> str:
        return 'VBL109'

    def __init__(
        self,
        filename: str,
        wrapper: __.libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ],
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )
        self._long_lines: list[ tuple[ int, int ] ] = [ ]

    def visit_Module( self, node: __.libcst.Module ) -> bool:
        ''' Checks all source lines for length violations. '''
        _ = node
        for line_num, line in enumerate( self.source_lines, start = 1 ):
            # Remove trailing newline for accurate length
            line_content = line.rstrip( '\n\r' )
            if len( line_content ) > MAX_LINE_LENGTH:
                self._long_lines.append( ( line_num, len( line_content ) ) )
        return True

    def _analyze_collections( self ) -> None:
        ''' Generates violations for long lines. '''
        for line_num, length in self._long_lines:
            # Create a simple violation without CST node
            from ..violations import Violation
            violation = Violation(
                rule_id = self.rule_id,
                filename = self.filename,
                line = line_num,
                column = MAX_LINE_LENGTH + 1,
                message = (
                    f"Line exceeds {MAX_LINE_LENGTH} characters "
                    f"({length} characters)."
                ),
                severity = 'warning',
            )
            self._violations.append( violation )


# Self-register this rule
__.RULE_DESCRIPTORS[ 'VBL109' ] = __.RuleDescriptor(
    vbl_code = 'VBL109',
    descriptive_name = 'line-length',
    description = f'Enforces maximum line length ({MAX_LINE_LENGTH} chars).',
    category = 'readability',
    subcategory = 'formatting',
    rule_class = VBL109,
    violation_message = 'Line exceeds maximum length',
    examples = (
        '# Violation\n'
        'very_long_variable_name = some_function_call( with_many, arguments, '
        'that_make, the_line, too_long )\n'
        '\n'
        '# Fix\n'
        'very_long_variable_name = some_function_call(\n'
        '    with_many, arguments, that_make, the_line, too_long )'
    )
)
