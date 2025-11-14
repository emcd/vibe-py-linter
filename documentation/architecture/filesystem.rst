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
Filesystem Organization
*******************************************************************************

This document describes the specific filesystem organization for the project,
showing how the standard organizational patterns are implemented for this
project's configuration. For the underlying principles and rationale behind
these patterns, see the `common architecture documentation
<https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_.

Project Structure
===============================================================================

Root Directory Organization
-------------------------------------------------------------------------------

The project implements the standard filesystem organization:

.. code-block::

    vibe-py-linter/
    ├── LICENSE.txt              # Project license
    ├── README.rst               # Project overview and quick start
    ├── pyproject.toml           # Python packaging and tool configuration
    ├── documentation/           # Sphinx documentation source
    ├── sources/                 # All source code
    ├── tests/                   # Test suites
    ├── data/                    # Redistributable data resources
    ├── pyinstaller.spec         # Executable packaging configuration
    └── .auxiliary/              # Development workspace

Source Code Organization
===============================================================================

Package Structure
-------------------------------------------------------------------------------

The main Python package follows the standard ``sources/`` directory pattern:

.. code-block::

    sources/
    ├── linter/                       # Main Python package
    │   ├── __/                      # Centralized import hub
    │   │   ├── __init__.py          # Re-exports core utilities
    │   │   ├── imports.py           # External library imports (libcst, tomli)
    │   │   └── nomina.py            # Linter-specific naming constants
    │   ├── __init__.py              # Package entry point
    │   ├── py.typed                 # Type checking marker
    │   ├── __main__.py              # CLI entry point for `python -m vibelinter`
    │   ├── cli.py                   # Command-line interface implementation
    │   ├── exceptions.py            # Package exception hierarchy
    │   ├── engine.py                # Core linter engine and orchestration
    │   ├── configuration.py         # TOML configuration management
    │   ├── reporting.py             # Violation formatting and output
    │   └── rules/                   # Rule implementation package
    │       ├── __.py                # Centralized imports for rules subpackage
    │       ├── __init__.py          # Rules package entry point
    │       ├── base.py              # BaseRule abstract class
    │       ├── registry.py          # Rule registry and VBL code mapping
    │       ├── xtnsapi.py           # Extension API for external rule development
    │       ├── VBL101.py            # Blank line elimination (readability/compactness)
    │       ├── VBL102.py            # Simple naming conventions (readability/nomenclature)
    │       ├── VBL201.py            # Function ordering (discoverability/navigation)
    │       └── VBL301.py            # Collection type variance (robustness/Postel's Law)

**Rule Package Organization:**

The ``rules/`` subpackage implements the plugin architecture with:

- **Base abstractions**: ``base.py`` contains ``BaseRule`` and common utilities
- **Rule registry**: ``registry.py`` maintains mapping between VBL codes and descriptive names
- **Individual rules**: Each rule in its own VBL-prefixed module following semantic series
- **Extension API**: ``xtnsapi.py`` provides external packages access to rule development utilities
- **Shared imports**: Rules inherit parent imports via ``__.py`` plus rule-specific dependencies

**VBL Rule Naming Convention:**

Rule modules use the **VBL** (malodorous) prefix with semantic series organization:

.. code-block::

    VBL[Series][Number].py where:

    Series:
    - 1XX: Readability (function body compactness, nomenclature clarity)
    - 2XX: Discoverability (function ordering, code navigation)
    - 3XX: Robustness (Postel's Law, type variance, defensive patterns)

    Examples:
    - VBL101: Blank line elimination (readability/compactness)
    - VBL102: Simple naming conventions (readability/nomenclature)
    - VBL201: Function ordering (discoverability/navigation)
    - VBL301: Collection type variance (robustness/Postel's Law)

This system provides:
- **Ruff integration readiness**: Rules like ``VBL101`` clearly identify the malodorous package
- **Semantic organization**: Related rules grouped by conceptual focus
- **Extensibility**: ~99 rules per semantic category with clear progression

**Module Responsibilities:**

.. code-block::

    engine.py           # LinterEngine class, file processing pipeline
    configuration.py    # Configuration discovery, TOML parsing, validation
    reporting.py        # Violation formatting, output channel management
    cli.py             # Argument parsing, file discovery, user interface

    rules/base.py       # BaseRule abstract class, metadata utilities
    rules/registry.py   # Rule registry: VBL codes ↔ descriptive names mapping
    rules/xtnsapi.py    # Extension API for external rule development
    rules/VBL101.py     # REQ-002: Blank line elimination (readability)
    rules/VBL102.py     # REQ-003: Simple naming conventions (readability)
    rules/VBL201.py     # REQ-001: Function ordering (discoverability)
    rules/VBL301.py     # REQ-004: Collection type variance (robustness)

**Rule Registry Design:**

The ``registry.py`` module maintains bidirectional mapping between VBL codes and descriptive information:

.. code-block:: python

    # Example registry structure
    RULE_REGISTRY = {
        "VBL101": {
            "name": "blank-line-elimination",
            "description": "Prohibit blank lines within function bodies",
            "category": "readability",
            "subcategory": "compactness",
            "class": "BlankLineEliminationRule"
        },
        "VBL102": {
            "name": "simple-naming-conventions",
            "description": "Avoid unnecessary underscores in names",
            "category": "readability",
            "subcategory": "nomenclature",
            "class": "SimpleNamingRule"
        },
        # ... etc
    }

    # Configuration support for both formats
    # pyproject.toml can use: VBL101 = false OR blank-line-elimination = false

**Extension API Design:**

The ``xtnsapi.py`` module provides external packages with all necessary imports and utilities to develop custom rules:

.. code-block:: python

    # External package usage example
    from vibelinter.rules.xtnsapi import BaseRule, Violation, libcst, metadata

    class CustomRule(BaseRule):
        rule_id = "EXT001"
        # Implementation using provided utilities

All package modules use the standard ``__`` import pattern as documented
in the common architecture guide.

Component Integration
===============================================================================

CLI Implementation
-------------------------------------------------------------------------------

The command-line interface is organized for maintainability:

.. code-block::

    linter/
    ├── __main__.py      # Entry point: `python -m vibelinter`
    └── cli.py           # CLI implementation and argument parsing

This separation allows the CLI logic to be imported and tested independently
while following Python's standard module execution pattern.

Exception Organization
-------------------------------------------------------------------------------

Package-wide exceptions are centralized in ``sources/vibelinter/exceptions.py``
following the standard hierarchy patterns documented in the `common practices guide
<https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst>`_.

Architecture Evolution
===============================================================================

This filesystem organization provides a foundation that architect agents can
evolve as the project grows. For questions about organizational principles,
subpackage patterns, or testing strategies, refer to the comprehensive common
documentation:

* `Architecture Patterns <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_
* `Development Practices <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst>`_
* `Test Development Guidelines <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst>`_
