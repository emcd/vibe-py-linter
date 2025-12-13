## CLI Architecture: Subcommand Organization

**Severity**: Low (refactoring opportunity)
**Component**: `sources/vibelinter/cli.py`
**Discovered**: 2025-12-07 (during describe subcommand implementation)

**Description**: The CLI implementation currently has all subcommands (check, fix, configure, describe, serve) in a single `cli.py` file (755 lines), while the architecture spec (`documentation/architecture/openspec/specs/cli/design.md`) shows a planned structure with separate `subcommands/` directory.

**Current Structure**:
```
sources/vibelinter/
├── cli.py              # All subcommands in one file (755 lines)
└── ... other modules
```

**Planned Structure (per spec)**:
```
sources/vibelinter/
├── cli.py              # Main CLI orchestration
├── subcommands/        # Individual subcommand implementations
│   ├── __init__.py     # Subcommand registry
│   ├── check.py        # Analysis and violation reporting
│   ├── fix.py          # Auto-fix with safety controls
│   ├── configure.py    # Non-destructive configuration management
│   ├── describe.py     # Rule documentation and discovery
│   └── serve.py        # Protocol server modes (future)
└── ... other modules
```

**Impact**:
- Single file is manageable at current size (755 lines)
- All tests pass and implementation works correctly
- Code is well-organized within the file with clear sections
- Future maintenance may benefit from separation as complexity grows

**Recommendation**: Defer refactoring until:
1. File grows significantly larger (e.g., >1500 lines)
2. New subcommands add substantial complexity
3. Team needs parallel development on different subcommands
4. During a planned architectural refactoring phase

**Action**: Document as future refactoring task, not urgent.
