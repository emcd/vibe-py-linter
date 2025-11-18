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

1. **Hub import**: `from . import __` (special case - importing the hub itself)
2. **Relative imports with private aliases**: `from . import exceptions as _exceptions`, `from .base import BaseRule as _BaseRule`
3. **Private aliases for any import**: `from json import loads as _json_loads`
4. **Future imports**: `from __future__ import annotations`

**Exceptions** (modules where all imports are allowed):

1. **`__init__.py` files**: Re-export hubs that define public API
2. **`__.py` files**: Single-file import hub pattern
3. **`<package>/__/imports.py` files**: Directory-based import hub pattern

**Note**: Hub module patterns should be configurable via rule parameters to support project-specific conventions.

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

from json import loads as _json_loads  # OK: private alias

from . import __                       # OK: hub import (special case)
from . import exceptions as _exceptions  # OK: relative import with private alias
from .base import BaseRule as _BaseRule  # OK: relative import with private alias

# Later in code:
path = __.pathlib.Path('foo')      # Using hub
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

Determine if a module is an import hub based on configurable patterns:

```python
def _is_import_hub_module(self) -> bool:
    """Check if current file is an import hub module.

    Hub modules match one of these patterns (configurable):
    1. __init__.py (re-export hubs)
    2. __.py (single-file import hub)
    3. <package>/__/imports.py (directory-based import hub)
    """
    file_path = Path(self.filename)
    filename = file_path.name

    # Pattern 1: __init__.py files
    if filename == '__init__.py':
        return True

    # Pattern 2: __.py files
    if filename == '__.py':
        return True

    # Pattern 3: __/imports.py or any file under __/ directory
    path_parts = file_path.parts
    if '__' in path_parts:
        # Check if it's specifically __/imports.py or any __/ submodule
        try:
            idx = path_parts.index('__')
            # If '__' appears in path, it's a hub module
            return True
        except ValueError:
            pass

    return False
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
    if self._is_allowed_relative_import(node):
        return True
    if self._is_private_alias_import(node):
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

def _is_hub_import(self, node: libcst.ImportFrom) -> bool:
    """Check if import is the hub import itself (from . import __).

    This is a special case that is always allowed.
    """
    # Must be a simple relative import (from .)
    if not node.relative or len(node.relative) != 1:
        return False

    # Module should be None or empty (from . import X, not from .module import X)
    if node.module is not None:
        return False

    # Check if importing '__'
    if isinstance(node.names, libcst.ImportStar):
        return False

    # Should import exactly '__' (may or may not be aliased)
    for name in node.names:
        original_name = name.name.value
        if original_name == '__':
            return True

    return False

def _is_allowed_relative_import(self, node: libcst.ImportFrom) -> bool:
    """Check if import is an allowed relative import.

    Allowed cases:
    1. from . import __  (hub import - special case)
    2. from . import foo as _foo  (private alias)
    3. from .module import name as _name  (private alias)
    """
    # Must be a relative import
    if not node.relative or len(node.relative) == 0:
        return False

    # Special case: from . import __
    if self._is_hub_import(node):
        return True

    # Otherwise, must use private aliases
    return self._is_private_alias_import(node)

def _is_private_alias_import(self, node: libcst.ImportFrom) -> bool:
    """Check if all imported names use private aliases (_name)."""
    # from json import loads as _json_loads  # OK
    # from json import loads                  # Violation
    if isinstance(node.names, libcst.ImportStar):
        return False

    for name in node.names:
        if isinstance(name.asname, libcst.AsName):
            # Has alias, check if private
            alias = name.asname.name.value
            if not alias.startswith('_'):
                return False
        else:
            # No alias, not private
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

### 1. Hub Import Special Case

**Decision**: The hub import itself (`from . import __`) is always allowed, even though it's a relative import without a private alias.

**Implementation**: Detect this specific pattern in `_is_hub_import()` and allow it as a special case.

### 2. Hub Module Patterns

**Decision**: Three patterns identify hub modules (all configurable):
- `__init__.py` files (re-export hubs)
- `__.py` files (single-file import hub)
- Files under `__/` directory (directory-based import hub)

**Implementation**: Check file path against configured patterns in `_is_import_hub_module()`.

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
    "__.py",            # Single-file import hub
    "__/imports.py",    # Directory-based import hub
    "__/*.py",          # Any file under __/ directory
]
```

### Future Configuration Options

```toml
[tool.vibelinter.rules.VBL201]
enabled = true
severity = "warning"

hub_patterns = ["__init__.py", "__.py", "__/imports.py", "__/*.py"]

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

# Test 3: Allowed hub import
"""
from . import __
"""
# Expected: 0 violations

# Test 4: Relative imports - violations without private aliases
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
- [ ] Implement `_is_import_hub_module()` helper (with configurable patterns)
- [ ] Implement `visit_Import()` for simple imports
- [ ] Implement `visit_ImportFrom()` for from imports
- [ ] Implement `_is_future_import()` helper
- [ ] Implement `_is_hub_import()` helper (special case for `from . import __`)
- [ ] Implement `_is_allowed_relative_import()` helper
- [ ] Implement `_is_private_alias_import()` helper
- [ ] Implement `_analyze_collections()` for violation generation
- [ ] Self-register rule in `RULE_DESCRIPTORS`
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

1. **`__init__.py` files are hub modules**
   - **Decision**: All `__init__.py` files are exempt (they're re-export hubs)
   - **Rationale**: They define the public API and need to import from submodules
   - **Configurable**: Yes, via `hub_patterns` configuration

2. **Relative imports require private aliases**
   - **Decision**: `from . import foo` is a violation; must use `from . import foo as _foo`
   - **Exception**: `from . import __` is always allowed (hub import)
   - **Rationale**: Maintains namespace cleanliness and consistency

3. **Hub module patterns are configurable**
   - **Decision**: Support three patterns by default: `__init__.py`, `__.py`, `__/imports.py`
   - **Rationale**: Different projects may use different import hub conventions
   - **Configuration**: Via `hub_patterns` list in rule parameters

4. **TYPE_CHECKING imports**
   - **Initial decision**: Flag as violations
   - **Future enhancement**: Add configuration option to allow
   - **Rationale**: Start strict, relax if needed based on usage

5. **Test files**
   - **Initial decision**: Enforce consistently
   - **Future enhancement**: Add configuration option if needed
   - **Rationale**: Tests should follow the same patterns as production code

6. **Scripts (e.g., `__main__.py`)**
   - **Decision**: Enforce the same rules
   - **Rationale**: Consistency across codebase

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
