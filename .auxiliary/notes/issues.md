# Known Issues and Investigation Notes

## Missing appcore Globals Instance Integration

**Status**: Open
**Priority**: High
**Assigned**: Future session

### Problem

The CLI does not currently initialize or use an `appcore.Globals` instance, which means:

1. **Configuration discovery uses `Path.cwd()` instead of `globals.distribution.location`**
   - Current implementation in `cli.py:277`: `config = _configuration.discover_configuration()`
   - This defaults to searching from current working directory
   - Should use `globals.distribution.location` as the starting point

2. **No access to distribution metadata**
   - Cannot reliably determine package root directory
   - Cannot distinguish between development and production installations
   - Missing access to package data files via `distribution.provide_data_location()`

### Expected Behavior

Per the appcore pattern (see `https://raw.githubusercontent.com/emcd/python-appcore/refs/heads/master/sources/appcore/distribution.py`):

1. CLI initialization should create a `Globals` instance
2. `Globals` provides `distribution.location` which points to:
   - **Development**: Project root (where `pyproject.toml` is)
   - **Production**: Installed package location
3. Configuration discovery should use `globals.distribution.location` as `start_directory`

### Files Affected

- `sources/vibelinter/cli.py` - Needs Globals initialization
- `sources/vibelinter/configuration.py` - Already supports `start_directory` parameter
- Tests remain valid - they test the public API with explicit paths

### References

- Appcore distribution module: `https://github.com/emcd/python-appcore/blob/master/sources/appcore/distribution.py`
- Current configuration discovery: `sources/vibelinter/configuration.py:86-97`
- Current CLI usage: `sources/vibelinter/cli.py:277`

### Notes

This was supposed to be handled when the CLI stub was initially built. The infrastructure for proper appcore integration is missing.
