# Change: Add Describe Subcommands

## Why
Users need to discover available linting rules and understand what each rule does before applying them. Without documentation and discovery features, users cannot effectively use the linter or understand violation messages.

## What Changes
- **CLI**: Add `describe rules` subcommand to list all available rules
- **CLI**: Add `describe rule <identifier>` subcommand to show detailed rule information
- **Rule Framework**: Enhance `RuleDescriptor` with `violation_message` and `examples` fields
- **Rule Implementations**: Update existing rules with violation messages and examples

## Impact
- **Affected specs**: `cli`, `rule-framework`
- **Affected code**: `cli.py`, `rules/registry.py`, rule implementation files
- **New capabilities**: Rule discovery, documentation, and user education