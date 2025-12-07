## MODIFIED Requirements

### Requirement: Rule Suppression
The system SHALL support suppressing rule violations via configuration or inline comments.

#### Scenario: Suppressing via comment (Specific Rule)
- **WHEN** a line contains a comment ending with `# noqa: VBL101`
- **THEN** violations of rule `VBL101` on that line are ignored

#### Scenario: Suppressing via comment (All Rules)
- **WHEN** a line contains a comment ending with `# noqa`
- **THEN** all violations on that line are ignored

#### Scenario: Suppressing via configuration (Per-File)
- **WHEN** a file matches a per-file ignore pattern for a specific rule
- **THEN** violations of that rule in that file are ignored
