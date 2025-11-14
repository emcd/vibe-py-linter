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
   | +--------------------------------------------------------------------------+


*******************************************************************************
003. Configuration Management System
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

The Python linter requires a configuration system to support PRD requirements REQ-005 and REQ-009:

- **Individual rule control**: Enable/disable specific rules per project
- **Severity customization**: Configure error, warning, info levels per rule  
- **Rule parameterization**: Customize thresholds and options (similarity thresholds, type mappings)
- **Project integration**: ``pyproject.toml`` integration for Python ecosystem compatibility
- **Command-line overrides**: Runtime configuration changes without file modification

Analysis of prototype implementations reveals varying approaches to configuration:

1. **Hardcoded constants**: Simple but inflexible (from initial sketches)
2. **TOML-based configuration**: Industry standard with ``pyproject.toml`` integration
3. **Programmatic API**: Code-based configuration for advanced use cases

**Key Requirements:**
- **Zero-configuration operation**: Sensible defaults enable immediate usage
- **Project-specific customization**: Teams can adapt rules to their standards  
- **Configuration discovery**: Automatic location of project configuration files
- **Validation and error handling**: Clear messages for invalid configuration
- **Performance**: Configuration loading shouldn't impact analysis speed
- **User workflow integration**: Non-destructive configuration management preserving user formatting and comments

**Configuration Scope:**
- **Global settings**: Output format, parallel processing options
- **Rule management**: Enable/disable, severity levels, rule-specific parameters
- **Path filtering**: Include/exclude patterns for file discovery  
- **Integration options**: CI/CD behavior, exit code customization

Decision
===============================================================================

We will implement a **layered TOML-based configuration system** with non-destructive user interaction:

**Configuration Sources (precedence order):**
1. Command-line arguments (highest precedence)
2. ``pyproject.toml`` in current directory or parent directories
3. Built-in defaults (lowest precedence)

**Configuration Format:**

.. code-block:: toml

    # pyproject.toml
    [tool.vibelinter]
    # Global settings
    render-as = "text"  # text, json, structured
    display-source = true
    exit-zero = false
    
    # Rule configuration - supports both VBL codes and descriptive names
    [tool.vibelinter.rules]
    VBL101 = true                    # blank-line-elimination
    VBL102 = false                   # simple-naming-conventions  
    VBL201 = true                    # function-ordering
    VBL301 = true                    # collection-type-variance
    
    # Alternative descriptive syntax (mapped via registry)
    blank-line-elimination = true
    simple-naming-conventions = false
    
    # Rule-specific parameters
    [tool.vibelinter.rules.VBL102]       # simple-naming-conventions
    similarity-threshold = 0.85
    allow-digits = true
    
    [tool.vibelinter.rules.VBL301]       # collection-type-variance
    concrete-return-types = ["tuple", "frozenset", "types.MappingProxyType"]
    abstract-param-types = ["collections.abc.Mapping", "collections.abc.Sequence"]
    
    # Severity overrides
    [tool.vibelinter.severity]
    VBL101 = "error"                 # blank-line-elimination
    VBL102 = "info"                  # simple-naming-conventions
    VBL201 = "warning"               # function-ordering
    VBL301 = "warning"               # collection-type-variance

**Configuration Architecture:**

.. code-block:: python

    @dataclass
    class RuleConfiguration:
        enabled: bool = True
        severity: str = "error"  # error, warning, info
        parameters: Dict[str, Any] = field(default_factory=dict)
    
    @dataclass  
    class LinterConfiguration:
        render_as: str = "text"
        display_source: bool = True
        exit_zero: bool = False
        rules: Dict[str, RuleConfiguration] = field(default_factory=dict)
        
        @classmethod
        def load_from_file(cls, path: Path) -> 'LinterConfiguration': ...
        
        @classmethod
        def discover(cls, start_path: Path) -> 'LinterConfiguration': ...

**Implementation Strategy:**

1. **Configuration discovery**: Walk directory tree upward to find ``pyproject.toml``
2. **TOML parsing**: Use Python's ``tomllib`` (3.11+) or ``tomli`` dependency
3. **Validation**: Schema validation with helpful error messages
4. **Rule integration**: Rules receive configuration during instantiation
5. **CLI integration**: Command-line arguments override file-based settings

**User Interaction Model:**

Configuration management through the ``configure`` subcommand uses **non-destructive** approaches:

- **TOML snippet generation**: Generate configuration blocks for manual copying to preserve user formatting and comments
- **Interactive wizard**: Guide users through configuration choices with validation
- **Validation and display**: Show effective configuration from all sources without modification
- **Future destructive mode**: Optional ``--destructive`` flag for direct file modification (with comment loss warning)

Alternatives
===============================================================================

**Alternative 1: JSON Configuration**

Use JSON format for configuration files.

*Rejected because:*
- **No comments support**: TOML allows inline documentation
- **Less human-friendly**: TOML syntax is more readable for configuration  
- **Python ecosystem mismatch**: ``pyproject.toml`` is the standard for Python tools
- **Type limitations**: JSON's limited type system vs. TOML's richer types

**Alternative 2: YAML Configuration**

Use YAML format for configuration files.

*Rejected because:*
- **External dependency**: Requires PyYAML or similar library
- **Complexity overkill**: YAML's advanced features unnecessary for our needs
- **Python ecosystem mismatch**: TOML is preferred for Python tooling
- **Security concerns**: YAML parsing can execute arbitrary code

**Alternative 3: Python Configuration Files**

Use Python modules (e.g., ``linter_config.py``) for configuration.

*Rejected because:*
- **Security risk**: Executing arbitrary Python code for configuration
- **Complexity**: Overkill for simple key-value configuration needs  
- **Tooling integration**: Harder to integrate with editors and other tools
- **Validation difficulty**: No schema validation for Python code

**Alternative 4: INI/ConfigParser Format**

Use Python's built-in INI format and ConfigParser.

*Rejected because:*
- **Limited type support**: No native support for lists, booleans, nested structures
- **Syntax limitations**: Less expressive than TOML for complex configuration
- **Python ecosystem trend**: Modern tools prefer TOML over INI
- **Nesting difficulty**: Complex rule parameters hard to express

**Alternative 5: Direct File Modification**

Modify ``pyproject.toml`` files directly for configuration changes.

*Rejected because:*
- **Comment loss**: TOML libraries don't preserve comments and formatting
- **User experience degradation**: Destroys carefully maintained file structure
- **Version control noise**: Automated formatting changes create meaningless diffs
- **Note**: Future ``--destructive`` flag may enable this with explicit user consent

Consequences
===============================================================================

**Positive Consequences:**

- **Ecosystem integration**: ``pyproject.toml`` is the Python packaging standard
- **Zero-configuration operation**: Built-in defaults enable immediate usage
- **Flexible customization**: Teams can adapt all aspects of rule behavior
- **Clear precedence model**: Command-line overrides file settings with predictable behavior
- **Validation and error handling**: Schema validation provides clear error messages
- **Future extensibility**: TOML format supports additional configuration options
- **User workflow preservation**: Non-destructive management preserves formatting and comments
- **Configuration transparency**: Users can see effective configuration from all sources

**Negative Consequences:**

- **Configuration complexity**: Advanced users may find TOML limiting vs. programmatic APIs
- **Discovery overhead**: Directory traversal adds minor startup cost  
- **TOML dependency**: Requires ``tomli`` dependency for Python <3.11
- **Validation maintenance**: Configuration schema must evolve with rule additions
- **Manual configuration effort**: Non-destructive approach requires manual snippet copying

**Risks and Mitigations:**

- **Risk**: Configuration file discovery impacts performance  
  *Mitigation*: Cache discovered configurations, limit traversal depth

- **Risk**: Invalid configuration causes poor user experience  
  *Mitigation*: Comprehensive validation with helpful error messages and examples

- **Risk**: Configuration schema becomes too complex  
  *Mitigation*: Keep rule parameters simple, provide configuration examples

- **Risk**: Version compatibility issues with TOML parsing  
  *Mitigation*: Pin dependency versions, comprehensive testing

**Implementation Guidelines:**

1. **Default behavior**: All rules enabled with sensible parameters by default
2. **Discovery algorithm**: Search up to 5 parent directories for ``pyproject.toml``
3. **Error handling**: Graceful fallback to defaults with warning messages
4. **Schema evolution**: Maintain backward compatibility, deprecate obsolete options
5. **Documentation**: Comprehensive examples for all configuration options

**Configuration Examples:**

.. code-block:: toml

    # Minimal configuration - disable one rule (VBL code)
    [tool.vibelinter.rules]
    VBL102 = false                   # simple-naming-conventions
    
    # Alternative syntax using descriptive names
    [tool.vibelinter.rules]
    simple-naming-conventions = false
    
    # Advanced configuration - custom parameters
    [tool.vibelinter.rules.VBL102]       # simple-naming-conventions
    similarity-threshold = 0.9
    allow-digits = false
    exceptions = ["_", "__init__", "__call__"]
    
    # Semantic series configuration - disable all readability rules
    [tool.vibelinter.rules]
    VBL101 = false                   # All 1XX series
    VBL102 = false
    # ODR1XX series rules...
    
    # CI/CD integration
    [tool.vibelinter]
    render-as = "json"
    exit-zero = true  # Don't fail builds on warnings

**Dependencies:**

- **Python 3.11+**: Built-in ``tomllib`` module
- **Python 3.10**: ``tomli`` dependency for TOML parsing
- **Validation**: Custom schema validation with clear error reporting