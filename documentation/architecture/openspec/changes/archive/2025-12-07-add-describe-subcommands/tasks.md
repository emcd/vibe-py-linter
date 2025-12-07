# Tasks: Add Describe Subcommands

## Implementation Tasks

### Phase 1: Core Infrastructure
- [x] **Enhance RuleDescriptor class** (`sources/vibelinter/rules/registry.py`)
  - Add `violation_message` field to store violation message format
  - Add `examples` field to store violation/fix examples
  - Update type hints and documentation

### Phase 2: Rule Implementation Updates
- [x] **Update VBL101: Blank Line Elimination** (`sources/vibelinter/rules/implementations/vbl101.py`)
  - Add violation message: "Remove blank line after {context}"
  - Add examples showing blank line violations and fixes
  - Ensure examples demonstrate common scenarios

- [x] **Update VBL201: Import Hub Enforcement** (`sources/vibelinter/rules/implementations/vbl201.py`)
  - Add violation message: "Import {module} should be in import hub"
  - Add examples showing scattered imports vs. hub organization
  - Include both simple and complex import scenarios

- [x] **Update VBL202: Import Spaghetti Detection** (`sources/vibelinter/rules/implementations/vbl202.py`)
  - Add violation message: "Import spaghetti detected: {module} imports {count} modules"
  - Add examples showing import spaghetti patterns
  - Include examples of refactored, cleaner imports

### Phase 3: CLI Implementation
- [x] **Implement DescribeRulesCommand** (`sources/vibelinter/cli.py`)
  - Create `DescribeRulesResult` class with JSON/text rendering
  - Implement command logic to list all available rules
  - Support `--details` flag for additional information
  - Sort rules by descriptive name for consistent output

- [x] **Implement DescribeRuleCommand** (`sources/vibelinter/cli.py`)
  - Create `DescribeRuleResult` class with JSON/text rendering
  - Implement command logic to show detailed rule information
  - Support both VBL codes and descriptive names as identifiers
  - Include violation message and examples in output
  - Support `--details` flag for configuration status

- [x] **Implement DescribeCommand** (`sources/vibelinter/cli.py`)
  - Create container command for `rules` and `rule` subcommands
  - Use Tyro subcommand configuration for proper CLI structure
  - Ensure proper delegation to selected subcommand

- [x] **Integrate with CLI orchestrator** (`sources/vibelinter/cli.py`)
  - Add `DescribeCommand` to main `Cli` class union
  - Configure as subcommand with `describe` name
  - Ensure proper error handling via `intercept_errors`

### Phase 4: Rule Registry Integration
- [x] **Update rule registry manager** (`sources/vibelinter/rules/registry.py`)
  - Ensure `resolve_rule_identifier` supports both VBL codes and names
  - Add proper error handling for invalid rule identifiers
  - Update `survey_available_rules` to return all descriptors

- [x] **Register VBL202 implementation** (`sources/vibelinter/rules/implementations/__init__.py`)
  - Add VBL202 to `RULE_DESCRIPTORS` dictionary
  - Ensure proper import of VBL202 module

### Phase 5: VBL202 Self-Application Issue
- [x] **Document the issue** (`.auxiliary/notes/issues/vbl202-suppression.md`)
  - Document that VBL202 detects violations in its own implementation
  - Note that this is expected behavior for import spaghetti detection
  - Plan temporary and long-term solutions

- [x] **Add temporary suppression** (`pyproject.toml`)
  - Add per-file ignore for VBL202 in rule implementation files
  - Use `[tool.vibelinter.per-file-ignores]` section
  - Specify patterns matching rule implementation files

### Phase 6: Testing and Validation
- [x] **Run existing tests** to ensure no regressions
- [x] **Run linters** (ruff, mypy) to ensure code quality
- [x] **Test CLI commands manually**:
  - `vibelinter describe rules`
  - `vibelinter describe rules --details`
  - `vibelinter describe rule VBL101`
  - `vibelinter describe rule blank-line-elimination --details`
  - `vibelinter --format json describe rules`

### Phase 7: Documentation
- [x] **Create Openspec proposal** (`proposal.md`)
  - Document the "why", "what changes", and "impact"
  - Reference affected specs and code
- [x] **Update CLI spec** (`specs/cli/design.md`)
  - Ensure spec matches actual implementation
  - Update any discrepancies between design and implementation
- [x] **Create tasks documentation** (`tasks.md`) - this file

## Testing Tasks

### Unit Tests
- [ ] **Add tests for DescribeRulesCommand**
  - Test listing all rules
  - Test `--details` flag behavior
  - Test JSON output format
  - Test text output format

- [ ] **Add tests for DescribeRuleCommand**
  - Test with VBL code identifiers
  - Test with descriptive name identifiers
  - Test `--details` flag behavior
  - Test error handling for invalid identifiers
  - Test JSON and text output formats

- [ ] **Add tests for RuleDescriptor enhancements**
  - Test `violation_message` field
  - Test `examples` field
  - Test serialization to JSON

### Integration Tests
- [ ] **Test CLI integration**
  - Test `describe` command in full CLI context
  - Test error handling via `intercept_errors`
  - Test with different output formats

- [ ] **Test rule registry integration**
  - Test `resolve_rule_identifier` with various inputs
  - Test `survey_available_rules` returns enhanced descriptors

## Future Considerations

### Architectural Questions
- [ ] **Subcommand organization**: Should `describe` commands be moved to separate `subcommands/` directory per original design?
- [ ] **Configuration integration**: How should `--details` show configuration status? Need configuration system integration.
- [ ] **Rule examples format**: Should examples use a structured format (e.g., YAML blocks) for better parsing?

### VBL202 Self-Application
- [ ] **Long-term solution**: Implement proper rule suppression mechanism
- [ ] **Alternative approach**: Modify VBL202 to exclude rule implementation files
- [ ] **Documentation**: Add guidance for rule authors on self-application issues

### Enhancement Opportunities
- [ ] **Rule categories**: Implement hierarchical categorization for better organization
- [ ] **Search functionality**: Add `--search` flag to `describe rules` for filtering
- [ ] **Interactive mode**: Add interactive rule browser with pagination
- [ ] **Rule dependencies**: Show which rules depend on or conflict with others