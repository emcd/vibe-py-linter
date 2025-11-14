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
Designs
*******************************************************************************

.. toctree::
   :maxdepth: 2

   linter-core
   cli
   configuration-integration
   diagnostic-reporting
   file-discovery


Current Designs
===============================================================================

**Linter Core Framework Design**
  Hybrid modular architecture implementing validated LibCST patterns with BaseRule framework, single-pass CST analysis orchestration, rule registry system, and context extraction for enhanced error reporting.

**CLI System Design**
  Tyro-based subcommand architecture with protocol-driven command interfaces, comprehensive type safety, and integration with established configuration and engine systems.

**Configuration Integration Design**
  Integration between python-linter's TOML-based configuration system and emcd-appcore's standardized configuration infrastructure, providing layered precedence with pyproject.toml support and CLI overrides.

**Diagnostic and Report Formatting Design**
  Multi-format diagnostic reporting system with enhanced context display, deterministic sorting, and pluggable renderers implementing REQ-007 requirements for sophisticated error presentation.

**File Discovery and Processing Pipeline Design**
  Python file discovery system with .gitignore integration, configurable filtering, and processing pipeline coordination providing seamless integration with the linter core framework.
