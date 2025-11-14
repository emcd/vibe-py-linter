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
Architectural Decision Records
*******************************************************************************

.. toctree::
   :maxdepth: 2

   001-core-engine-and-rule-framework
   002-syntax-tree-analysis-technology  
   003-configuration-management
   004-subcommand-architecture

Current Decisions
===============================================================================

**001. Core Engine and Rule Framework Architecture**
  Hybrid modular architecture combining rapid prototyping with extensible plugin system for rule implementation.

**002. Syntax Tree Analysis Technology Selection**  
  LibCST adoption for concrete syntax tree analysis with rich metadata support enabling precise error reporting and future auto-fix capabilities.

**003. Configuration Management System**
  TOML-based configuration with ``pyproject.toml`` integration, supporting rule parameterization, command-line overrides, and non-destructive user interaction via snippet generation.

**004. Subcommand-Based CLI Architecture**
  Verb-based subcommand structure (check, fix, configure, describe, serve) with isolated option namespaces for different operational modes.

For ADR format and guidance, see the `architecture documentation guide
<https://emcd.github.io/python-project-common/stable/sphinx-html/common/architecture.html>`_.