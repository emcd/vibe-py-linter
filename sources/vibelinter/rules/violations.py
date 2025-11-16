# type: ignore
# vim: set filetype=python fileencoding=utf-8:
# ruff: noqa: E501, F403

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


''' Core violation data structures for linting framework. '''


# ruff: noqa: F405
from ..__ import *


class Violation( immut.DataclassObject ):
    ''' Represents a rule violation with precise location and context information. '''

    rule_id: typx.Annotated[
        str, ddoc.Doc( 'VBL code identifier for the rule that detected this violation.' ) ]
    filename: typx.Annotated[
        str, ddoc.Doc( 'Path to source file containing violation.' ) ]
    line: typx.Annotated[
        int, ddoc.Doc( 'One-indexed line number of violation.' ) ]
    column: typx.Annotated[
        int, ddoc.Doc( 'One-indexed column position of violation.' ) ]
    message: typx.Annotated[
        str, ddoc.Doc( 'Human-readable description of violation.' ) ]
    severity: typx.Annotated[
        str, ddoc.Doc( "Severity level: 'error', 'warning', or 'info'." ) ] = 'error'


class ViolationContext( immut.DataclassObject ):
    ''' Represents source code context surrounding a violation for enhanced error reporting. '''

    violation: typx.Annotated[
        Violation, ddoc.Doc( 'The violation this context describes.' ) ]
    context_lines: typx.Annotated[
        tuple[ str, ... ], ddoc.Doc( 'Source lines surrounding violation.' ) ]
    context_start_line: typx.Annotated[
        int, ddoc.Doc( 'One-indexed starting line of context display.' ) ]


# Type aliases for rule framework contracts
ViolationSequence: typx.TypeAlias = cabc.Sequence[ Violation ]
ViolationContextSequence: typx.TypeAlias = cabc.Sequence[ ViolationContext ]
