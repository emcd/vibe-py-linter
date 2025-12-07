## 1. Fix Infrastructure

- [ ] 1.1 Create `sources/vibelinter/rules/fixable.py` with `FixSafety`, `Fix`, and `FixableRule`
- [ ] 1.2 Create `sources/vibelinter/fixer.py` with `FixEngine` and `FixResult`
- [ ] 1.3 Add `collect_fixes()` method to `Engine` class in `engine.py`
- [ ] 1.4 Update `sources/vibelinter/rules/__init__.py` to export fixable module

## 2. CLI Integration

- [ ] 2.1 Implement `FixCommand.__call__()` in `cli.py`
- [ ] 2.2 Add diff generation for `--simulate` mode
- [ ] 2.3 Wire up safety filtering with `--apply-dangerous` flag

## 3. Style Rules

- [ ] 3.1 Implement VBL103 (bracket spacing) with fix support
- [ ] 3.2 Implement VBL104 (keyword argument spacing) with fix support
- [ ] 3.3 Implement VBL105 (quote normalization) with fix support
- [ ] 3.4 Implement VBL106 (single-line body compaction) with fix support
- [ ] 3.5 Implement VBL107 (trailing comma enforcement) with fix support
- [ ] 3.6 Implement VBL108 (docstring formatting) with fix support
- [ ] 3.7 Create `LineReformatter` class with left-gravity algorithm
- [ ] 3.8 Implement VBL109 (line length and reformatting) with fix support
- [ ] 3.9 Register all new rules in `implementations/__init__.py`

## 4. Testing

- [ ] 4.1 Add unit tests for fix infrastructure (`test_4XX_fixable.py`)
- [ ] 4.2 Add unit tests for fix engine (`test_4XX_fixer.py`)
- [ ] 4.3 Add unit tests for each style rule (VBL103-109)
- [ ] 4.4 Add integration tests for fix command

## 5. Documentation

- [ ] 5.1 Update rule descriptions in `describe` command output
- [ ] 5.2 Add user documentation for style rules
