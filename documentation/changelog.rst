.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Release Notes
*******************************************************************************

.. towncrier release notes start

vibelinter 1.0a2 (2025-12-06)
=============================

Enhancements
------------

- Add support for inline ``# noqa`` suppressions and per-file ignores in configuration.
  Users can now suppress specific violations inline or configure files to ignore certain rules.
- Support descriptive rule names (e.g., ``import-hub-enforcement``) alongside VBL codes in CLI arguments, per-file ignores, and inline suppressions.
  Maintains backward compatibility with existing VBL codes.


Repairs
-------

- Fix per-file ignores configuration not being applied from ``pyproject.toml``.
  Previously, ignore rules specified in configuration were silently ignored.


vibelinter 1.0a1 (2025-12-03)
=============================

Enhancements
------------

- Update VBL101 (Blank Line Elimination) to allow blank lines immediately surrounding nested function and class definitions for better readability.


Repairs
-------

- Fix VBL201 (Import Hub Enforcement) to correctly recognize private aliases (e.g., ``import x as _x``) in simple imports, preventing false positive violations.


vibelinter 1.0a0 (2025-11-30)
=============================

Enhancements
------------

- Add support for CPython 3.10 to 3.14.
- Add support for PyPy 3.10 and 3.11.
- CLI: Interactive command-line interface with check command supporting multiple output formats (text, JSON), context display, rule selection, and parallel processing.
- Configuration: Support for pyproject.toml configuration files with rule selection, file path filtering, context line configuration, and per-rule settings.
- Core linting engine with LibCST integration for single-pass AST analysis, rule orchestration, and violation collection across multiple Python files.
- VBL101: Blank line elimination rule detects unnecessary blank lines in function bodies while preserving blank lines inside docstrings and string literals.
- VBL201: Import hub enforcement rule ensures non-private imports only appear in designated hub modules (configurable via hub_patterns) to maintain architectural consistency and prevent namespace pollution.
- VBL202: Import spaghetti prevention rule detects excessive relative import depth (more than 2 parent levels) and enforces proper import structure in re-export hub modules.
