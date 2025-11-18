*******************************************************************************
Test Organization Summary
*******************************************************************************

This document describes the test module numbering scheme and organization
conventions specific to the vibelinter project.

Test Module Numbering Scheme
===============================================================================

vibelinter follows a hierarchical numbering system where test modules are
organized by architectural layer:

Module Number Assignments
-------------------------------------------------------------------------------

* **000-099**: Package internals and utilities

  * ``test_000_package.py`` - Package-level sanity checks
  * ``test_010_base.py`` - Internal utilities and common imports

* **100-199**: Core rule infrastructure

  * ``test_100_violations.py`` - Violation data structures
  * ``test_110_context.py`` - Rule context management
  * ``test_120_base.py`` - Base rule framework
  * ``test_130_registry.py`` - Rule registry and discovery

* **200-299**: Rule implementations (subpackage)

  * ``test_210_rules_vbl101.py`` - VBL101 rule tests
  * ``test_220_rules_vbl201.py`` - VBL201 import hub enforcement tests

* **300-399**: Configuration and parsing

  * ``test_300_configuration.py`` - Configuration loading and validation

* **400-499**: Analysis engine

  * ``test_400_engine.py`` - Linting engine core functionality

* **500-599**: CLI interface

  * ``test_500_cli.py`` - Command-line interface

Test Function Numbering
===============================================================================

Within each test module, test functions use a separate numbering scheme:

* **000-099**: Basic functionality tests
* **100-199**: First component/feature tests
* **200-299**: Second component/feature tests
* **300-399**: Third component/feature tests
* And so on...

Related tests within a component block can be separated by 10 or 20 for
logical grouping.

Project-Specific Conventions
===============================================================================

Test Data Organization
-------------------------------------------------------------------------------

Test data is organized under ``tests/data/`` with the following structure:

* ``tests/data/snippets/`` - Python code snippets for rule testing

  * ``valid/`` - Valid code that should not trigger violations
  * ``invalid/`` - Invalid code that should trigger violations
  * Each snippet is a minimal, focused example

Fixtures and Utilities
-------------------------------------------------------------------------------

Common fixtures are defined in:

* ``tests/test_000_vibelinter/fixtures.py`` - Shared fixtures
* ``tests/test_000_vibelinter/__.py`` - Common test utilities

Rule Testing Pattern
-------------------------------------------------------------------------------

Rules are tested using a consistent pattern:

1. **Basic functionality** (000-099): Rule instantiation, basic detection
2. **Positive cases** (100-199): Valid code that should pass
3. **Negative cases** (200-299): Invalid code that should fail
4. **Edge cases** (300-399): Boundary conditions, complex scenarios
5. **Configuration** (400-499): Configuration parsing and defaults

Rationale for Exceptions
===============================================================================

Currently, no exceptions to standard testing patterns are required.

Updates Log
===============================================================================

* 2025-11-18: Initial test organization document created
* 2025-11-18: Planned VBL201 test module as ``test_220_rules_vbl201.py``
