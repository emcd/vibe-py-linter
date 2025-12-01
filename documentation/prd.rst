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
Product Requirements Document
*******************************************************************************

Executive Summary
===============================================================================

A custom Python linter to enforce specialized code quality rules that are not covered by existing linters like Ruff, Pylint, or Flake8. The linter focuses on detecting code smells related to structural organization, naming conventions, and type signature patterns that promote maintainable, readable Python code. The tool will provide incremental rule implementation, allowing teams to adopt and customize rules based on their specific coding standards.

Problem Statement
===============================================================================

Current Python linters excel at detecting syntax errors, common bugs, and standard style violations, but they lack support for organization-specific rules that can significantly impact code maintainability:

**Who experiences the problem**: Python development teams and individual developers who want to enforce custom coding standards beyond what existing linters provide.

**When and where it occurs**: During code review processes, when maintaining large codebases, and when onboarding new team members who need to learn project-specific conventions.

**Impact and consequences**:
- Inconsistent code organization makes codebases harder to navigate
- Manual enforcement of custom rules during code reviews is time-consuming and error-prone
- Lack of automated feedback for domain-specific patterns leads to technical debt accumulation
- Teams cannot enforce their specific preferences for function ordering, naming, and type usage

**Current limitations**: Existing linters are not designed to handle:
- Complex function ordering rules with context-aware exceptions
- Sophisticated naming convention analysis requiring disambiguation logic
- Type variance rules that distinguish between parameter and return type requirements
- Fine-grained whitespace rules within function bodies

Goals and Objectives
===============================================================================

**Primary Objectives (Critical)**:
- Create a working linter that can analyze Python code structure
- Implement four core linting rules with configurable severity levels
- Provide clear, actionable error messages with precise line/column positions
- Enable incremental adoption of rules

**Secondary Objectives (High)**:
- Support configuration files for rule customization with non-destructive management
- Integrate with popular development environments and CI/CD pipelines  
- Provide auto-fix capabilities for certain rule violations with safety controls
- Maintain good performance on large codebases with parallel processing support
- Enable rule discovery and documentation through dedicated subcommands

**Success Metrics**:
- Performance: Process 1000 lines of Python code in <1000ms
- User adoption: Enable teams to customize at least 2 rules for their workflow
- Maintainability: Add new rules without modifying core engine

Target Users
===============================================================================

**Primary Users**:
- Python developers working on medium to large codebases (1000+ lines)
- Development teams with established coding standards
- Technical leads responsible for code quality enforcement

**Technical Proficiency**: Users are experienced Python developers comfortable with command-line tools and configuration files.

**Usage Contexts**:
- Local development environment integration
- CI/CD pipeline quality gates
- Pre-commit hooks
- Code review automation

Functional Requirements
===============================================================================

**REQ-001: Function Ordering Rule (Critical)**
As a developer, I want functions to be ordered with public functions (alphabetically sorted) followed by private functions (alphabetically sorted), so that code organization is consistent and navigable.

Acceptance Criteria:
- Detect when public functions appear after private functions
- Allow private functions used as default arguments to appear early (exception handling)
- Verify alphabetical sorting within public and private function groups
- Support both module-level and class method analysis
- Provide specific error messages indicating expected order

**REQ-002: Blank Line Elimination Rule (Critical)**
As a developer, I want to prohibit blank lines within function bodies, so that function implementations remain compact and focused.

Acceptance Criteria:
- Detect any empty lines within function body statements
- Distinguish between function body content and inter-function spacing
- Handle nested functions appropriately
- Ignore blank lines in docstrings and multi-line strings
- Report exact line numbers of violations

**REQ-003: Simple Naming Convention Rule (High)**
As a developer, I want to avoid unnecessary underscores in names unless needed for disambiguation, so that code remains readable while preventing naming conflicts.

Acceptance Criteria:
- Flag underscores in argument, variable, and attribute names
- Implement disambiguation logic using fuzzy string matching
- Allow underscores for Python conventions (private members, dunder methods)
- Consider keyword conflicts and builtin name collisions
- Support configurable similarity thresholds for disambiguation

**REQ-004: Collection Type Variance Rule (High)**
As a developer, I want function parameters to use abstract collection types and return values to use concrete collection types, so that interfaces are flexible and implementations are specific.

Acceptance Criteria:
- Detect concrete collection types in parameter annotations (list, dict, set, tuple)
- Recommend abstract alternatives (collections.abc.Mapping, Sequence, etc.)
- Flag abstract collection types in return annotations
- Suggest concrete immutable alternatives (tuple, frozenset, MappingProxyType)
- Handle complex type annotations including generics and unions

**REQ-005: Rule Documentation and Discovery (Medium)**
As a developer, I want to easily discover and understand available linting rules, so that I can configure the linter effectively for my project.

Acceptance Criteria:
- Provide 'describe' subcommand for rule information and documentation
- Support 'describe rules' to list all available rules with descriptions
- Support 'describe rule VBL101' for detailed rule information with examples
- Display rule parameters and configuration options
- Show rule status in current configuration context
- Include usage examples and common configuration patterns

**REQ-006: Command Line Interface (Critical)**
As a developer, I want a command-line interface for running the linter, so that it integrates with existing development workflows.

Acceptance Criteria:
- Support verb-based subcommand structure: check (default), fix, configure, describe, serve
- Accept file paths and directory arguments with recursive directory scanning
- Provide output formatting options (text, JSON, structured)
- Support rule selection via --select parameter (e.g., --select VBL101,VBL201)
- Support parallel processing with --jobs parameter (default: auto)
- Return appropriate exit codes (0=clean, 1=violations, 2+=errors)
- Display help and usage information for all subcommands
- Honor .gitignore files by default for file discovery

**REQ-007: Error Reporting (Critical)**
As a developer, I want clear, actionable error messages with precise locations, so that I can quickly understand and fix violations.

Acceptance Criteria:
- Report exact line and column numbers
- Include rule identifier and descriptive message
- Suggest specific fixes when possible
- Group violations by file and rule type
- Support multiple output formats (text, JSON, structured)
- Support configurable context display showing lines before/after violations
- Provide --context flag to show 2+ lines around violations with line numbers
- Maintain deterministic output ordering sorted by filename for consistent CI/CD behavior

**REQ-008: Auto-Fix Capabilities (High)**
As a developer, I want automated fix capabilities for certain rule violations, so that I can quickly resolve issues without manual intervention.

Acceptance Criteria:
- Provide separate 'fix' subcommand with safety controls
- Support --simulate flag to preview changes without applying them
- Support --diff-format option (unified, context) for change visualization
- Implement safety classification: safe fixes vs dangerous fixes requiring --apply-dangerous
- Allow selective fixing via --select parameter for specific rules
- Preserve original file formatting and structure when possible
- Handle fix conflicts and provide clear error messages

**REQ-009: Configuration Management (Medium)**
As a user, I want streamlined configuration management without destructive file editing, so that I can easily customize the linter for my project needs.

Acceptance Criteria:
- Provide 'configure' subcommand for configuration management
- Generate TOML configuration snippets for manual addition to pyproject.toml
- Support interactive configuration wizard for initial setup
- Validate existing configuration and display effective merged settings
- Support --validate flag to check configuration without running analysis
- Follow configuration precedence: CLI args > pyproject.toml > user config > defaults
- Provide clear error messages for invalid configuration with problem location

Non-Functional Requirements
===============================================================================

**Performance Requirements**:
- Process 1000 lines of Python code in under 1000ms on standard development hardware
- Memory usage should not exceed 100MB for typical codebases (10,000 lines)
- Support parallel processing for directory analysis

**Scalability Requirements**:
- Handle individual files up to 10,000 lines without performance degradation
- Support projects with 100+ Python files
- Maintain consistent performance as rule count increases

**Compatibility Requirements**:
- Support Python 3.10+
- Compatible with major operating systems (Windows, macOS, Linux)
- CI/CD system compatibility (GitHub Actions, GitLab CI, Jenkins)

**Reliability Requirements**:
- Handle malformed Python code gracefully without crashing
- Provide meaningful error messages for parsing failures
- Maintain backward compatibility across minor version updates

**Usability Requirements**:
- Installation via pip in under 30 seconds
- Zero-configuration operation with sensible defaults
- Clear documentation with examples for each rule
- Migration guide for teams adopting the tool

**Security Requirements**:
- No execution of analyzed code
- Safe handling of file system operations
- Input validation for configuration files

Constraints and Assumptions
===============================================================================

**Technical Constraints**:
- Python 3.10+ requirement
- Single-threaded analysis per file initially

**Development Constraints**:
- Incremental development approach - rules implemented individually
- Focus on analysis rather than code transformation initially
- Command-line tool before IDE integration

**Dependencies**:
- Python syntax tree analysis library
- Standard library modules for configuration and file handling
- Optional dependencies for advanced features (colorama for colored output)

**Assumptions**:
- Users are familiar with Python development practices
- Code being analyzed follows basic Python syntax rules
- Development teams have established preferences for the rules being enforced
- Integration environments support Python package installation
- Target Python version is 3.10 or higher

Out of Scope
===============================================================================

**Explicitly excluded from initial implementation**:

- Auto-fixing capabilities (future enhancement)
- Real-time editor integration beyond basic error reporting
- Integration with popular editors (VS Code, PyCharm, Vim, Emacs)
- Support for Python versions below 3.10
- Analysis of dynamically generated code
- Integration with type checkers like mypy or pyright
- Web-based configuration interfaces
- Support for languages other than Python
- Advanced metrics and code complexity analysis
- Git integration for differential analysis
- Performance profiling and optimization suggestions

**Future considerations** (not in current scope):
- Language server protocol implementation via 'serve lsp' subcommand
- Model Context Protocol server implementation via 'serve mcp' subcommand  
- Integration with popular editors (VS Code, PyCharm, Vim, Emacs)
- Integration with popular linting aggregators
- GitHub Actions annotations output format
- Advanced fix safety classifications and per-rule safety models
- Machine learning-based rule suggestions
- Team analytics and violation trending
- Custom rule development framework