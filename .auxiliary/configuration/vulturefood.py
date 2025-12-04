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


''' Vulture whitelist for intentionally unused code. '''

# type: ignore

# ruff: noqa: F401, F811

# Framework code not yet wired to CLI
from vibelinter.engine import Engine, EngineConfiguration, Report
from vibelinter.exceptions import RuleConfigureFailure
from vibelinter.rules.base import BaseRule
from vibelinter.rules.context import ContextExtractor
from vibelinter.rules.implementations.vbl101 import VBL101
from vibelinter.rules.implementations.vbl201 import VBL201
from vibelinter.rules.registry import (
    RuleClassFactory,
    RuleDescriptor,
    RuleRegistry,
    RuleRegistryManager,
)

# Framework attributes and methods used by subclasses
_ = BaseRule.METADATA_DEPENDENCIES
_ = BaseRule.leave_Module
_ = BaseRule._produce_violation
_ = BaseRule._extract_context

# Context extractor methods
_ = ContextExtractor.format_context_display

# VBL101 visitor methods
_ = VBL101.visit_FunctionDef
_ = VBL101.visit_ClassDef
_ = VBL101.visit_SimpleString
_ = VBL101.visit_ConcatenatedString

# VBL201 visitor methods
_ = VBL201.visit_FunctionDef
_ = VBL201.leave_FunctionDef
_ = VBL201.visit_Import
_ = VBL201.visit_ImportFrom

# Registry manager methods
_ = RuleRegistryManager.resolve_rule_identifier
_ = RuleRegistryManager.filter_rules_by_category
_ = RuleRegistryManager.filter_rules_by_subcategory

# Engine methods
_ = Engine.lint_files

# Report fields
_ = Report.contexts
_ = Report.rule_count

# Rule descriptor fields
_ = RuleDescriptor.description

# Type aliases
_ = RuleRegistry
_ = RuleClassFactory

from vibelinter.rules.violations import ViolationContextSequence

_ = ViolationContextSequence

# Exception classes
_ = RuleConfigureFailure

# Pre-existing unused items (not from rules system implementation)
from vibelinter.__ import nomina
from vibelinter.cli import Context

_ = nomina.ComparisonResult
_ = nomina.NominativeArguments
_ = nomina.PositionalArguments
_ = nomina.package_name
_ = Context

# Note: cli.py:466 verbose parameter cannot be whitelisted via vulturefood
# This is a pre-existing unused parameter, not introduced by rules framework
# Vulture will exit with code 3 (1 warning) until this is addressed in CLI implementation
