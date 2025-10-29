---
description: Troubleshooting guide for Python package build cache issues
SNIPPET_NAME: python-package-build-cache
ANNOUNCE_USAGE: false
---

# Python Package Build Cache Issues

## Symptoms

- Code changes don't appear after `pip install .` or `uv tool install .`
- New files/modules missing from installed package
- `uv run` shows changes but globally installed command doesn't
- `make install` doesn't reflect latest code

## Root Cause

Non-editable installs build a wheel package (cached snapshot) that doesn't automatically update when source changes. The wheel is stored in:
- `build/` - Built package files
- `dist/` - Distribution archives
- `*.egg-info` - Package metadata

For `uv tool install`, the cached wheel lives in `~/.local/share/uv/tools/`.

## Solutions

### 1. Clean Before Install (Recommended for Production)

```bash
rm -rf build/ dist/ *.egg-info
uv tool install --force .
```

**Makefile pattern:**
```makefile
install: clean
	uv tool install --force .

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

### 2. Use Editable Mode (Development)

```bash
uv tool install --editable .  # Changes reflect immediately
```

**Note:** Editable mode creates symlinks to source directory instead of building a wheel.

### 3. Use Local Environment (Best for Development)

```bash
uv sync          # Create/update local environment
uv run <command> # Always uses current source
```

**Workflow:**
1. Run `uv sync` once to set up environment
2. Use `uv run <command>` instead of global install
3. No reinstall needed - changes always reflected

## Build Artifacts to Clean

```bash
build/          # Built package files
dist/           # Distribution archives
*.egg-info      # Package metadata
__pycache__/    # Bytecode cache (optional, recreated automatically)
.pytest_cache/  # Test cache
.ruff_cache/    # Linter cache (if using ruff)
.mypy_cache/    # Type checker cache (if using mypy)
```

## Installation Modes Comparison

| Mode | Command | When to Use | Changes Reflect? | Rebuild Needed? |
|------|---------|-------------|------------------|-----------------|
| Production | `uv tool install .` | Stable releases | No | Yes |
| Editable | `uv tool install --editable .` | Active development | Yes | No |
| Local Env | `uv sync` + `uv run` | Development (recommended) | Yes | No |

## Debugging Steps

1. **Check which version is running:**
   ```bash
   which <command>           # Shows path to executable
   <command> --version       # If version command exists
   ```

2. **Compare local vs global:**
   ```bash
   uv run <command> <args>   # Uses local source
   <command> <args>          # Uses global install
   ```

3. **Clean and rebuild:**
   ```bash
   rm -rf build/ dist/ *.egg-info
   uv tool install --force .
   ```

4. **Verify package contents:**
   ```bash
   # For local environment
   uv run python -c "import <package>; print(<package>.__file__)"

   # For global install
   python -c "import <package>; print(<package>.__file__)"
   ```

## Common Gotchas

- **New files not appearing:** Package metadata (`.egg-info`) lists files at build time. Adding new modules requires rebuild.
- **Global vs local mismatch:** `uv run` uses local environment, global command uses cached wheel.
- **Stale imports:** Python caches imports in `__pycache__/`. Usually not an issue, but can delete if suspicious.
- **Force flag not enough:** `--force` reinstalls but may reuse cached wheel. Must clean build artifacts first.

## Real-World Example

**Scenario:** Added new file `myproject/commands/workflows.py`

```bash
# This won't show the new command (stale wheel)
uv tool install --force .
myproject workflows  # Command not found

# This works (uses local source)
uv run myproject workflows  # Works!

# Fix global install
rm -rf build/ dist/ *.egg-info
uv tool install --force .
myproject workflows  # Now works!
```

## When to Use Each Approach

**Use Production Install (`uv tool install .`) when:**
- Deploying to production
- Installing stable released versions
- Users installing your tool

**Use Editable Install (`--editable`) when:**
- Actively developing a tool
- Need global command that stays in sync with source
- Making frequent changes

**Use Local Environment (`uv run`) when:**
- Developing libraries or CLI tools
- Want fastest iteration cycle
- Don't need global command availability
- Working with multiple projects (isolation)

---

**TL;DR:** Use `make install` with `clean` dependency for reliable production builds, or `uv sync` + `uv run` for development (no rebuild needed).
