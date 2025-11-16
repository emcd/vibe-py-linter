# type: ignore
# vim: set filetype=python fileencoding=utf-8:
# ruff: noqa: E501, TRY003

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


# ruff: noqa: E501, TRY003
# pyright: reportUndefinedVariable=false, reportArgumentType=false, reportUnknownParameterType=false, reportUnknownVariableType=false

from __future__ import annotations


# ruff: noqa

''' Rule registry system for discovery and instantiation. '''


from . import __


class RuleDescriptor( __.immut.DataclassObject ):
    ''' Describes rule metadata for registry and configuration systems. '''

    vbl_code: __.typx.Annotated[
        str, __.ddoc.Doc( 'VBL code identifier (e.g., "VBL101").' ) ]
    descriptive_name: __.typx.Annotated[
        str, __.ddoc.Doc( 'Hyphen-separated descriptive name (e.g., "blank-line-elimination").' ) ]
    description: __.typx.Annotated[
        str, __.ddoc.Doc( 'Human-readable rule description.' ) ]
    category: __.typx.Annotated[
        str, __.ddoc.Doc( 'Rule category (readability, discoverability, robustness).' ) ]
    subcategory: __.typx.Annotated[
        str, __.ddoc.Doc( 'Rule subcategory (compactness, nomenclature, navigation, etc.).' ) ]
    rule_class: __.typx.Annotated[
        type, __.ddoc.Doc( 'Rule class for instantiation.' ) ]


# Type aliases for registry
RuleRegistry: __.typx.TypeAlias = __.immut.Dictionary[ str, RuleDescriptor ]
RuleClassFactory: __.typx.TypeAlias = __.cabc.Callable[
    [ str, __.libcst.metadata.MetadataWrapper, tuple[ str, ... ] ],
    'BaseRule'  # Forward reference since we're in registry.py
]


class RuleRegistryManager:
    ''' Manages bidirectional mapping between VBL codes and rule implementations. '''

    def __init__(
        self,
        registry: __.typx.Annotated[
            __.cabc.Mapping[ str, RuleDescriptor ],
            __.ddoc.Doc( 'Mapping of VBL codes to rule descriptors.' ) ]
    ) -> None:
        self.registry = __.immut.Dictionary( registry )
        # Build reverse mapping from descriptive names to VBL codes
        self._name_to_code = __.immut.Dictionary( {
            descriptor.descriptive_name: vbl_code
            for vbl_code, descriptor in registry.items( )
        } )

    def resolve_rule_identifier(
        self,
        identifier: __.typx.Annotated[
            str, __.ddoc.Doc( 'VBL code or descriptive name to resolve.' ) ]
    ) -> __.typx.Annotated[
        str,
        __.ddoc.Doc( 'Canonical VBL code for identifier.' ),
        __.ddoc.Raises( 'RuleRegistryInvalidity', 'If identifier is not registered.' ) ]:
        ''' Resolves either VBL code or descriptive name to canonical VBL code. '''
        from ..exceptions import RuleRegistryInvalidity

        # Try as VBL code first
        if identifier in self.registry:
            return identifier

        # Try as descriptive name
        if identifier in self._name_to_code:
            return self._name_to_code[ identifier ]

        raise RuleRegistryInvalidity(
            f'Unknown rule identifier: {identifier!r}. '
            f'Must be a valid VBL code or descriptive name.' )

    def produce_rule_instance(
        self,
        vbl_code: __.typx.Annotated[
            str, __.ddoc.Doc( 'VBL code for rule.' ) ],
        filename: __.typx.Annotated[
            str, __.ddoc.Doc( 'Path to source file being analyzed.' ) ],
        wrapper: __.typx.Annotated[
            __.libcst.metadata.MetadataWrapper,
            __.ddoc.Doc( 'LibCST metadata wrapper.' ) ],
        source_lines: __.typx.Annotated[
            tuple[ str, ... ], __.ddoc.Doc( 'Source file lines.' ) ],
        **parameters: __.typx.Any
    ) -> __.typx.Annotated[
        'BaseRule',  # Forward reference
        __.ddoc.Doc( 'Instantiated rule ready for analysis.' ),
        __.ddoc.Raises( 'RuleRegistryInvalidity', 'If VBL code is not registered.' ) ]:
        ''' Creates a rule instance from its VBL code. '''
        from ..exceptions import RuleRegistryInvalidity

        if vbl_code not in self.registry:
            raise RuleRegistryInvalidity(
                f'Unknown VBL code: {vbl_code!r}. '
                f'Rule must be registered before instantiation.' )

        descriptor = self.registry[ vbl_code ]
        rule_class = descriptor.rule_class

        # Instantiate rule with parameters
        # Base parameters are filename, wrapper, source_lines
        # Additional parameters can be passed as keyword arguments
        return rule_class(
            filename = filename,
            wrapper = wrapper,
            source_lines = source_lines,
            **parameters
        )

    def survey_available_rules( self ) -> tuple[ RuleDescriptor, ... ]:
        ''' Returns all registered rule descriptors sorted by VBL code. '''
        return tuple(
            descriptor
            for _, descriptor in sorted( self.registry.items( ) )
        )

    def filter_rules_by_category(
        self,
        category: __.typx.Annotated[
            str, __.ddoc.Doc( 'Category to filter by.' ) ]
    ) -> tuple[ RuleDescriptor, ... ]:
        ''' Returns rule descriptors matching specified category. '''
        return tuple(
            descriptor
            for descriptor in self.survey_available_rules( )
            if descriptor.category == category
        )

    def filter_rules_by_subcategory(
        self,
        subcategory: __.typx.Annotated[
            str, __.ddoc.Doc( 'Subcategory to filter by.' ) ]
    ) -> tuple[ RuleDescriptor, ... ]:
        ''' Returns rule descriptors matching specified subcategory. '''
        return tuple(
            descriptor
            for descriptor in self.survey_available_rules( )
            if descriptor.subcategory == subcategory
        )
