# Proof-of-Concept: Blank Line Rule (VBL101)

This directory contains the proof-of-concept implementation for REQ-002 from the PRD: "Prohibit blank lines within function bodies, so that function implementations remain compact and focused."

## Proof-of-Concept Implementation

### `blank_line_rule_poc.py`

Command-line tool that implements the VBL101 rule using LibCST with validated integration patterns.

**Usage:**
```bash
# Check a single Python file
python blank_line_rule_poc.py <python_file> [--verbose] [--context]

# Examples
python blank_line_rule_poc.py test_blank_lines.py --verbose
python blank_line_rule_poc.py test_good_functions.py
python blank_line_rule_poc.py test_blank_lines.py --context  # Show context lines
python blank_line_rule_poc.py test_blank_lines.py -c -v     # Context + verbose
```

**Features:**
- Detects blank lines within function and method bodies
- Supports regular and async functions
- Handles nested functions and class methods
- Provides precise line/column error reporting using PositionProvider
- **Context display**: Shows 2 lines before and after each violation (--context flag)
- Graceful error handling for syntax errors
- Exit codes suitable for CI/CD integration (0 = clean, 1 = violations found)

**Rule Implementation:**
- Uses LibCST visitor pattern with PositionProvider metadata
- Tracks function scope to only check within function bodies
- Detects EmptyLine nodes in IndentedBlock structures
- Reports violations with rule ID "VBL101"

## Test Files

### `test_blank_lines.py`
Demonstrates various violation scenarios:
- Functions with blank lines (should fail)
- Async functions with blank lines (should fail)
- Class methods with blank lines (should fail)
- Nested functions with blank lines (should fail)
- Functions with comments and blank lines (should fail)

**Expected result:** 16 violations found

**Context output example:**
```
.auxiliary/poc/test_blank_lines.py:18:1: error: Blank line found within function bad_function body. Function implementations should remain compact and focused. (VBL101)

   16 |     """This function has blank lines - should fail."""
   17 |     x = 1
>  18 |
   19 |     y = 2
   20 |
```

### `test_good_functions.py`
Clean functions without violations:
- Simple functions without blank lines
- Async functions without blank lines
- Class methods without blank lines
- Nested functions without blank lines
- Multi-line statements without blank lines

**Expected result:** 0 violations (clean)

## Integration with Validated Architecture

This proof-of-concept demonstrates the validated LibCST integration patterns:

1. **Visitor Pattern**: Inherits from `cst.CSTVisitor` with metadata dependencies
2. **Position Reporting**: Uses `PositionProvider` for precise error locations
3. **Error Handling**: Graceful handling of `ParserSyntaxError` and other exceptions
4. **Metadata Access**: Safe metadata access with try/catch for KeyError
5. **Performance**: Efficient single-pass analysis using collection-then-analysis pattern

## Validation Results Reference

This implementation is based on comprehensive LibCST validation:
- **128 tests across 6 categories** with 100% functional success
- **Performance validated**: 600ms for 1000 lines (20% over target but acceptable)
- **Memory efficient**: 6-20MB peak usage, no leaks detected
- **Error resilient**: 36/36 error handling tests passed
- **All metadata providers working correctly**

See `.auxiliary/notes/libcst-validation-report.md` for complete validation results.

## Next Steps

This proof-of-concept serves as the foundation for implementing:
1. **BaseRule Framework** using the same LibCST patterns
2. **Core Engine Integration** following ADR 001 architecture
3. **Additional Rules**: REQ-001 (function ordering), REQ-003 (naming), REQ-004 (type variance)
4. **Configuration System** using validated TOML approach from ADR 003

The implementation validates that LibCST can successfully implement the blank line elimination rule with precise error reporting and good performance characteristics.

## Configuration Files

### `.ruff.toml`

This file configures **Ruff** (not vibelinter) for linting the POC scripts themselves. It disables certain Ruff rules that would conflict with the demonstration code or are relaxed for proof-of-concept work.
