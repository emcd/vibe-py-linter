## 1. Implementation
- [x] 1.1 Update `tests/test_000_vibelinter/test_410_rules_vbl101.py` to expect no violations for blank lines around nested definitions.
- [x] 1.2 Add new test cases to `tests/test_000_vibelinter/test_410_rules_vbl101.py` specifically targeting blank lines before and after `def` and `class` blocks within functions.
- [x] 1.3 Refactor `sources/vibelinter/rules/implementations/vbl101.py` to collect `ClassDef` nodes in addition to `FunctionDef`.
- [x] 1.4 Update `VBL101.visit_FunctionDef` (and new `visit_ClassDef`) to record the start and end lines of all definitions (nested or not) into a queryable structure.
- [x] 1.5 Modify `VBL101._analyze_collections` to check if a blank line is adjacent (line before start or line after end) to any collected nested definition before reporting a violation.
- [x] 1.6 Verify all tests pass.