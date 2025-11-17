# Known Issues and Investigation Notes

## DataclassProtocol + Protocol Multiple Inheritance

**Status**: Needs investigation
**Date**: 2025-11-17
**Context**: Refactoring RenderableResult base class

### Issue

When attempting to create `RenderableResult` with multiple inheritance from both
`__.immut.DataclassProtocol` and `__.typx.Protocol`, type checking errors occurred
with pyright reporting incompatible `__init__` signatures between the protocol and
the dataclass result classes.

### Current Implementation

```python
@__.typx.runtime_checkable
class RenderableResult( __.typx.Protocol ):
    ''' Protocol for command results with format-specific rendering. '''

    @__.abc.abstractmethod
    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ...

    @__.abc.abstractmethod
    def render_as_text( self ) -> tuple[ str, ... ]:
        ...
```

### Attempted Implementation

```python
class RenderableResult( __.immut.DataclassProtocol, __.typx.Protocol ):
    # Same methods as above
```

### Error

Pyright reported errors like:
```
Argument of type "CheckResult" cannot be assigned to parameter "result" of type "RenderableResult"
  "CheckResult" is incompatible with protocol "RenderableResult"
    "__init__" is an incompatible type
      Type "(*, paths: tuple[str, ...], ...) -> None" is not assignable to type "() -> None"
        Extra parameter "paths"
```

### Expected Behavior

According to the maintainer, `DataclassProtocol` was designed to be compatible with
`Protocol` and has been successfully used in other parts of the codebase with this
pattern. The combination should allow structural subtyping while properly handling
dataclass `__init__` signatures.

### Investigation Needed

- Verify whether the issue is specific to this use case or a general problem
- Check examples in other parts of the codebase where this pattern works
- Determine if there's a missing import, decorator, or configuration
- Consider whether the issue relates to how the result classes are defined

### Solution Found - DataclassProtocol Provides Dataclass Machinery

**Date**: 2025-11-17
**Status**: RESOLVED

**Failed Approach**:
Initially attempted to inherit from both `DataclassObject` and `RenderableResult`:
```python
class RenderableResult( __.immut.DataclassProtocol, __.typx.Protocol ):
    @__.abc.abstractmethod
    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ...

class CheckResult( __.immut.DataclassObject, RenderableResult ):  # WRONG!
    paths: tuple[ str, ... ]
    # ...
```

This caused metaclass conflict: `Dataclass` vs `ProtocolDataclass`.

**Successful Approach**:
The key insight is that `DataclassProtocol` itself provides the dataclass machinery,
so result classes should ONLY inherit from `RenderableResult`:

```python
class RenderableResult( __.immut.DataclassProtocol, __.typx.Protocol ):
    @__.abc.abstractmethod
    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        ...
    @__.abc.abstractmethod
    def render_as_text( self ) -> tuple[ str, ... ]:
        ...

class CheckResult( RenderableResult ):  # CORRECT!
    paths: tuple[ str, ... ]
    context_lines: int
    jobs: __.typx.Union[ int, str ]
    rule_selection: __.Absential[ str ] = __.absent

    def render_as_json( self ) -> dict[ str, __.typx.Any ]:
        # Implementation
        ...

    def render_as_text( self ) -> tuple[ str, ... ]:
        # Implementation
        ...
```

**Results**:
- ✅ Pyright: 0 errors, 0 warnings
- ✅ Ruff: All checks passed
- ✅ Isort: Clean

**Key Lessons**:
1. `DataclassProtocol` provides complete dataclass functionality via its metaclass
2. Cannot combine `DataclassObject` with `DataclassProtocol` - they have incompatible metaclasses
3. Use either `DataclassObject` OR `DataclassProtocol`, not both
4. When using `DataclassProtocol` + `Protocol`, subclasses inherit from the protocol directly

### Previous Workaround (Now Obsolete)

Currently using `__.typx.Protocol` alone with `@__.typx.runtime_checkable`, which
provides structural subtyping without the dataclass-specific protocol features.
Result classes satisfy the protocol through their method implementations without
explicit inheritance. This works correctly but doesn't leverage DataclassProtocol's
features.
