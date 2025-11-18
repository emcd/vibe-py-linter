# Rule Ideas and Future Enhancements

## Proposed Rules for Implementation

### VBL201 - Import Hub Enforcement (RECOMMENDED NEXT)

**Category**: Imports / Architecture
**Priority**: High

**Description**: Enforce the `__` import hub pattern by detecting non-private imports in modules that are not designated as import hubs.

**Rationale**:
- Maintains architectural consistency across the codebase
- Prevents namespace pollution in API modules
- Self-documenting code through explicit import hub usage
- Would have caught the inline import issue from this session

**Examples**:

❌ **Violation** (in regular module):
```python
# sources/vibelinter/cli.py
from pathlib import Path  # Should use __.pathlib.Path
import json               # Should use __.json
from typing import Any    # Should use __.typx.Any
```

✅ **Correct**:
```python
# sources/vibelinter/cli.py
from . import __

# Later in code:
path = __.pathlib.Path('foo')
data = __.json.loads(content)
value: __.typx.Any = get_value()
```

✅ **Exception** (import hub modules):
```python
# sources/vibelinter/__/imports.py - This IS a hub
from pathlib import Path  # OK - this is an import hub
import json               # OK - this is an import hub
```

**Implementation Notes**:
- Need to identify which modules are import hubs (look for `__/imports.py` pattern)
- Should allow `from . import __` (the hub import itself)
- Should allow relative imports like `from . import exceptions as _exceptions`
- Should flag: `import <stdlib>`, `from <stdlib> import`, `from <third-party> import`
- Could check for private aliases (e.g., `from tomli import loads as _toml_loads` at module top)

**Edge Cases**:
- Import hubs themselves (`sources/vibelinter/__/imports.py`)
- `__init__.py` files that are re-export hubs
- Test files (may have different patterns)

---

### VBL102 - Unnecessary Comments in Function Bodies

**Category**: Code Style / Vertical Compactness
**Priority**: Medium

**Description**: Detect single-line comments within function bodies that are not TODO markers, URLs, or part of multi-line comment blocks.

**Rationale**:
- Enforces vertical compactness philosophy (complements VBL101)
- Code should be self-documenting through clear naming
- Comments in function bodies often indicate code smell
- Docstrings and type hints should make inline comments unnecessary

**Examples**:

❌ **Violation**:
```python
def process_data(items):
    # Initialize the counter
    count = 0
    # Process each item
    for item in items:
        count += 1
    # Return the result
    return count
```

✅ **Correct**:
```python
def process_data(items):
    count = 0
    for item in items:
        count += 1
    return count
```

✅ **Allowed** (TODO):
```python
def process_data(items):
    # TODO: Optimize this algorithm
    count = 0
    return count
```

✅ **Allowed** (URL):
```python
def validate_format(text):
    # See: https://tools.ietf.org/html/rfc2822
    return regex.match(text)
```

✅ **Allowed** (Multi-line explanatory block):
```python
def complex_algorithm(data):
    # This implements the Foo-Bar algorithm as described in:
    # Smith et al. (2020). The algorithm operates in three phases:
    # 1. Preprocessing - normalize inputs
    # 2. Core processing - apply transformations
    # 3. Postprocessing - validate outputs
    result = preprocess(data)
    return postprocess(apply_transform(result))
```

**Implementation Notes**:
- Need to distinguish between:
  - Single-line comments (flag)
  - TODO/FIXME/NOTE/HACK markers (allow)
  - URL references (allow, detect `http://` or `https://`)
  - Multi-line comment blocks (allow, detect 2+ consecutive comment lines)
- Consider allowing comments that are configuration markers (e.g., `# noqa`, `# type: ignore`)
- May need special handling for commented-out code vs. explanatory comments

---

## Suppression Mechanism

### Comment-Based Suppression

**Format Options**:

```python
# Option 1: Inline suppression (like ruff/pylint)
x = 1  # vibelint: ignore VBL101

# Option 2: Next-line suppression
# vibelint: ignore VBL101
x = 1

# Option 3: Block suppression
# vibelint: ignore-start VBL101
x = 1
y = 2
# vibelint: ignore-end

# Option 4: File-level suppression (at top of file)
# vibelint: ignore-file VBL201

# Option 5: Multiple rules
# vibelint: ignore VBL101, VBL102
```

**Recommended Approach**:
- Start with Options 1 & 2 (inline and next-line)
- Use format: `# vibelint: ignore [RULE_CODE, ...]`
- Support both `ignore` and `noqa` keywords for compatibility
- Require explicit rule codes (no blanket suppression without codes)

**Implementation Considerations**:
- Parse comments during CST traversal
- Store suppression directives with line numbers
- Check suppressions when reporting violations
- Warn about unused suppressions (suppression with no matching violation)
- Consider configuration option to require suppression comments to include reason:
  ```python
  # vibelint: ignore VBL101 - intentional blank line for readability
  ```

### PEP 593 Annotation-Based Suppression

**Experimental Idea**: Use `Annotated` with metadata for suppressions

```python
from typing import Annotated

# Suppress at variable/parameter level
def foo(
    data: Annotated[dict, "vibelint:ignore:VBL201"],  # Suppress for this param
    config: dict,
) -> None:
    ...

# Or use dedicated marker type
from vibelinter import SuppressVBL

def bar(
    data: Annotated[dict, SuppressVBL(201, reason="legacy code")],
) -> None:
    ...
```

**Pros**:
- Type-safe suppressions
- More structured than comments
- Can be programmatically inspected

**Cons**:
- More verbose than comments
- Requires runtime dependency on vibelinter
- Only works for annotated locations (variables, parameters, returns)
- Not useful for suppressing structural violations (blank lines, imports)

**Recommendation**:
- Start with comment-based suppression (simpler, more flexible)
- Consider PEP 593 approach as a future enhancement
- PEP 593 might be better suited for rule configuration than suppression

---

## Other Rule Ideas (Future)

### VBL103 - Consecutive Blank Lines
- Detect 2+ consecutive blank lines anywhere in file
- Complements VBL101 (no blank lines in functions)

### VBL104 - Trailing Blank Lines
- Detect blank lines at end of file beyond the required single blank line
- Related to vertical compactness principle

### VBL202 - Star Import Usage
- Flag `from module import *` except in designated re-export modules
- Prevents namespace pollution

### VBL203 - Import Ordering
- Verify imports follow PEP 8 grouping (stdlib, third-party, first-party)
- Verify lexicographic ordering within groups
- (May overlap with isort, but could enforce project-specific patterns)

### VBL301 - Naming Conventions
- Private names start with `_`
- Constants are UPPER_CASE
- Classes are PascalCase
- Functions/variables are snake_case
- Module-level "type aliases" (TypeAlias annotations) are PascalCase

### VBL302 - Function Length
- Functions should be ≤ 30 lines (configurable)
- Enforces single responsibility principle

### VBL303 - Module Length
- Modules should be ≤ 600 lines (configurable)
- Encourages proper code organization

---

## Implementation Priority

1. **VBL201** - Import hub enforcement (architectural, catches real issues)
2. **VBL102** - Unnecessary comments (style, complements VBL101)
3. **Suppression mechanism** - Enable targeted rule disabling
4. **VBL103/104** - Additional blank line rules (easy wins)
5. **VBL301-303** - Naming and length conventions (lower priority, overlaps with other tools)

---

## Notes from Session

- Configuration support is now complete (pyproject.toml)
- All infrastructure is in place for adding new rules
- Rule framework supports per-rule configuration via `rule_parameters`
- Consider whether each rule should be auto-fixable (future enhancement)
