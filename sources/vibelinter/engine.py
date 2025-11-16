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

''' Central linter engine coordinating single-pass CST analysis. '''

# ruff: noqa: E501
# pyright: reportUndefinedVariable=false, reportArgumentType=false

from __future__ import annotations

import pathlib
import time

from . import __
from .rules import context, violations


class EngineConfiguration( __.immut.DataclassObject ):
    ''' Configuration for linter engine behavior and rule selection. '''

    enabled_rules: __.typx.Annotated[
        frozenset[ str ], __.ddoc.Doc( 'VBL codes of rules to execute.' ) ]
    rule_parameters: __.typx.Annotated[
        __.immut.Dictionary[ str, __.immut.Dictionary[ str, __.typx.Any ] ],
        __.ddoc.Doc( 'Rule-specific configuration parameters indexed by VBL code.' ) ] = (
            __.immut.Dictionary( ) )
    context_size: __.typx.Annotated[
        int, __.ddoc.Doc( 'Number of context lines to extract around violations.' ) ] = 2
    include_context: __.typx.Annotated[
        bool, __.ddoc.Doc( 'Whether to extract source context for violations.' ) ] = True


class Report( __.immut.DataclassObject ):
    ''' Results of linting analysis including violations and metadata. '''

    violations: __.typx.Annotated[
        tuple[ violations.Violation, ... ],
        __.ddoc.Doc( 'All violations detected during analysis.' ) ]
    contexts: __.typx.Annotated[
        tuple[ violations.ViolationContext, ... ],
        __.ddoc.Doc( 'Violation contexts when context extraction enabled.' ) ]
    filename: __.typx.Annotated[
        str, __.ddoc.Doc( 'Path to analyzed source file.' ) ]
    rule_count: __.typx.Annotated[
        int, __.ddoc.Doc( 'Number of rules executed during analysis.' ) ]
    analysis_duration_ms: __.typx.Annotated[
        float, __.ddoc.Doc( 'Time spent in analysis phase excluding parsing.' ) ]


class Engine:
    ''' Central orchestrator for linting analysis implementing single-pass CST traversal. '''

    def __init__(
        self,
        registry_manager: __.typx.Annotated[
            'RuleRegistryManager',  # Forward reference to avoid circular import
            __.ddoc.Doc( 'Rule registry for instantiating rules.' ) ],
        configuration: __.typx.Annotated[
            EngineConfiguration, __.ddoc.Doc( 'Engine configuration and rule selection.' ) ],
    ) -> None:
        self.registry_manager = registry_manager
        self.configuration = configuration

    def lint_file(
        self,
        file_path: __.typx.Annotated[
            pathlib.Path, __.ddoc.Doc( 'Path to Python source file to analyze.' ) ]
    ) -> __.typx.Annotated[
        Report,
        __.ddoc.Doc( 'Analysis results including violations and metadata.' ),
        __.ddoc.Raises( 'RuleExecuteFailure', 'If rule execution fails unrecoverably.' ),
        __.ddoc.Raises( 'MetadataProvideFailure', 'If LibCST metadata initialization fails.' ) ]:
        ''' Analyzes a Python source file and returns violations. '''
        source_code = file_path.read_text( encoding = 'utf-8' )
        return self.lint_source( source_code, str( file_path ) )

    def lint_source(
        self,
        source_code: __.typx.Annotated[
            str, __.ddoc.Doc( 'Python source code to analyze.' ) ],
        filename: __.typx.Annotated[
            str, __.ddoc.Doc( 'Logical filename for source code.' ) ] = '<string>',
    ) -> __.typx.Annotated[
        Report,
        __.ddoc.Doc( 'Analysis results including violations and metadata.' ),
        __.ddoc.Raises( 'RuleExecuteFailure', 'If rule execution fails unrecoverably.' ),
        __.ddoc.Raises( 'MetadataProvideFailure', 'If LibCST metadata initialization fails.' ) ]:
        ''' Analyzes Python source code and returns violations. '''
        from .exceptions import MetadataProvideFailure, RuleExecuteFailure

        analysis_start_time = time.perf_counter( )

        try:
            # Parse source code into CST
            module = __.libcst.parse_module( source_code )
            source_lines = tuple( source_code.splitlines( ) )

            # Create metadata wrapper with required providers
            try:
                wrapper = __.libcst.metadata.MetadataWrapper( module )
            except Exception as exc:
                raise MetadataProvideFailure(
                    f'Failed to initialize LibCST metadata providers for {filename!r}'
                ) from exc

            # Instantiate enabled rules
            rules = [ ]
            for vbl_code in self.configuration.enabled_rules:
                # Get rule-specific parameters if any
                params = self.configuration.rule_parameters.get( vbl_code, { } )
                try:
                    rule = self.registry_manager.produce_rule_instance(
                        vbl_code = vbl_code,
                        filename = filename,
                        wrapper = wrapper,
                        source_lines = source_lines,
                        **params
                    )
                    rules.append( rule )
                except Exception as exc:
                    raise RuleExecuteFailure(
                        f'Failed to instantiate rule {vbl_code!r} for {filename!r}'
                    ) from exc

            # Single-pass CST traversal with all rules
            for rule in rules:
                try:
                    wrapper.visit( rule )
                except Exception as exc:
                    raise RuleExecuteFailure(
                        f'Rule {rule.rule_id!r} failed during analysis of {filename!r}'
                    ) from exc

            # Collect violations from all rules
            all_violations: list[ violations.Violation ] = [ ]
            for rule in rules:
                all_violations.extend( rule.violations )

            # Sort violations by location (line, then column)
            all_violations.sort( key = lambda v: ( v.line, v.column ) )

            # Extract contexts if enabled
            violation_contexts: tuple[ violations.ViolationContext, ... ] = ( )
            if self.configuration.include_context and all_violations:
                violation_contexts = context.extract_contexts_for_violations(
                    all_violations,
                    source_lines,
                    self.configuration.context_size
                )

            analysis_duration_ms = ( time.perf_counter( ) - analysis_start_time ) * 1000

            return Report(
                violations = tuple( all_violations ),
                contexts = violation_contexts,
                filename = filename,
                rule_count = len( rules ),
                analysis_duration_ms = analysis_duration_ms,
            )

        except ( MetadataProvideFailure, RuleExecuteFailure ):
            # Re-raise our own exceptions
            raise
        except Exception as exc:
            # Wrap unexpected exceptions
            raise RuleExecuteFailure(
                f'Unexpected error during analysis of {filename!r}'
            ) from exc

    def lint_files(
        self,
        file_paths: __.typx.Annotated[
            __.cabc.Sequence[ pathlib.Path ],
            __.ddoc.Doc( 'Paths to Python source files to analyze.' ) ]
    ) -> __.typx.Annotated[
        tuple[ Report, ... ],
        __.ddoc.Doc( 'Analysis results for all files.' ) ]:
        ''' Analyzes multiple Python source files and returns violations for each. '''
        reports: list[ Report ] = [ ]
        for file_path in file_paths:
            try:
                report = self.lint_file( file_path )
                reports.append( report )
            except Exception:
                # For batch analysis, we continue on errors
                # Individual file errors are logged but don't stop the batch
                # Future enhancement: collect errors in report
                continue
        return tuple( reports )
