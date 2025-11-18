# VBL201: Import Hub Enforcement - Design Document

## Overview

**Rule ID**: VBL201
**Name**: import-hub-enforcement
**Category**: Imports / Architecture
**Priority**: High
**Severity**: warning

## Purpose

Enforce the `__` import hub pattern throughout the codebase by detecting non-private imports in modules that are not designated as import hubs. This rule maintains architectural consistency, prevents namespace pollution, and makes the codebase more self-documenting.

## Background

### The Import Hub Pattern

The project uses a centralized import pattern where common imports are collected in an import hub module (`__/imports.py`), and other modules access these imports via the hub:

```python
# Standard pattern in non-hub modules
from . import __

# Later in code:
path = __.pathlib.Path('foo')
data = __.json.loads(content)
value: __.typx.Any = get_value()
```

This pattern provides several benefits:
- **Namespace cleanliness**: Avoids polluting module namespace with third-party names
- **Centralized control**: All common imports defined in one place
- **Self-documenting**: Clear distinction between hub modules and regular modules
- **Consistency**: Uniform import style across the codebase

### Problem

Without enforcement, developers may inadvertently add direct imports:

```python
# Violation: direct imports in non-hub module
from pathlib import Path
import json
from typing import Any
```

These violations:
- Break architectural consistency
- Create namespace pollution
- Make code harder to refactor
- Were not caught in the previous session, leading to manual fixes

## Rule Specification

### What to Detect

**Violations** (in non-hub modules):

1. **Standard library imports**: `import json`, `from pathlib import Path`
2. **Third-party imports**: `from requests import get`, `import numpy`
3. **Direct public imports**: Any import that brings non-private names into module namespace

**Allowed** (in non-hub modules):

1. **Private imports**: Any import where the resulting name starts with `_`
   - `from . import __` (name starts with `_`)
   - `from . import exceptions as _exceptions` (alias starts with `_`)
   - `from json import loads as _json_loads` (alias starts with `_`)
2. **Future imports**: `from __future__ import annotations`

**Exceptions** (modules where all imports are allowed):

Hub modules are identified by configurable glob patterns. Any file matching these patterns is exempt from import restrictions. Default patterns:
- `__init__.py` - Re-export modules
- `__main__.py` - Entry point modules
- `__.py` - Single-file import hub
- `__/imports.py` - Directory-based import hub

### Examples

#### ❌ Violations

```python
# sources/vibelinter/cli.py
from pathlib import Path          # VBL201: Use __.pathlib.Path or private alias
import json                       # VBL201: Use __.json or private alias
from typing import Any            # VBL201: Use __.typx.Any or private alias
from requests import get          # VBL201: Use hub or private alias

# Relative imports without private aliases are also violations:
from . import exceptions          # VBL201: Use 'from . import exceptions as _exceptions'
from .base import BaseRule        # VBL201: Use 'from .base import BaseRule as _BaseRule'
```

#### ✅ Correct Usage

```python
# sources/vibelinter/cli.py
from __future__ import annotations  # OK: future import

from json import loads as _json_loads  # OK: private alias (starts with _)

from . import __ as _hub                       # OK: private alias (starts with _)
from . import __                               # OK: private name (__ starts with _)
from . import exceptions as _exceptions        # OK: private alias (starts with _)
from .base import BaseRule as _BaseRule        # OK: private alias (starts with _)

# Later in code:
path = __.pathlib.Path('foo')      # Using private import __
data = _json_loads(content)        # Using private alias
error = _exceptions.LinterError()  # Using private relative import
```

#### ✅ Exception: Hub Modules

```python
# Pattern 1: sources/vibelinter/__/imports.py
from pathlib import Path           # OK: hub module
import json                        # OK: hub module
from typing import Any             # OK: hub module

# Pattern 2: sources/vibelinter/__.py
from pathlib import Path           # OK: hub module (single-file pattern)

# Pattern 3: sources/vibelinter/__init__.py
from .engine import LinterEngine   # OK: re-export module
from .cli import main              # OK: re-export module
```

## Implementation Design

### High-Level Approach

1. **Identification Phase**: Determine if the current file is an import hub module
2. **Collection Phase**: Visit all import statements and collect violations
3. **Analysis Phase**: Generate violations for disallowed imports

### Technical Details

#### Module Classification

Determine if a module is an import hub using configurable glob patterns:

```python
from pathlib import Path

def _is_import_hub_module(self) -> bool:
    """Check if current file matches any hub module pattern.

    Uses glob patterns from configuration (e.g., '__init__.py', '__.py',
    '__/imports.py', '__/*.py'). Matches against both the filename and
    the full relative path.
    """
    file_path = Path(self.filename)

    # Get hub patterns from rule configuration
    # Default: ['__init__.py', '__main__.py', '__.py', '__/imports.py']
    hub_patterns = self._get_hub_patterns()

    for pattern in hub_patterns:
        # Try matching against filename
        if file_path.match(pattern):
            return True

        # Try matching against relative path components
        # This handles patterns like '__/*.py'
        if file_path.match(f'*/{pattern}'):
            return True

    return False

def _get_hub_patterns(self) -> list[str]:
    """Get hub module patterns from rule configuration."""
    # Access rule_parameters from configuration
    # Default patterns if not configured
    return getattr(self, '_hub_patterns', [
        '__init__.py',
        '__main__.py',
        '__.py',
        '__/imports.py',
    ])
```

#### Import Statement Analysis

Visit and analyze different import types:

1. **Simple imports**: `import json`
   - Check if module is from stdlib or third-party
   - Report violation if not in hub module

2. **From imports**: `from pathlib import Path`
   - Check if it's a relative import (`from .`)
   - Check if it's a future import (`from __future__`)
   - Check if imported names are private (start with `_`)
   - Report violation for public imports

3. **Position tracking**:
   - Use LibCST PositionProvider for accurate line/column
   - Extract import statement text for clear messaging

#### CST Visitor Methods

```python
def visit_Import(self, node: libcst.Import) -> bool:
    """Visit simple import statements (import foo)."""
    # Skip if this is a hub module
    if self._is_hub_module:
        return True

    # Collect for later analysis
    self._simple_imports.append(node)
    return True

def visit_ImportFrom(self, node: libcst.ImportFrom) -> bool:
    """Visit from imports (from foo import bar)."""
    # Skip if this is a hub module
    if self._is_hub_module:
        return True

    # Check for allowed patterns
    if self._is_future_import(node):
        return True
    if self._has_private_names(node):
        return True

    # Collect violation
    self._from_imports.append(node)
    return True
```

#### Helper Methods

```python
def _is_future_import(self, node: libcst.ImportFrom) -> bool:
    """Check if import is from __future__."""
    module = node.module
    if isinstance(module, libcst.Attribute):
        return False
    return module and module.value == '__future__'

def _has_private_names(self, node: libcst.ImportFrom) -> bool:
    """Check if all imported names are private (start with _).

    Allowed examples:
    - from . import __  (__ starts with _)
    - from . import exceptions as _exceptions  (alias starts with _)
    - from json import loads as _json_loads  (alias starts with _)

    Violations:
    - from . import exceptions  (exceptions doesn't start with _)
    - from pathlib import Path  (Path doesn't start with _)
    - from pathlib import Path as P  (P doesn't start with _)
    """
    # Star imports are never private
    if isinstance(node.names, libcst.ImportStar):
        return False

    # Check each imported name
    for name in node.names:
        # Determine the resulting name in the module namespace
        if isinstance(name.asname, libcst.AsName):
            # Has alias - check if alias is private
            resulting_name = name.asname.name.value
        else:
            # No alias - check if original name is private
            resulting_name = name.name.value

        # Must start with underscore to be private
        if not resulting_name.startswith('_'):
            return False

    return True
```

#### Analysis and Reporting

```python
def _analyze_collections(self) -> None:
    """Analyze collected imports and report violations."""
    for node in self._simple_imports:
        self._report_simple_import_violation(node)

    for node in self._from_imports:
        self._report_from_import_violation(node)

def _report_simple_import_violation(self, node: libcst.Import) -> None:
    """Report violation for simple import statement."""
    module_name = self._extract_module_name(node)
    message = (
        f"Direct import of '{module_name}'. "
        f"Use import hub (__.{module_name}) or private alias."
    )
    self._produce_violation(node, message, severity='warning')

def _report_from_import_violation(self, node: libcst.ImportFrom) -> None:
    """Report violation for from import statement."""
    module_name = self._extract_from_module_name(node)
    imported_names = self._extract_imported_names(node)

    message = (
        f"Direct import from '{module_name}'. "
        f"Use import hub or private aliases (_name)."
    )
    self._produce_violation(node, message, severity='warning')
```

### Data Structures

```python
class VBL201(BaseRule):
    """Enforces import hub pattern for non-hub modules."""

    def __init__(self, filename: str, wrapper: MetadataWrapper, source_lines: tuple[str, ...]) -> None:
        super().__init__(filename, wrapper, source_lines)

        # Classification
        self._is_hub_module: bool = self._is_import_hub_module()

        # Collections
        self._simple_imports: list[libcst.Import] = []
        self._from_imports: list[libcst.ImportFrom] = []
```

## Edge Cases and Special Handling

### 1. Hub Module Pattern Matching

**Decision**: Hub modules are identified using configurable glob patterns, not hard-coded checks.

**Implementation**: Use `Path.match()` to check if the current file matches any pattern in the `hub_patterns` configuration list. Supports standard glob syntax like `*.py`, `__/*.py`, etc.

**Default patterns**:
- `__init__.py` - Exact filename match (re-export modules)
- `__main__.py` - Exact filename match (entry point modules)
- `__.py` - Exact filename match (single-file import hub)
- `__/imports.py` - Relative path match (directory-based import hub)

### 2. Private Name Definition

**Decision**: A name is private if and only if it starts with underscore (`_`).

**Examples**:
- `__` is private (starts with `_`)
- `_foo` is private (starts with `_`)
- `foo` is NOT private
- `Foo` is NOT private

**Implementation**: Check `resulting_name.startswith('_')` where `resulting_name` is the alias if present, otherwise the imported name.

### 3. Test Files

**Decision**: Initial implementation will enforce the same rules for test files.

**Future**: May add configuration option to relax rules for test files if needed.

### 4. Multiple Imports Per Statement

```python
from typing import Any, Dict, List  # All should be flagged
```

**Implementation**: Iterate through all names in the import and generate appropriate messages.

### 5. Star Imports

```python
from typing import *  # Should be flagged
```

**Implementation**: Detect `ImportStar` and report violation (this overlaps with potential VBL202).

### 6. Import Aliases Without Privacy

```python
from pathlib import Path as P  # Public alias, should be flagged
from pathlib import Path as _Path  # Private alias, OK
```

**Implementation**: Check alias name prefix in `_is_private_alias_import`.

### 7. Conditional Imports

```python
if TYPE_CHECKING:
    from typing import Protocol  # May need special handling
```

**Decision**: Initial implementation treats these as violations. Future enhancement could detect `TYPE_CHECKING` blocks and allow them.

## Configuration Options

### Default Configuration

```toml
[tool.vibelinter.rules.VBL201]
enabled = true
severity = "warning"

# Hub module patterns (configurable)
# These patterns identify modules that are exempt from import restrictions
hub_patterns = [
    "__init__.py",      # Re-export modules
    "__main__.py",      # Entry point modules
    "__.py",            # Single-file import hub
    "__/imports.py",    # Directory-based import hub
]
```

### Future Configuration Options

```toml
[tool.vibelinter.rules.VBL201]
enabled = true
severity = "warning"

hub_patterns = ["__init__.py", "__main__.py", "__.py", "__/imports.py"]

# Future: Allow certain stdlib modules without hub
allowed_modules = []

# Future: Relax rules for test files
exclude_test_files = false

# Future: Allow TYPE_CHECKING imports
allow_type_checking_imports = false
```

## Testing Strategy

### Unit Tests

1. **Hub module detection**: Verify `_is_import_hub_module` correctly identifies hub modules
2. **Import classification**: Test `_is_future_import`, `_is_relative_import`, `_is_private_alias_import`
3. **Violation detection**: Test each violation scenario
4. **Exception handling**: Verify hub modules and re-export modules are excluded

### Integration Tests

1. **Full file analysis**: Test complete Python files with mixed imports
2. **Real codebase**: Run against `sources/vibelinter/` to ensure self-hosting
3. **Configuration**: Test with different configuration options

### Test Cases

```python
# Test 1: Simple import violation
"""
import json
"""
# Expected: 1 violation

# Test 2: From import violation
"""
from pathlib import Path
"""
# Expected: 1 violation

# Test 3: Allowed private imports (__ is just another private name)
"""
from . import __
from . import _utils
"""
# Expected: 0 violations (both __ and _utils start with _)

# Test 4: Relative imports - violations without private names
"""
from . import exceptions
from .base import BaseRule
"""
# Expected: 2 violations

# Test 4b: Allowed relative imports with private aliases
"""
from . import exceptions as _exceptions
from .base import BaseRule as _BaseRule
"""
# Expected: 0 violations

# Test 5: Allowed private alias
"""
from json import loads as _json_loads
"""
# Expected: 0 violations

# Test 6: Hub module exception
"""
# File: sources/vibelinter/__/imports.py
from pathlib import Path
import json
"""
# Expected: 0 violations

# Test 7: Mixed imports
"""
from __future__ import annotations
from json import loads as _json_loads
from . import __
from . import exceptions  # Violation: no private alias
from pathlib import Path  # Violation
"""
# Expected: 2 violations

# Test 8: Hub module with all patterns
"""
# File: sources/vibelinter/__init__.py
from .engine import LinterEngine
from typing import Any
"""
# Expected: 0 violations (all imports allowed in hub modules)
```

## Implementation Checklist

- [ ] Create `sources/vibelinter/rules/implementations/vbl201.py`
- [ ] Implement `VBL201` class inheriting from `BaseRule`
- [ ] Implement `_is_import_hub_module()` using glob pattern matching
- [ ] Implement `_get_hub_patterns()` to access configuration
- [ ] Implement `visit_Import()` for simple imports
- [ ] Implement `visit_ImportFrom()` for from imports
- [ ] Implement `_is_future_import()` helper
- [ ] Implement `_has_private_names()` helper (checks if names start with `_`)
- [ ] Implement `_analyze_collections()` for violation generation
- [ ] Self-register rule in `RULE_DESCRIPTORS` with default `hub_patterns`
- [ ] Create comprehensive unit tests
- [ ] Test against actual codebase (self-hosting)
- [ ] Update documentation if needed

## Success Criteria

1. **Detects violations**: Successfully identifies direct imports in non-hub modules
2. **Allows exceptions**: Correctly allows hub imports, relative imports, and private aliases
3. **Hub modules exempt**: Import hub modules can have any imports
4. **Clear messages**: Violation messages are actionable and clear
5. **Self-hosting**: Rule passes when run against the linter's own codebase
6. **Performance**: Minimal overhead during CST traversal

## Future Enhancements

1. **Auto-fix capability**: Automatically convert direct imports to hub pattern
2. **Smarter detection**: Recognize common patterns like `TYPE_CHECKING` blocks
3. **Custom exceptions**: Allow projects to configure module-specific exceptions
4. **Import optimization**: Suggest removing unused hub imports
5. **Integration with VBL202**: Coordinate with star import detection

## References

- **Rule ideas**: `.auxiliary/notes/rule-ideas.md`
- **Python practices**: `.auxiliary/instructions/practices-python.rst` (Import Organization section)
- **Base rule**: `sources/vibelinter/rules/base.py`
- **Example implementation**: `sources/vibelinter/rules/implementations/vbl101.py`
- **Architecture**: `documentation/architecture/summary.rst`

## Design Decisions and Rationale

1. **Private name definition is simple**
   - **Decision**: A name is private if and only if it starts with `_`
   - **Applies to**: `__`, `_foo`, `___bar`, etc.
   - **Rationale**: Simple, consistent rule with no special cases
   - **Note**: `__` is not special - it's just another private name

2. **Hub modules identified by configurable glob patterns**
   - **Decision**: Use file glob patterns, not hard-coded checks
   - **Default patterns**: `__init__.py`, `__main__.py`, `__.py`, `__/imports.py`
   - **Rationale**: Projects may use different conventions; configuration allows flexibility
   - **Implementation**: Uses `Path.match()` for pattern matching
   - **Entry points**: `__main__.py` treated as hub module since they serve as module boundaries

3. **All imports must result in private names (in non-hub modules)**
   - **Decision**: Any import that brings a public name into module namespace is a violation
   - **Allowed**: `from . import __`, `from . import foo as _foo`, `from json import loads as _json_loads`
   - **Violations**: `from . import foo`, `from pathlib import Path`, `import json`
   - **Rationale**: Maintains namespace cleanliness and architectural consistency

4. **TYPE_CHECKING imports**
   - **Initial decision**: Flag as violations (unless using private names)
   - **Future enhancement**: Add configuration option to allow non-private imports in TYPE_CHECKING blocks
   - **Rationale**: Start strict, relax if needed based on usage

5. **Test files**
   - **Initial decision**: Enforce consistently
   - **Future enhancement**: Add glob pattern to exclude test files if needed
   - **Rationale**: Tests should follow the same patterns as production code

6. **Scripts and entry points**
   - **Decision**: Enforce the same rules unless matched by hub patterns
   - **Rationale**: Consistency across codebase; can be exempted via configuration if needed

## Implementation Notes

### LibCST Node Types

- `libcst.Import`: Simple import statements (`import foo`)
- `libcst.ImportFrom`: From import statements (`from foo import bar`)
- `libcst.ImportStar`: Star imports (`from foo import *`)
- `libcst.Attribute`: Dotted module names (`from foo.bar import baz`)

### Position Extraction

Use `PositionProvider` metadata for accurate line/column reporting:

```python
position = self.wrapper.resolve(libcst.metadata.PositionProvider)[node]
line = position.start.line
column = position.start.column + 1  # Convert to 1-indexed
```

### Import Name Extraction

```python
# Simple import: import foo.bar.baz
module_name = node.names[0].name.value

# From import: from foo.bar import baz
if isinstance(node.module, libcst.Attribute):
    # Handle dotted names
    module_name = self._extract_dotted_name(node.module)
else:
    module_name = node.module.value
```

## Revision History

- **2025-11-18 (v1)**: Initial design document created
- **2025-11-18 (v2)**: Updated with corrected understanding:
  - Relative imports require private aliases (except `from . import __`)
  - Hub module patterns clarified: `__init__.py`, `__.py`, `__/imports.py`
  - Added configurable `hub_patterns` parameter
  - Updated examples and test cases to reflect corrections
  - Renamed `_is_relative_import` to `_is_allowed_relative_import`
  - Added `_is_hub_import` helper for special case detection
- **2025-11-18 (v3)**: Final simplification based on feedback:
  - **`__` is not special**: Just another private name (starts with `_`)
  - **No hard-coded patterns**: Use glob pattern matching from configuration
  - Removed `_is_hub_import` - no special case needed
  - Simplified to `_has_private_names()` - single rule for all imports
  - Hub modules identified by `Path.match()` against configurable patterns
  - Updated all examples and design to reflect simpler model
