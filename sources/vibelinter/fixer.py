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


''' Fix engine for applying automated code fixes.

    Coordinates fix application with conflict resolution, safety filtering,
    and diff generation for preview mode.
'''


import difflib as _difflib

from . import __
from .rules.fixable import Fix as _Fix
from .rules.fixable import FixSafety as _FixSafety


class FixConflict( __.immut.DataclassObject ):
    ''' Records when a fix is skipped due to overlap with another fix. '''

    skipped_fix: __.typx.Annotated[
        _Fix,
        __.ddoc.Doc( 'The fix that was skipped.' ) ]
    conflicting_fix: __.typx.Annotated[
        _Fix,
        __.ddoc.Doc( 'The fix that caused the conflict.' ) ]
    reason: __.typx.Annotated[
        str,
        __.ddoc.Doc( 'Description of why the conflict occurred.' ) ]


class SkippedFix( __.immut.DataclassObject ):
    ''' Records when a fix is skipped due to safety classification. '''

    fix: __.typx.Annotated[
        _Fix,
        __.ddoc.Doc( 'The fix that was skipped.' ) ]
    reason: __.typx.Annotated[
        str,
        __.ddoc.Doc(
            'Reason for skipping (e.g., "requires --apply-dangerous").'
        ) ]


class FixApplicationResult( __.immut.DataclassObject ):
    ''' Result of applying fixes to a single file. '''

    filename: __.typx.Annotated[
        str,
        __.ddoc.Doc( 'Path to the file that was processed.' ) ]
    original_source: __.typx.Annotated[
        str,
        __.ddoc.Doc( 'Original source code before fixes.' ) ]
    modified_source: __.typx.Annotated[
        str,
        __.ddoc.Doc( 'Modified source code after fixes.' ) ]
    applied_fixes: __.typx.Annotated[
        tuple[ _Fix, ... ],
        __.ddoc.Doc( 'Fixes that were successfully applied.' ) ]
    skipped_fixes: __.typx.Annotated[
        tuple[ SkippedFix, ... ],
        __.ddoc.Doc( 'Fixes skipped due to safety classification.' ) ]
    conflicts: __.typx.Annotated[
        tuple[ FixConflict, ... ],
        __.ddoc.Doc( 'Fixes skipped due to overlapping regions.' ) ]

    @property
    def has_changes( self ) -> bool:
        ''' Returns True if any fixes were applied. '''
        return len( self.applied_fixes ) > 0

    def generate_unified_diff( self ) -> str:
        ''' Generates unified diff of changes. '''
        original_lines = self.original_source.splitlines( keepends = True )
        modified_lines = self.modified_source.splitlines( keepends = True )
        diff = _difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile = f"a/{self.filename}",
            tofile = f"b/{self.filename}",
        )
        return ''.join( diff )

    def generate_context_diff( self ) -> str:
        ''' Generates context diff of changes. '''
        original_lines = self.original_source.splitlines( keepends = True )
        modified_lines = self.modified_source.splitlines( keepends = True )
        diff = _difflib.context_diff(
            original_lines,
            modified_lines,
            fromfile = f"a/{self.filename}",
            tofile = f"b/{self.filename}",
        )
        return ''.join( diff )


class FixEngineResult( __.immut.DataclassObject ):
    ''' Aggregate result from applying fixes across multiple files. '''

    file_results: __.typx.Annotated[
        tuple[ FixApplicationResult, ... ],
        __.ddoc.Doc( 'Results for each processed file.' ) ]
    total_applied: __.typx.Annotated[
        int,
        __.ddoc.Doc( 'Total number of fixes applied.' ) ]
    total_skipped: __.typx.Annotated[
        int,
        __.ddoc.Doc( 'Total number of fixes skipped.' ) ]
    total_conflicts: __.typx.Annotated[
        int,
        __.ddoc.Doc( 'Total number of conflicts encountered.' ) ]


class FixResult( __.immut.DataclassObject ):
    ''' Aggregated result from a fix command run. '''

    paths: tuple[ str, ... ]
    simulate: bool
    diff_format: str
    apply_dangerous: bool
    file_results: tuple[ FixApplicationResult, ... ]
    total_applied: int
    total_skipped: int
    total_conflicts: int
    rule_selection: __.typx.Optional[ str ] = None


class FixEngine:
    ''' Coordinates fix application with safety and conflict handling.

        Fixes are applied in reverse position order (end of file first)
        to avoid offset drift. Overlapping fixes are detected and skipped.
    '''

    def __init__(
        self,
        apply_dangerous: __.typx.Annotated[
            bool,
            __.ddoc.Doc(
                'Whether to apply potentially unsafe and dangerous fixes.'
            ) ] = False,
    ) -> None:
        self.apply_dangerous = apply_dangerous

    def apply_fixes(
        self,
        source_code: __.typx.Annotated[
            str,
            __.ddoc.Doc( 'Original source code.' ) ],
        fixes: __.typx.Annotated[
            __.cabc.Sequence[ _Fix ],
            __.ddoc.Doc( 'Fixes to apply.' ) ],
        filename: __.typx.Annotated[
            str,
            __.ddoc.Doc( 'Filename for reporting.' ) ] = '<string>',
    ) -> __.typx.Annotated[
        FixApplicationResult,
        __.ddoc.Doc( 'Result of fix application.' )
    ]:
        ''' Applies fixes to source code with conflict resolution. '''
        if not fixes:
            return FixApplicationResult(
                filename = filename,
                original_source = source_code,
                modified_source = source_code,
                applied_fixes = ( ),
                skipped_fixes = ( ),
                conflicts = ( ),
            )
        # Filter by safety
        eligible_fixes, skipped_fixes = self._filter_by_safety( fixes )
        if not eligible_fixes:
            return FixApplicationResult(
                filename = filename,
                original_source = source_code,
                modified_source = source_code,
                applied_fixes = ( ),
                skipped_fixes = tuple( skipped_fixes ),
                conflicts = ( ),
            )
        # Sort by position (reverse order - end of file first)
        sorted_fixes = self._sort_fixes_by_position( eligible_fixes )
        # Apply fixes sequentially, detecting conflicts
        module = __.libcst.parse_module( source_code )
        applied: list[ _Fix ] = [ ]
        conflicts: list[ FixConflict ] = [ ]
        applied_positions: dict[ tuple[ int, int ], _Fix ] = { }
        for fix in sorted_fixes:
            position = ( fix.violation.line, fix.violation.column )
            if position in applied_positions:
                conflicts.append( FixConflict(
                    skipped_fix = fix,
                    conflicting_fix = applied_positions[ position ],
                    reason = "Overlapping fix location.",
                ) )
                continue
            try:
                module = fix.transformer_factory( module )
                applied.append( fix )
                applied_positions[ position ] = fix
            except Exception:
                # If transformation fails, skip this fix
                conflicts.append( FixConflict(
                    skipped_fix = fix,
                    conflicting_fix = fix,
                    reason = "Transformation failed.",
                ) )
        modified_source = module.code
        return FixApplicationResult(
            filename = filename,
            original_source = source_code,
            modified_source = modified_source,
            applied_fixes = tuple( applied ),
            skipped_fixes = tuple( skipped_fixes ),
            conflicts = tuple( conflicts ),
        )

    def _filter_by_safety(
        self,
        fixes: __.cabc.Sequence[ _Fix ]
    ) -> tuple[ list[ _Fix ], list[ SkippedFix ] ]:
        ''' Filters fixes based on safety classification. '''
        eligible: list[ _Fix ] = [ ]
        skipped: list[ SkippedFix ] = [ ]
        for fix in fixes:
            if fix.safety == _FixSafety.Safe or self.apply_dangerous:
                eligible.append( fix )
            else:
                reason = (
                    "Fix is {safety}; use --apply-dangerous to enable."
                    .format( safety = fix.safety.value ) )
                skipped.append( SkippedFix( fix = fix, reason = reason ) )
        return eligible, skipped

    def _sort_fixes_by_position(
        self,
        fixes: list[ _Fix ]
    ) -> list[ _Fix ]:
        ''' Sorts fixes in reverse position order (end of file first). '''
        return sorted(
            fixes,
            key = lambda f: ( f.violation.line, f.violation.column ),
            reverse = True,
        )

    def apply_fixes_to_file(
        self,
        file_path: __.typx.Annotated[
            __.pathlib.Path,
            __.ddoc.Doc( 'Path to file to fix.' ) ],
        fixes: __.typx.Annotated[
            __.cabc.Sequence[ _Fix ],
            __.ddoc.Doc( 'Fixes to apply.' ) ],
        simulate: __.typx.Annotated[
            bool,
            __.ddoc.Doc( 'If True, do not write changes to disk.' ) ] = False,
    ) -> __.typx.Annotated[
        FixApplicationResult,
        __.ddoc.Doc( 'Result of fix application.' )
    ]:
        ''' Applies fixes to a file, optionally writing changes. '''
        source_code = file_path.read_text( encoding = 'utf-8' )
        result = self.apply_fixes( source_code, fixes, str( file_path ) )
        if result.has_changes and not simulate:
            file_path.write_text( result.modified_source, encoding = 'utf-8' )
        return result
