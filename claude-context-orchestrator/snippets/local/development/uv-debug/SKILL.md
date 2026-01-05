---
name: uv-debug
description: Troubleshooting uv (Python package manager) issues - stale cache, installation problems, package updates.
---

# UV Debugging

## Installation Modes

| Mode | Command | Updates | Best For |
|------|---------|---------|----------|
| **Production** | `uv tool install .` | Requires reinstall | Distribution |
| **Editable** | `uv tool install --editable .` | Immediate | Active dev |
| **Local** | `uv sync` + `uv run <cmd>` | Immediate | Recommended |

## Cache Locations

```
~/.local/share/uv/tools/<package>/  # Global installs
build/  dist/  *.egg-info/          # Build artifacts (source of problems!)
```

## Code Changes Not Appearing?

**Decision Tree:**
```
Does `uv run <cmd>` work?
├─ Yes → Stale build cache → Clean and reinstall
└─ No  → Code issue, not cache
```

**The Fix (90% of cases):**
```bash
rm -rf build/ dist/ *.egg-info
uv tool install --force .
```

**Diagnostic:**
```bash
which <command>                    # Which version running?
uv run <command> --help            # Local version works?
ls -la build/ dist/ *.egg-info     # Stale artifacts?
```

## Common Mistakes

### `--force` doesn't clean cache!
```bash
# Wrong - may reuse cached wheel
uv tool install --force .

# Right - clean first
rm -rf build/ dist/ *.egg-info && uv tool install --force .
```

### Makefile pattern
```makefile
install: clean
	uv tool install --force .

clean:
	rm -rf build/ dist/ *.egg-info
```

## New Module Not Found?

Wheel was built before file existed.

```bash
rm -rf build/ dist/ *.egg-info
uv tool install --force .
```

## Entry Point Not Updating?

Entry points baked into wheel at build time.

```bash
grep -A 10 "\[project.scripts\]" pyproject.toml  # Verify definition
rm -rf build/ dist/ *.egg-info
uv tool install --force .
ls ~/.local/share/uv/tools/<package>/*/bin/      # Verify installed
```

## Debug Installation Location

```bash
which <command>                                              # Where?
python3 -c "import <pkg>; print(<pkg>.__file__)"            # Python path
find ~/.local/share/uv/tools -name "<package>*"              # All installs
cat ~/.local/share/uv/tools/<pkg>/*/site-packages/*.pth     # Editable?
```

## Quick Reference

```bash
# Check versions
which <cmd> && uv run <cmd> --version && <cmd> --version

# Clean rebuild
rm -rf build/ dist/ *.egg-info && uv tool install --force .

# Development mode
uv sync && uv run <command>

# Inspect
ls ~/.local/share/uv/tools/<package>/
uv pip show <package>
```

## Docs

- Cache: https://docs.astral.sh/uv/concepts/cache/
- Build issues: https://docs.astral.sh/uv/reference/troubleshooting/build-failures/
- CLI: https://docs.astral.sh/uv/reference/cli/
