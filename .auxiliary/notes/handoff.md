# Session Handoff Notes

## Next Priority: Test Plans

### Gap Analysis

Test plans exist for:
- `configuration-reader.rst` - Configuration loading
- `engine.rst` - Linter engine
- `vbl101-blank-line-elimination.rst` - VBL101 rule
- `vbl201-import-hub-enforcement.rst` - VBL201 rule

Missing test plans (9 total):

### Priority 1: Fix Infrastructure (foundational)
1. **`fixer.rst`** - FixEngine, FixResult, FixApplicationResult, SkippedFix, FixConflict
   - Core fix application logic, safety filtering, conflict resolution
   - Located in `sources/vibelinter/fixer.py`

2. **`fixable.rst`** - FixableRule base class, Fix dataclass, FixSafety enum
   - Base framework for all fixable rules
   - Located in `sources/vibelinter/rules/fixable.py`

### Priority 2: Style Rules with Fix Support (high value)
3. **`vbl103-bracket-spacing.rst`** - Tests bracket spacing detection and fixes
4. **`vbl104-keyword-argument-spacing.rst`** - Tests keyword arg spacing detection and fixes
5. **`vbl105-quote-normalization.rst`** - Tests quote style detection and fixes

### Priority 3: Remaining Style Rules
6. **`vbl106-single-line-body.rst`** - Single-line body compaction
7. **`vbl107-trailing-comma.rst`** - Trailing comma enforcement
8. **`vbl108-docstring-formatting.rst`** - Docstring formatting
9. **`vbl109-line-length.rst`** - Line length detection (no fix support yet)

### Test Plan Format Reference
See `documentation/architecture/testplans/vbl101-blank-line-elimination.rst` for format:
- Coverage Analysis Summary (current %, target, uncovered areas)
- Test Strategy (in-memory code snippets, helper functions)
- Test cases organized by number ranges (000-099 basic, 100-199 simple, etc.)
- Implementation Notes (dependencies, fixtures, anti-patterns)
- Success Metrics (coverage goals, test count estimate)

### Test File Naming Convention
- `test_140_fixable.py` - Fixable rule framework (core infrastructure)
- `test_360_fixer.py` - Fix engine infrastructure (alongside engine)
- `test_440_rules_vbl103.py` - VBL103 rule
- `test_441_rules_vbl104.py` - VBL104 rule
- `test_442_rules_vbl105.py` - VBL105 rule
- `test_443_rules_vbl106.py` - VBL106 rule
- `test_444_rules_vbl107.py` - VBL107 rule
- `test_445_rules_vbl108.py` - VBL108 rule
- `test_446_rules_vbl109.py` - VBL109 rule

---

## Completed Work

### Style Rules Implementation (VBL103-VBL109)

Style rules have been drafted; see "Implementation Gaps" for remaining work:

| Rule | Name | Description | Fix Support |
|------|------|-------------|-------------|
| VBL103 | bracket-spacing | Spaces inside `()`, `[]`, `{}` | Yes |
| VBL104 | keyword-argument-spacing | Spaces around `=` in kwargs | Yes |
| VBL105 | quote-normalization | Single for data, double for f-strings/messages | Yes |
| VBL106 | single-line-body | Compact single-statement control flow | Yes (includes try bodies) |
| VBL107 | trailing-comma | Trailing commas in multi-line collections | Yes |
| VBL108 | docstring-formatting | Triple single-quotes, proper spacing | Yes (single- and multi-line) |
| VBL109 | line-length | Detect lines exceeding 79 chars | Detection only |

### Files Created/Modified

**New Files:**
- `sources/vibelinter/rules/implementations/vbl103.py` - Bracket spacing
- `sources/vibelinter/rules/implementations/vbl104.py` - Keyword arg spacing
- `sources/vibelinter/rules/implementations/vbl105.py` - Quote normalization
- `sources/vibelinter/rules/implementations/vbl106.py` - Single-line body
- `sources/vibelinter/rules/implementations/vbl107.py` - Trailing comma
- `sources/vibelinter/rules/implementations/vbl108.py` - Docstring formatting
- `sources/vibelinter/rules/implementations/vbl109.py` - Line length

**Modified Files:**
- `sources/vibelinter/rules/implementations/__init__.py` - Added imports
- `.auxiliary/configuration/vulturefood.py` - Whitelisted visitor methods

### Verification

- All 277 existing tests pass
- Pyright type checks pass for all new files
- `vibelinter describe rules` shows all 10 registered rules
- Rule imports work correctly

## Deferred Work

### Codebase Style Conformance

The vibelinter check is still not part of the standard linters run. We have
applied the fixers for VBL103, VBL105, VBL106, and VBL107 across `sources/`
and resolved all reported violations for those rules; VBL108 currently reports
none. VBL109 remains detection-only. Before re-enabling vibelinter in
`pyproject.toml`, consider a final repo-wide pass (including tests/docs) to
catch any stragglers outside `sources/`.

### LineReformatter with Left-Gravity Algorithm

VBL109 currently provides detection only. The full LineReformatter algorithm
(documented in `documentation/architecture/openspec/specs/remediation/design.md`)
is deferred:

- Progressive breaking levels (1-4)
- Content → next line, closing → own line, one-per-line, recurse into nested
- Trailing comma logic (collections yes, function calls no)
- Single-line body compaction threshold (70% of max line length)

### Implementation Gaps Discovered

- `FixEngine.apply_fixes` now tracks basic overlap conflicts (same line/column) but still needs richer span-aware detection and reporting for adjacent/structural overlaps.
- Action: extend FixEngine conflict detection to be span-aware (overlapping and adjacent spans), with clear reporting, before enabling dangerous fixes by default.

### Unit Tests for Style Rules

Tests should be added for VBL103-VBL109 following the patterns in:
- `tests/test_000_vibelinter/test_410_rules_vbl101.py`
- `tests/test_000_vibelinter/test_420_rules_vbl201.py`

## OpenSpec References

- Main change: `documentation/architecture/openspec/changes/add-style-rules-and-fix-implementation/`
- Rules spec: `specs/rules-readability/spec.md`
- Remediation design: `specs/remediation/design.md` (LineReformatter details)
- CLI spec: `specs/cli/spec.md`

## Technical Notes

### Rule Pattern

Each rule follows this pattern:
1. Inherit from `FixableRule` (or `BaseRule` for detection-only)
2. Define `METADATA_DEPENDENCIES` tuple
3. Implement `visit_*` methods to collect violations
4. Implement `_analyze_collections()` to generate violations
5. For fixable rules, call `_produce_fix()` with transformer factory
6. Self-register via `__.RULE_DESCRIPTORS['VBLxxx'] = RuleDescriptor(...)`

### Transformer Pattern

Transformers target specific positions using `(line, column)` tuples:
```python
class _SomeTransformer(__.libcst.CSTTransformer):
    def __init__(self, target_line: int, target_column: int) -> None:
        self.target_line = target_line
        self.target_column = target_column

    def leave_SomeNode(self, original, updated):
        pos = self._get_position(original)
        if pos != (self.target_line, self.target_column):
            return updated
        # Apply transformation
        return updated.with_changes(...)
```

### Vulture Whitelist

All visitor/leave methods must be whitelisted in
`.auxiliary/configuration/vulturefood.py` since they're called by LibCST
framework rather than directly by our code.
