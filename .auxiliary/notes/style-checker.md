# Plan: Style Checker and Code Reformatter Integration

## Summary

Add style checking and code reformatting capabilities to vibe-py-linter, integrating with the existing rule framework and CLI infrastructure.

## User Requirements

- **Unified approach**: Style violations appear alongside other lint violations in `check` command
- **Selective fix**: Apply fixes via `fix --select VBL1XX` (reuse existing CLI pattern)
- **Comprehensive style**: Whitespace, structural changes (import ordering, quotes, trailing commas), plus custom patterns

## Architecture Assessment

The existing infrastructure supports this naturally:

| Component | Current State | Extension Needed |
|-----------|--------------|------------------|
| Rule framework | `BaseRule` with `CSTVisitor` | Add `FixableRule` variant with fix support |
| Fix command | CLI stub exists (cli.py:332-364) | Implement actual fix logic |
| Violations | `Violation` dataclass | Optionally extend with `Fix` association |
| Engine | Single-pass CST traversal | Add `collect_fixes()` method |

## Implementation Plan

### Phase 1: Fix Infrastructure

**1.1 Create fix data structures**

New file: `sources/vibelinter/rules/fixable.py`

```
- FixSafety enum: Safe, PotentiallyUnsafe, Dangerous
- Fix dataclass: violation, description, safety, transformer_factory
- FixableRule(BaseRule): extends base with supports_fix property and collect_fixes() method
```

Key design: Detection uses `CSTVisitor` (existing), fixing uses `CSTTransformer` (new). Separate classes avoid metaclass conflicts.

**1.2 Create fix engine**

New file: `sources/vibelinter/fixer.py`

```
- FixEngine class: coordinates fix application
- apply_fixes(): filters by safety, orders by position, applies sequentially
- Conflict resolution: reverse position order, skip overlapping fixes
```

**1.3 Extend linter engine**

Modify: `sources/vibelinter/engine.py`

- Add `collect_fixes()` method to gather fixes from fixable rules
- Reuses existing CST traversal infrastructure

### Phase 2: CLI Integration

**2.1 Implement FixCommand**

Modify: `sources/vibelinter/cli.py` (lines 332-364)

- Wire up file discovery (already exists for `check`)
- Call `engine.collect_fixes()` for each file
- Apply fixes via `FixEngine`
- Generate diffs for `--simulate` mode
- Write modified files when not simulating

### Phase 3: Style Rules (VBL1XX Series - Readability)

New files in `sources/vibelinter/rules/implementations/`:

| Rule | Purpose | Safety |
|------|---------|--------|
| VBL103 | Bracket spacing (spaces inside `()`, `[]`, `{}`) | Safe |
| VBL104 | Keyword argument spacing (spaces around `=`) | Safe |
| VBL105 | Quote normalization (single for data, double for messages) | Safe |
| VBL106 | Single-line body compaction (`if x: return y`) | Safe |
| VBL107 | Trailing comma enforcement (multi-line collections) | Safe |
| VBL108 | Docstring formatting (triple single-quotes, spacing) | Safe |

*Style rules belong in VBL1XX (Readability) per documented block semantics.*

Each rule follows pattern:
1. Inherit from `FixableRule`
2. Collect violations during CST visit
3. Generate `Fix` objects with transformer factories
4. Transformers modify CST while preserving formatting

### Phase 4: Testing and Documentation

- Unit tests for fix infrastructure
- Integration tests for fix application
- ADR documenting style checker architecture
- User documentation for style rules

## Key Files to Modify/Create

**Create:**
- `sources/vibelinter/rules/fixable.py` - Fix infrastructure
- `sources/vibelinter/fixer.py` - Fix engine
- `sources/vibelinter/rules/implementations/vbl1XX.py` - Style rules (VBL103-108)

**Modify:**
- `sources/vibelinter/engine.py` - Add `collect_fixes()`
- `sources/vibelinter/cli.py` - Implement `FixCommand`
- `sources/vibelinter/rules/implementations/__init__.py` - Import new rules

## Design Decisions

1. **Separation of detection and fixing**: Avoids metaclass conflicts; rules can support detection-only or detection+fix
2. **Transformer factories**: Fixes store factories (not instances) for lazy creation and independent application
3. **Safety classification**: Existing `--apply-dangerous` flag maps naturally to safety levels
4. **Reverse position ordering**: Apply fixes from end of file toward beginning to avoid offset drift

## VBL Semantic Categories

| Series | Category | Philosophy | Examples |
|--------|----------|------------|----------|
| **VBL1XX** | Readability | "Can I understand this code quickly?" | Compactness, nomenclature, formatting |
| **VBL2XX** | Discoverability | "Can I find what I need?" | Navigation, import structure |
| **VBL3XX** | Robustness | "Does this code handle edge cases?" | Defensive patterns, type variance |
| **VBL4XX** | Correctness | "Is this code likely buggy?" | Unreachable code, anti-patterns |
| **VBL5XX** | Maintainability | "Will this code age well?" | Complexity, coupling |
| **VBL6XX** | Consistency | "Does this match project conventions?" | Project-specific patterns |

*Style/formatting rules belong in VBL1XX (Readability). VBL6XX is for project-specific conventions that go beyond universal best practices.*

## Style Conventions (Resolved)

Style rules are fully documented in `.auxiliary/instructions/practices-python.rst`:

**Spacing:**
- One space after `(`, `[`, `{` and before `)`, `]`, `}` (except in f-strings)
- Empty delimiters: `( )`, `[ ]`, `{ }`
- Spaces around `=` in keyword args: `func( arg = value )`

**Strings:**
- Single quotes for data strings
- Double quotes for f-strings, `.format`, exception/log messages

**Vertical compactness:**
- Single-line bodies: `if not data: return None`
- No blank lines within function bodies (already VBL101)

**Docstrings:**
- Triple single-quotes: `''' Example. '''`
- Narrative mood (third person)

**Collections:**
- Short: one line
- Long: one per line with trailing comma after last element

**Function invocations:**
- No trailing comma; closing paren on same line as final arg
