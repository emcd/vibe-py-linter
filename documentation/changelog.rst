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
