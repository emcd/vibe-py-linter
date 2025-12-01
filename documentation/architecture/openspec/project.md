# Project Context

## Purpose
**emcd-vibe-linter** is a specialized Python linter designed to enforce code quality rules that are often overlooked by standard tools like Ruff, Pylint, or Flake8. It specifically targets:
- **Code Structure:** Enforcing function ordering (e.g., public before private).
- **Naming Conventions:** Disallowing unnecessary underscores while handling disambiguation.
- **Type Signatures:** Enforcing specific patterns for collection types (abstract for parameters, concrete for returns).
- **Whitespace:** Eliminating blank lines within function bodies for compactness.

The goal is to promote maintainable, readable, and consistent Python code through configurable, incremental rule adoption.

## Tech Stack
- **Language:** Python 3.10+
- **Parsing & Analysis:** [LibCST](https://github.com/Instagram/LibCST) (Concrete Syntax Tree parsing)
- **CLI Framework:** [Tyro](https://github.com/brentyi/tyro) (via `emcd-appcore`)
- **Configuration:** TOML (via `tomli`)
- **Build System:** Hatch
- **Testing:** Pytest, Sphinx (doctests)
- **Internal Libraries:**
    - `absence`: Sentinel values.
    - `accretive`: Accretive data structures.
    - `classcore`: Class factories/decorators.
    - `dynadoc`: Documentation generation.
    - `frigid`: Immutable data structures.
    - `emcd-appcore`: CLI application scaffolding.

## Project Conventions

### Code Style
- **Spacing:**
    - Spaces around function arguments: `func( arg )`
    - Spaces inside brackets/braces: `[ 1, 2 ]`, `{ 'key': val }`
- **Imports:** Use of `from . import __` pattern (central import hub).
- **Typing:** Extensive use of type hints, including `__.typx.Annotated`.
- **Immutability:** Preference for immutable data structures (`frigid`, `accretive`).
- **Naming:**
    - `VBLxxx` for rule codes.
    - Descriptive variable/function names.

### Architecture Patterns
- **Engine-Based:** A central `Engine` orchestrates the analysis.
- **Rule Registry:** Rules are registered and instantiated dynamically via `RuleRegistryManager`.
- **Visitor Pattern:** Rules are implemented as LibCST visitors (`wrapper.visit( rule )`).
- **Configuration:** Hierarchical configuration (CLI > Config File > Defaults).

### Testing Strategy
- **Unit Tests:** `pytest` for core logic and rules.
- **Doctests:** Embedded in documentation/docstrings, run via Sphinx.
- **Coverage:** 100% coverage goal enforced via `coverage-pytest`.

### Git Workflow
- **Branching:** Feature branches merged to `master`.
- **Commits:** `<Topic>: ...` format.
- **Changelog:** Managed via `towncrier`.

## Domain Context
- **CST (Concrete Syntax Tree):** Represents the code exactly as written, including whitespace and comments, unlike an AST.
- **Rule:** A specific check with a unique ID (e.g., `VBL101`).
- **Violation:** A detected issue with line/column information.
- **Context:** Surrounding lines of code to help identify the issue.

## Important Constraints
- **Python Version:** Strictly 3.10 and above.
- **Performance:** Must process 1000 lines < 1000ms.
- **No Code Execution:** The linter analyzes code statically; it never executes the user's code.

## External Dependencies
- **PyPI:** Primary source for dependencies.
- **GitHub Actions:** For CI/CD.
