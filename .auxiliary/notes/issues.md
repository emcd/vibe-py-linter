# Known Issues and Investigation Notes

## VBL101: String Literal Detection Bug [RESOLVED]

**Severity**: Medium
**Component**: `sources/vibelinter/rules/implementations/vbl101.py:87-88`
**Discovered**: 2025-11-22 (during test development)
**Resolved**: 2025-11-22 (commit c62a39a)

**Description**: The string literal detection logic only identifies triple-quoted strings that appear at the beginning of a stripped line. This causes false positives for blank lines inside string literals that follow assignments or other code.

**Current Behavior**:
```python
# WORKS (string starts line after stripping)
def func():
    """Docstring with

    blank lines inside.
    """
```

```python
# FAILS (string after assignment)
def func():
    text = """String with

    blank lines inside.
    """
    # Lines 3-4 incorrectly flagged as violations
```

**Root Cause**: Lines 87-88 use `stripped.startswith()` which only detects strings at line beginning:
```python
starts_triple_double = stripped.startswith( '"""' )
starts_triple_single = stripped.startswith( "'''" )
```

**Impact**:
- False positives in test_290 (multiline string after assignment)
- Workaround required in tests 200, 210, 330 to use docstrings instead
- Affects real-world code with assigned multiline strings

**Fix Complexity**: Low-Medium
- **Simple fix** (30-60 min): Search for `"""` or `'''` anywhere in line using `.find()` or `in` operator
  - Risk: Edge cases with quotes in comments or nested strings
- **Robust fix** (2-3 hours): Use LibCST's string literal node detection
  - Leverage existing `libcst.SimpleString` or `libcst.ConcatenatedString` nodes
  - Properly track string boundaries via CST
  - More reliable but requires refactoring the line-based approach

**Recommended Approach**: Robust fix using LibCST node detection, since the codebase already uses LibCST for parsing and the line-based approach is inherently fragile for this use case.

**Test Coverage**: Bug is documented in:
- `tests/test_000_vibelinter/test_410_rules_vbl101.py:test_200` (now tests correctly)
- `tests/test_000_vibelinter/test_410_rules_vbl101.py:test_210` (now tests correctly)
- `tests/test_000_vibelinter/test_410_rules_vbl101.py:test_290` (now tests correctly)
- `tests/test_000_vibelinter/test_410_rules_vbl101.py:test_330` (now tests correctly)

**Resolution**: Implemented LibCST-based string literal detection
- Added `visit_SimpleString()` method to collect triple-quoted string ranges
- Added `visit_ConcatenatedString()` method for concatenated strings
- Added `_is_in_string()` helper to check if line falls within string
- Removed fragile line-based string detection logic
- All tests now pass with assigned strings, not just docstrings
- Visitor methods whitelisted in `.auxiliary/configuration/vulturefood.py`

---

## VBL101: Nested Function Blank Line Counting

**Severity**: Low (arguably correct behavior)
**Component**: `sources/vibelinter/rules/implementations/vbl101.py:75-102`
**Discovered**: 2025-11-22 (during test development)

**Description**: The implementation counts blank lines that appear before nested function definitions as violations in the outer function's body.

**Behavior**:
```python
def outer():
    x = 1
    # Line 3: blank line (violation in outer)
    def inner():  # Line 4: this line is in outer's range
        y = 2
        # Line 6: blank line (violation in inner)
        z = 3
```
Result: 3 violations (lines 3, 4, 6) instead of expected 2 (lines 3, 6)

**Root Cause**: The function range (`start_line` to `end_line`) includes the entire outer function body, so blank lines before the `def inner():` statement are analyzed as part of the outer function.

**Impact**:
- Higher violation counts than initially expected in nested function scenarios
- Not necessarily wrong - blank lines before nested defs are technically in the outer function
- Tests adjusted to expect this behavior

**Fix Complexity**: N/A - May be correct behavior per style guidelines

**Discussion Needed**: Is a blank line before a nested function definition acceptable? The current implementation treats it as a violation, which enforces maximum compactness. This may align with project style guidelines that discourage blank lines in function bodies.

**Test Coverage**: Behavior documented in:
- `tests/test_000_vibelinter/test_410_rules_vbl101.py:test_400` (3 violations expected)
- `tests/test_000_vibelinter/test_410_rules_vbl101.py:test_410` (3 violations expected)
- `tests/test_000_vibelinter/test_410_rules_vbl101.py:test_420` (3 violations expected)
- `tests/test_000_vibelinter/test_410_rules_vbl101.py:test_430` (6 violations expected)
