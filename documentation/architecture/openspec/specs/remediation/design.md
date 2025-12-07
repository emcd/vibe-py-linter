# Remediation (Auto-Fix) Design

This document specifies the remediation framework design implementing
automated fix capabilities for rule violations. The design extends the
core linter framework with fix data structures, fixable rule patterns,
and fix engine orchestration.

## Remediation Architecture

### Framework Components

The remediation system extends the linter core with four primary components:

**Fix Data Structures**

:   Immutable data classes representing automated fixes with safety
    classification and transformer factory patterns.

**FixableRule Framework**

:   Extension of BaseRule providing fix collection capabilities alongside
    violation detection, using separate CSTTransformer instances to avoid
    metaclass conflicts.

**Fix Engine Orchestration**

:   Coordinator managing fix application with safety filtering, conflict
    resolution, and reverse position ordering.

**Diff Generation Utilities**

:   Patterns for generating unified and context diffs for simulation mode
    preview.

## Data Structure Design

### Fix Safety Classification

Fix operations are classified by their potential impact on code semantics:

``` python
from . import __

class FixSafety( __.enum.Enum ):
    ''' Classification of fix safety for graduated application control. '''
    Safe = 'safe'
    # Whitespace-only changes with no semantic impact.
    # Examples: bracket spacing, blank line removal, quote normalization.
    PotentiallyUnsafe = 'potentially_unsafe'
    # Changes that may affect semantics in edge cases.
    # Examples: import reordering (initialization order), trailing commas.
    Dangerous = 'dangerous'
    # Changes that can alter program behavior.
    # Examples: type annotation modifications, code restructuring.
```

### Fix Representation

The fix data structure associates violations with transformation capabilities:

``` python
from . import __

class Fix( __.immut.DataclassObject ):
    ''' Represents an automated fix for a rule violation. '''
    violation: __.typx.Annotated[
        Violation, __.ddoc.Doc( 'The violation this fix addresses.' ) ]
    description: __.typx.Annotated[
        str, __.ddoc.Doc( 'Human-readable description of the fix action.' ) ]
    safety: __.typx.Annotated[
        FixSafety, __.ddoc.Doc( 'Safety classification for this fix.' ) ]
    transformer_factory: __.typx.Annotated[
        __.cabc.Callable[ [ ], __.libcst.CSTTransformer ],
        __.ddoc.Doc( 'Factory producing transformer to apply fix.' ) ]

# Type aliases for fix framework contracts
FixSequence: __.typx.TypeAlias = __.cabc.Sequence[ Fix ]
```

### Transformer Factory Pattern

Fixes store factories rather than transformer instances for several reasons:

- **Lazy creation**: Transformers are only instantiated when fix is applied
- **Independent application**: Each fix can be applied without shared state
- **Conflict avoidance**: Fresh transformers avoid accumulated modifications

``` python
# Example transformer factory for bracket spacing fix
def _create_bracket_spacing_transformer(
    target_node: __.libcst.CSTNode,
    spacing_type: str,
) -> __.cabc.Callable[ [ ], __.libcst.CSTTransformer ]:
    ''' Creates factory for bracket spacing transformer. '''
    def factory( ) -> BracketSpacingTransformer:
        return BracketSpacingTransformer( target_node, spacing_type )
    return factory
```

## FixableRule Framework Design

### Extension of BaseRule

The FixableRule extends BaseRule to provide fix collection alongside
violation detection:

``` python
from . import __

class FixableRule( BaseRule ):
    ''' Extended base class for rules that can provide automated fixes.

        Inherits violation detection from BaseRule and adds fix collection
        capabilities. Detection uses CSTVisitor (inherited), fixing uses
        separate CSTTransformer instances to avoid metaclass conflicts.
    '''

    @property
    def supports_fix( self ) -> __.typx.Annotated[
        bool, __.ddoc.Doc( 'Indicates whether this rule provides fixes.' )
    ]:
        ''' Returns True if rule can generate fixes for violations. '''
        return False

    def collect_fixes( self ) -> __.typx.Annotated[
        tuple[ Fix, ... ],
        __.ddoc.Doc( 'Fixes for detected violations.' ),
    ]:
        ''' Returns fixes for violations detected during analysis.

            Called after _analyze_collections completes. Rules should
            generate Fix objects for violations that can be automatically
            remediated. Not all violations need fixes.
        '''
        return ( )
```

### Separation of Detection and Fixing

LibCST's `CSTVisitor` and `CSTTransformer` have incompatible metaclasses,
preventing a single class from inheriting both. The design addresses this
through separation:

- **Detection phase**: Rule inherits from `CSTVisitor` via `BaseRule`
- **Fixing phase**: Rule creates `CSTTransformer` instances via factories

This separation provides additional benefits:

- Rules can detect violations without providing fixes
- Fixes can be applied selectively without re-running detection
- Transformer logic is isolated and independently testable

### Example Fixable Rule Implementation

``` python
class VBL103( FixableRule ):
    ''' Enforces bracket spacing conventions. '''

    @property
    def rule_id( self ) -> str: return 'VBL103'

    @property
    def supports_fix( self ) -> bool: return True

    def __init__(
        self,
        filename: str,
        wrapper: __.libcst.metadata.MetadataWrapper,
        source_lines: tuple[ str, ... ],
    ) -> None:
        super( ).__init__( filename, wrapper, source_lines )
        self._spacing_violations: list[ tuple[ __.libcst.CSTNode, str ] ] = [ ]

    def visit_Call( self, node: __.libcst.Call ) -> bool:
        ''' Checks function call bracket spacing. '''
        # Detection logic - collect violations during traversal
        if not self._has_correct_spacing( node ):
            self._spacing_violations.append( ( node, 'call' ) )
        return True

    def _analyze_collections( self ) -> None:
        ''' Generates violations for spacing issues. '''
        for node, context in self._spacing_violations:
            message = f"Missing spaces in {context} brackets."
            self._produce_violation( node, message, severity = 'warning' )

    def collect_fixes( self ) -> tuple[ Fix, ... ]:
        ''' Creates fixes for spacing violations. '''
        fixes = [ ]
        for node, context in self._spacing_violations:
            fix = Fix(
                violation = self._violation_for_node( node ),
                description = f"Add spaces to {context} brackets.",
                safety = FixSafety.Safe,
                transformer_factory = _create_spacing_transformer( node, context ),
            )
            fixes.append( fix )
        return tuple( fixes )
```

## Fix Engine Design

### Engine Orchestration Interface

The FixEngine coordinates fix application with safety controls:

``` python
from . import __

class FixResult( __.immut.DataclassObject ):
    ''' Results of fix application including before/after content. '''
    original: __.typx.Annotated[
        str, __.ddoc.Doc( 'Original source code before fixes.' ) ]
    modified: __.typx.Annotated[
        str, __.ddoc.Doc( 'Modified source code after fixes.' ) ]
    applied_fixes: __.typx.Annotated[
        tuple[ Fix, ... ], __.ddoc.Doc( 'Fixes that were applied.' ) ]
    skipped_fixes: __.typx.Annotated[
        tuple[ Fix, ... ], __.ddoc.Doc( 'Fixes skipped due to safety or conflicts.' ) ]

class FixEngine:
    ''' Coordinates fix application with safety controls and conflict resolution. '''

    def __init__(
        self,
        max_safety: __.typx.Annotated[
            FixSafety,
            __.ddoc.Doc( 'Maximum safety level to apply without explicit flag.' )
        ] = FixSafety.Safe,
    ) -> None: ...

    def apply_fixes(
        self,
        source_code: __.typx.Annotated[
            str, __.ddoc.Doc( 'Source code to modify.' ) ],
        fixes: __.typx.Annotated[
            __.cabc.Sequence[ Fix ], __.ddoc.Doc( 'Fixes to apply.' ) ],
        apply_dangerous: __.typx.Annotated[
            bool, __.ddoc.Doc( 'Enable fixes above max_safety level.' ) ] = False,
    ) -> __.typx.Annotated[
        FixResult,
        __.ddoc.Doc( 'Result containing modified code and fix metadata.' ),
    ]: ...

    def generate_diff(
        self,
        result: __.typx.Annotated[
            FixResult, __.ddoc.Doc( 'Fix result to diff.' ) ],
        format: __.typx.Annotated[
            str, __.ddoc.Doc( 'Diff format: unified or context.' ) ] = 'unified',
        context_lines: __.typx.Annotated[
            int, __.ddoc.Doc( 'Context lines in diff output.' ) ] = 3,
    ) -> __.typx.Annotated[
        str, __.ddoc.Doc( 'Formatted diff string.' ),
    ]: ...
```

### Fix Application Algorithm

The fix engine applies fixes using reverse position ordering to avoid
offset drift:

``` python
def apply_fixes( self, source_code, fixes, apply_dangerous = False ):
    ''' Applies fixes with safety filtering and conflict resolution. '''
    # 1. Filter by safety level
    applicable = self._filter_by_safety( fixes, apply_dangerous )
    # 2. Sort by position (reverse order - end of file first)
    ordered = sorted(
        applicable,
        key = lambda f: ( f.violation.line, f.violation.column ),
        reverse = True )
    # 3. Track modified ranges for conflict detection
    modified_ranges: list[ tuple[ int, int ] ] = [ ]
    applied: list[ Fix ] = [ ]
    skipped: list[ Fix ] = [ ]
    # 4. Apply fixes sequentially
    modified = source_code
    for fix in ordered:
        if self._conflicts_with_modified( fix, modified_ranges ):
            skipped.append( fix )
            continue
        transformer = fix.transformer_factory( )
        module = __.libcst.parse_module( modified )
        modified = module.visit( transformer ).code
        modified_ranges.append( self._range_for_fix( fix ) )
        applied.append( fix )
    return FixResult(
        original = source_code,
        modified = modified,
        applied_fixes = tuple( applied ),
        skipped_fixes = tuple( skipped ) )
```

### Conflict Resolution Strategy

When multiple fixes target overlapping source regions:

1. **Position priority**: Fixes are applied from end of file toward beginning
2. **Range tracking**: Modified line ranges are recorded after each fix
3. **Overlap detection**: Subsequent fixes overlapping modified ranges are skipped
4. **Skip reporting**: Skipped fixes are reported in FixResult for user awareness

This approach ensures:

- No offset drift from earlier modifications affecting later positions
- No corruption from overlapping transformations
- Transparent reporting of what was and wasn't applied

## Engine Integration

### Extending Linter Engine

The linter engine gains fix collection capabilities:

``` python
class Engine:
    # ... existing methods ...

    def collect_fixes(
        self,
        source_code: __.typx.Annotated[
            str, __.ddoc.Doc( 'Source code to analyze.' ) ],
        filename: __.typx.Annotated[
            str, __.ddoc.Doc( 'Logical filename for source.' ) ] = '<string>',
        enabled_rules: __.typx.Annotated[
            __.Absential[ frozenset[ str ] ],
            __.ddoc.Doc( 'Rules to collect fixes from. Defaults to all fixable.' )
        ] = __.absent,
    ) -> __.typx.Annotated[
        tuple[ Fix, ... ],
        __.ddoc.Doc( 'Fixes collected from enabled fixable rules.' ),
    ]:
        ''' Collects fixes from fixable rules after violation detection.

            Reuses the same CST traversal as lint_source, then gathers
            fixes from rules that implement FixableRule.collect_fixes().
        '''
        # Same setup as lint_source
        wrapper, source_lines = self._create_metadata_wrapper( source_code, filename )
        rules = self._instantiate_rules( wrapper, source_lines, filename )
        # Execute rules (same as check)
        for rule in rules:
            wrapper.visit( rule )
        # Collect fixes from fixable rules
        fixes: list[ Fix ] = [ ]
        for rule in rules:
            if isinstance( rule, FixableRule ) and rule.supports_fix:
                fixes.extend( rule.collect_fixes( ) )
        return tuple( fixes )
```

## CLI Integration

### FixCommand Implementation

The CLI fix command wires together the components:

``` python
class FixCommand( __.immut.DataclassObject ):
    ''' Applies automated fixes with safety controls. '''

    paths: PathsArgument = ( '.',)
    select: __.Absential[ RuleSelectorArgument ] = __.absent
    simulate: bool = False
    diff_format: DiffFormats = DiffFormats.Unified
    apply_dangerous: bool = False

    async def __call__( self, display: DisplayOptions ) -> int:
        ''' Executes fix command. '''
        config = discover_configuration( )
        file_paths = _discover_python_files( self.paths )
        engine = _create_engine( config )
        fix_engine = FixEngine( )
        exit_code = 0
        for file_path in file_paths:
            source_code = file_path.read_text( encoding = 'utf-8' )
            fixes = engine.collect_fixes( source_code, str( file_path ) )
            if not fixes: continue
            result = fix_engine.apply_fixes(
                source_code, fixes, self.apply_dangerous )
            if self.simulate:
                diff = fix_engine.generate_diff( result, self.diff_format.value )
                _display_diff( diff, file_path, display )
            else:
                file_path.write_text( result.modified, encoding = 'utf-8' )
                _display_applied( result, file_path, display )
            if result.skipped_fixes: exit_code = 1
        return exit_code
```

## Module Organization

### Framework Module Structure

```
sources/vibelinter/
├── rules/
│   ├── fixable.py              # FixableRule, Fix, FixSafety
│   └── implementations/
│       ├── vbl103.py           # Bracket spacing (fixable)
│       ├── vbl104.py           # Keyword argument spacing (fixable)
│       └── ...
├── fixer.py                    # FixEngine, FixResult
└── cli.py                      # FixCommand implementation
```

## Line Reformatting Design

### Overview

Line reformatting addresses violations where content exceeds the maximum
line length (79 characters per style guide). The algorithm uses a "left
center of gravity" approach: earlier/higher lines in a multi-line
expression should be lighter (fewer tokens), with content flowing downward.

### Progressive Breaking Algorithm

When a line exceeds the limit, the reformatter applies breaks progressively
until the line fits. Each step adds one level of breaking:

| Step | Action | Trailing Comma |
|------|--------|----------------|
| 1 | Move content after opening delimiter to next line; closing stays with content | No |
| 2 | Move closing delimiter to its own line | Yes (collections) / No (calls) |
| 3 | Split elements one-per-line | Yes (collections) / No (calls) |
| 4+ | Recurse into nested structures | Inherit context |

### Visual Progression

```
Step 0 (violation):
config = { 'name': 'example', 'settings': { 'timeout': 30, 'retries': 3 }, 'enabled': True }

Step 1 (content to next line):
config = {
    'name': 'example', 'settings': { 'timeout': 30, 'retries': 3 }, 'enabled': True }

Step 2 (closing to own line, trailing comma added):
config = {
    'name': 'example', 'settings': { 'timeout': 30, 'retries': 3 }, 'enabled': True,
}

Step 3 (one-per-line):
config = {
    'name': 'example',
    'settings': { 'timeout': 30, 'retries': 3 },
    'enabled': True,
}

Step 4 (recurse into nested):
config = {
    'name': 'example',
    'settings': {
        'timeout': 30, 'retries': 3 },
    'enabled': True,
}
```

### Function Call Constraints

Function calls have additional constraints beyond collections:

- **Positional/nominative grouping**: Keep positional arguments together,
  keep keyword arguments together
- **No trailing comma**: Function calls omit trailing comma after final
  argument (per style guide)
- **Closing on content line**: Closing parenthesis stays on same line as
  final argument unless one-per-line mode

``` python
# Step 0 (violation):
result = process_data( input_file, output_file, format = 'json', validate = True, strict = False )

# Step 1 (content to next line, args grouped):
result = process_data(
    input_file, output_file,
    format = 'json', validate = True, strict = False )

# Step 2 (one-per-line, no trailing comma):
result = process_data(
    input_file,
    output_file,
    format = 'json',
    validate = True,
    strict = False )
```

### Single-Line Body Compaction

Control flow statements (`if`, `for`, `while`, `try`, `except`, `with`)
with single-statement bodies use a threshold-based decision for single-line
vs multi-line form.

#### Threshold Configuration

``` python
class LineLengthConfiguration( __.immut.DataclassObject ):
    ''' Configuration for line length and compaction rules. '''
    max_line_length: __.typx.Annotated[
        int, __.ddoc.Doc( 'Maximum line length.' ) ] = 79
    single_line_threshold_ratio: __.typx.Annotated[
        float,
        __.ddoc.Doc(
            'Ratio of max_line_length for single-line body compaction. '
            'If statement + body <= max_line_length * ratio, use single-line.'
        ) ] = 0.70
```

With defaults: `79 * 0.70 = 55.3` → single-line if total ≤ 55 characters.

#### Compaction Rules

| Condition | Action |
|-----------|--------|
| Total length ≤ threshold | Use single-line: `if x: return y` |
| Total length > threshold | Use multi-line form |
| Body has multiple statements | Always multi-line |
| Body contains nested control flow | Always multi-line |

#### Examples

``` python
# Short enough for single-line (≤55 chars):
if not data: return None
for item in items: process( item )
try: value = op( )
except ValueError: return default

# Too long for single-line (>55 chars):
if not validate_input( data ):
    return InvalidInputError( "Validation failed." )

# Multiple statements - always multi-line:
if error:
    log_error( error )
    raise error
```

### Algorithm Implementation

``` python
class LineReformatter:
    ''' Reformats lines exceeding length limit using left-gravity algorithm. '''

    def __init__( self, config: LineLengthConfiguration ) -> None:
        self._config = config
        self._threshold = int(
            config.max_line_length * config.single_line_threshold_ratio )

    def reformat_expression(
        self,
        node: __.libcst.CSTNode,
        current_indent: int,
    ) -> __.libcst.CSTNode:
        ''' Progressively breaks expression until it fits line limit. '''
        for break_level in range( 1, self._max_break_level( node ) + 1 ):
            reformatted = self._apply_break_level( node, break_level, current_indent )
            if self._fits_line_limit( reformatted, current_indent ):
                return reformatted
        return reformatted  # Best effort if still too long

    def should_compact_body(
        self,
        control_node: __.libcst.CSTNode,
        body_node: __.libcst.CSTNode,
    ) -> bool:
        ''' Determines if control flow body should use single-line form. '''
        if self._has_multiple_statements( body_node ): return False
        if self._has_nested_control_flow( body_node ): return False
        total_length = self._estimate_single_line_length( control_node, body_node )
        return total_length <= self._threshold

    def _apply_break_level(
        self,
        node: __.libcst.CSTNode,
        level: int,
        indent: int,
    ) -> __.libcst.CSTNode:
        ''' Applies specific break level to node. '''
        match level:
            case 1: return self._move_content_to_next_line( node, indent )
            case 2: return self._move_closing_to_own_line( node, indent )
            case 3: return self._split_elements_per_line( node, indent )
            case _: return self._recurse_into_nested( node, level - 3, indent )
```

### Trailing Comma Logic

``` python
def _needs_trailing_comma(
    self,
    node: __.libcst.CSTNode,
    break_level: int,
) -> bool:
    ''' Determines if trailing comma should be added. '''
    # Function calls never get trailing commas
    if isinstance( node, __.libcst.Call ): return False
    # Collections get trailing comma when closing is on own line (level >= 2)
    if isinstance( node, ( __.libcst.List, __.libcst.Dict, __.libcst.Set, __.libcst.Tuple ) ):
        return break_level >= 2
    return False
```

### Safety Classification

Line reformatting fixes are classified as **Safe** because:

- Changes are purely whitespace/formatting
- No semantic impact on code execution
- Preserves all tokens and their order
- Only affects visual layout

## Design Validation

### Practices Compliance

- Wide parameter types for public interfaces (`__.cabc.Sequence[ Fix ]`)
- Narrow return types (`tuple[ Fix, ... ]`, `FixResult`)
- Immutable data structures (`__.immut.DataclassObject`)
- Exception handling follows established patterns

### Style Compliance

- Function signatures follow spacing and bracket conventions
- Docstrings use narrative mood with triple single-quotes
- Type annotations use `__.typx.Annotated` with `__.ddoc` documentation

### Architecture Compliance

- Extends existing single-pass CST traversal
- Separation of detection (visitor) and fixing (transformer)
- Safety classification maps to existing CLI `--apply-dangerous` flag
- Fix engine provides conflict resolution and transparent reporting
