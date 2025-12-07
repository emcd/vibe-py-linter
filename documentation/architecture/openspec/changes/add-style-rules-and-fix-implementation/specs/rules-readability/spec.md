## ADDED Requirements

### Requirement: Bracket Spacing (VBL103)

The system SHALL enforce spaces after opening delimiters and before closing delimiters for parentheses, brackets, and braces.

Priority: High

#### Scenario: Missing space after opening delimiter

- **WHEN** code contains `func(arg)` without space after `(`
- **THEN** a violation is reported suggesting `func( arg )`

#### Scenario: Missing space before closing delimiter

- **WHEN** code contains `[1, 2, 3]` without space before `]`
- **THEN** a violation is reported suggesting `[ 1, 2, 3 ]`

#### Scenario: Empty delimiters

- **WHEN** code contains empty delimiters like `()` or `[]`
- **THEN** a violation is reported suggesting `( )` or `[ ]`

#### Scenario: F-string exception

- **WHEN** spacing violation occurs inside an f-string expression
- **THEN** no violation is reported (f-strings are exempt)

### Requirement: Keyword Argument Spacing (VBL104)

The system SHALL enforce spaces around `=` in keyword arguments and default parameter values.

Priority: High

#### Scenario: Missing spaces in function call

- **WHEN** code contains `func(arg=value)`
- **THEN** a violation is reported suggesting `func( arg = value )`

#### Scenario: Missing spaces in function definition

- **WHEN** code contains `def func(param=default)`
- **THEN** a violation is reported suggesting `def func( param = default )`

### Requirement: Quote Normalization (VBL105)

The system SHALL enforce single quotes for data strings and double quotes for f-strings, format strings, and messages.

Priority: High

#### Scenario: Data string with double quotes

- **WHEN** a plain data string uses double quotes like `"value"`
- **THEN** a violation is reported suggesting `'value'`

#### Scenario: F-string with single quotes

- **WHEN** an f-string uses single quotes like `f'Hello {name}'`
- **THEN** a violation is reported suggesting `f"Hello {name}"`

#### Scenario: Exception message with single quotes

- **WHEN** an exception message uses single quotes like `raise ValueError('Invalid')`
- **THEN** a violation is reported suggesting double quotes

#### Scenario: String containing quotes

- **WHEN** a string contains the opposite quote character
- **THEN** no violation is reported (preserve to avoid escaping)

### Requirement: Single-Line Body Compaction (VBL106)

The system SHALL enforce single-line form for simple control flow bodies.

Priority: Medium

#### Scenario: Simple if statement

- **WHEN** an if statement has a single short statement on a separate line
- **THEN** a violation is reported suggesting single-line form like `if x: return y`

#### Scenario: Simple for loop

- **WHEN** a for loop has a single short statement on a separate line
- **THEN** a violation is reported suggesting `for item in items: process( item )`

#### Scenario: Simple try/except

- **WHEN** a try block has a single statement
- **THEN** a violation is reported suggesting `try: value = op( )` form

#### Scenario: Complex body

- **WHEN** a control flow body has multiple statements or long content
- **THEN** no violation is reported (multi-line form is appropriate)

### Requirement: Trailing Comma Enforcement (VBL107)

The system SHALL enforce trailing commas in multi-line collection literals.

Priority: Medium

#### Scenario: Multi-line list without trailing comma

- **WHEN** a multi-line list literal lacks a trailing comma after the last element
- **THEN** a violation is reported

#### Scenario: Multi-line dict without trailing comma

- **WHEN** a multi-line dictionary literal lacks a trailing comma
- **THEN** a violation is reported

#### Scenario: Single-line collection

- **WHEN** a collection fits on a single line
- **THEN** no trailing comma violation is reported

#### Scenario: Function call arguments

- **WHEN** a multi-line function call lacks trailing comma
- **THEN** no violation is reported (function calls exempt per style guide)

### Requirement: Docstring Formatting (VBL108)

The system SHALL enforce triple single-quote docstrings with proper spacing.

Priority: Medium

#### Scenario: Double-quote docstring

- **WHEN** a docstring uses triple double-quotes `"""`
- **THEN** a violation is reported suggesting triple single-quotes `'''`

#### Scenario: Missing space after opening quotes

- **WHEN** a single-line docstring has no space after opening quotes
- **THEN** a violation is reported suggesting `''' Text '''`

#### Scenario: Missing space before closing quotes

- **WHEN** a single-line docstring has no space before closing quotes
- **THEN** a violation is reported

#### Scenario: Multi-line docstring format

- **WHEN** a multi-line docstring doesn't follow indentation conventions
- **THEN** a violation is reported with guidance on proper formatting
