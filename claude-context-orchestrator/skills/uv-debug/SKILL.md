---
name: uv-debug
description: Troubleshooting and debugging problems with uv (Python package manager). Use when encountering uv installation issues, stale build cache, package not updating, or discrepancies between uv run and global installs.
---

# UV Debugging Skill

## Purpose

This skill provides systematic troubleshooting workflows for common `uv` (Python package manager) issues, with particular focus on build cache problems, installation discrepancies, and package update issues.

## When to Use This Skill

Use this skill when encountering:

- Code changes not appearing after `uv tool install`
- Discrepancy between `uv run <command>` and globally installed command
- New files/modules missing from installed package
- "Command not found" after installation
- Stale build cache issues
- Installation mode confusion (editable vs production)

## Core Concepts

### UV Installation Modes

**Production Install:**
```bash
uv tool install .
```
- Builds wheel package (cached snapshot)
- Fast to install, slow to update
- Requires reinstall after code changes
- Isolated from source directory

**Editable Install:**
```bash
uv tool install --editable .
```
- Creates symlinks to source directory
- Changes reflect immediately
- Best for active development
- Less isolated

**Local Environment:**
```bash
uv sync          # Setup environment
uv run <command> # Execute from source
```
- No global install needed
- Always uses current source code
- Fastest iteration cycle
- Recommended for development

### Build Cache Location

**Global tool installs:**
```
~/.local/share/uv/tools/<package-name>/
```

**Build artifacts:**
```
build/          - Temporary build files
dist/           - Built wheels (.whl) and source distributions
*.egg-info/     - Package metadata and file manifest
```

## Troubleshooting Workflows

### Workflow 1: Code Changes Not Appearing

**Symptoms:**
- Ran `uv tool install .` or `make install`
- Code changes don't appear in installed command
- New files/modules missing

**Diagnostic Steps:**

1. **Verify the discrepancy:**
   ```bash
   # Check which version is running
   which <command>

   # Test local version
   uv run <command> --help

   # Test global version
   <command> --help
   ```

2. **Check for stale build artifacts:**
   ```bash
   ls -la build/ dist/ *.egg-info 2>/dev/null
   ```

3. **Identify installation mode:**
   ```bash
   # Check if editable install
   ls ~/.local/share/uv/tools/<package>/ | grep -i editable
   ```

**Solutions (in order of preference):**

**Solution A: Clean and Reinstall (Recommended)**
```bash
# Remove stale artifacts
rm -rf build/ dist/ *.egg-info

# Force fresh build
uv tool install --force .

# Verify
<command> --help
```

**Solution B: Use Makefile Pattern**
```makefile
install: clean
	uv tool install --force .

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

**Solution C: Switch to Local Environment**
```bash
# Setup once
uv sync

# Use for development
uv run <command>
```

**Solution D: Use Editable Mode**
```bash
uv tool install --editable .
```

### Workflow 2: New Module Not Found

**Symptoms:**
- Added new Python file (e.g., `mypackage/commands/new_cmd.py`)
- `ModuleNotFoundError` or command not recognized
- `uv run` works but global install doesn't

**Root Cause:**
Wheel package built before new file existed. Package metadata (`*.egg-info/RECORD`) doesn't list the new file.

**Solution:**
```bash
# 1. Clean build artifacts
rm -rf build/ dist/ *.egg-info

# 2. Reinstall with force
uv tool install --force .

# 3. Verify new module appears
<command> <new-subcommand> --help
```

**Prevention:**
Add to Makefile:
```makefile
install: clean
	uv tool install --force .
```

### Workflow 3: Debugging Installation Location

**Symptoms:**
- Unsure which version is running
- Multiple installations conflict
- Changes not appearing despite reinstall

**Diagnostic Commands:**

```bash
# 1. Check which executable
which <command>

# 2. Check Python import location
python3 -c "import <package>; print(<package>.__file__)"

# 3. List all installations
find ~/.local/share/uv/tools -name "<package>*"

# 4. Check if editable install
cat ~/.local/share/uv/tools/<package>/*/site-packages/*.pth 2>/dev/null
```

**Interpretation:**

If `which <command>` shows:
- `~/.local/share/uv/tools/` → Global uv install
- `/usr/local/bin/` → System-wide install (pip)
- `<project>/.venv/bin/` → Virtual environment

If `.pth` file exists → Editable install (points to source)

### Workflow 4: Entry Point Not Updating

**Symptoms:**
- Changed command name or added new subcommand
- Entry point not updating in installed version

**Root Cause:**
Entry points defined in `pyproject.toml` are baked into wheel at build time.

**Solution:**

1. **Verify entry point definition:**
   ```bash
   # Read pyproject.toml
   grep -A 10 "\[project.scripts\]" pyproject.toml
   ```

2. **Clean and rebuild:**
   ```bash
   rm -rf build/ dist/ *.egg-info
   uv tool install --force .
   ```

3. **Verify entry points installed:**
   ```bash
   ls ~/.local/share/uv/tools/<package>/*/bin/
   ```

### Workflow 5: Dependency Issues

**Symptoms:**
- Import errors for dependencies
- Version conflicts
- `ModuleNotFoundError` for installed packages

**Diagnostic:**

```bash
# Check installed dependencies
uv pip list

# Check project dependencies
grep -A 20 "dependencies" pyproject.toml

# Check dependency resolution
uv pip tree
```

**Solution:**

```bash
# Sync dependencies
uv sync --all-extras

# Or for global install
uv tool install --force --reinstall-package <package> .
```

## Decision Tree

```
Code changes not appearing?
├─ Does `uv run <cmd>` work?
│  ├─ Yes → Stale build cache
│  │  └─ Solution: rm -rf build/ dist/ *.egg-info && uv tool install --force .
│  └─ No → Code issue, not cache
│     └─ Debug the code itself
│
├─ New file/module missing?
│  └─ Solution: Clean build artifacts and reinstall
│
├─ Entry point not found?
│  └─ Check pyproject.toml [project.scripts], then clean and reinstall
│
└─ Dependency missing?
   └─ Run uv sync or uv tool install --reinstall-package
```

## Best Practices

### Development Workflow

**Option 1: Local Environment (Recommended)**
```bash
# Setup once
uv sync

# Develop with instant updates
uv run <command>
uv run pytest
```

**Option 2: Editable Install**
```bash
# Install once
uv tool install --editable .

# Changes reflect immediately
<command>  # Always uses latest source
```

**Option 3: Production Build with Makefile**
```bash
# Makefile ensures clean builds
make install

# Reinstall after each change
make install
```

### Testing Installation

Before distributing or deploying:

```bash
# 1. Clean environment
rm -rf build/ dist/ *.egg-info

# 2. Production build
uv tool install --force .

# 3. Test from clean shell
<command> --help
<command> <subcommand>

# 4. Verify all entry points
ls ~/.local/share/uv/tools/<package>/*/bin/
```

## Common Mistakes

### Mistake 1: Assuming `--force` Cleans Cache

**Wrong:**
```bash
uv tool install --force .  # Doesn't clean build artifacts!
```

**Right:**
```bash
rm -rf build/ dist/ *.egg-info
uv tool install --force .
```

**Why:** `--force` reinstalls but may reuse cached wheel from `dist/`.

### Mistake 2: Editing Global Install Directly

**Wrong:**
```bash
# Editing files in ~/.local/share/uv/tools/<package>/
vim ~/.local/share/uv/tools/<package>/.../myfile.py
```

**Right:**
```bash
# Edit source, then reinstall
vim mypackage/myfile.py
make install
```

### Mistake 3: Mixing Installation Methods

**Problem:**
```bash
uv tool install .           # Production install
# Later...
uv tool install --editable . # Now editable
# Changes behavior unpredictably
```

**Solution:**
Pick one method and stick with it, or uninstall first:
```bash
uv tool uninstall <package>
uv tool install --editable .
```

## Advanced Debugging

### Inspecting Wheel Contents

```bash
# Build wheel
uv build

# List contents
unzip -l dist/*.whl

# Extract and examine
unzip dist/*.whl -d /tmp/wheel-inspect
ls -la /tmp/wheel-inspect/<package>/
```

### Checking Package Metadata

```bash
# View installed package info
uv pip show <package>

# View RECORD file (manifest of installed files)
cat ~/.local/share/uv/tools/<package>/*/*.dist-info/RECORD
```

### Debugging Import Paths

```python
import sys
print("Python path:")
for p in sys.path:
    print(f"  {p}")

import <package>
print(f"\nPackage location: {<package>.__file__}")
```

## Reference: Build Process

Understanding what happens during `uv tool install .`:

1. **Read metadata** - Parse `pyproject.toml` for package info
2. **Collect files** - Find all Python files in package
3. **Build wheel** - Create `.whl` in `dist/`
4. **Write manifest** - Record all files in `*.egg-info/RECORD`
5. **Install wheel** - Copy to `~/.local/share/uv/tools/<package>/`
6. **Create entry points** - Generate executables in `bin/`

**Key insight:** Steps 3-4 create a snapshot. New files added after this won't be included until rebuild.

## Quick Reference

**Check what's running:**
```bash
which <command>
uv run <command> --version
<command> --version
```

**Clean build cache:**
```bash
rm -rf build/ dist/ *.egg-info
```

**Fresh install:**
```bash
uv tool install --force .
```

**Development mode:**
```bash
uv sync && uv run <command>
```

**Inspect installation:**
```bash
ls ~/.local/share/uv/tools/<package>/
uv pip show <package>
```

## Official UV Documentation

**Cache Management:**
- https://docs.astral.sh/uv/concepts/cache/ - How UV caches packages, cache types, cache location, cache commands

**Build Troubleshooting:**
- https://docs.astral.sh/uv/reference/troubleshooting/build-failures/ - Common build errors, missing dependencies, build isolation issues

**CLI Commands:**
- https://docs.astral.sh/uv/reference/cli/ - Complete command reference with all flags and options

**Settings Reference:**
- https://docs.astral.sh/uv/reference/settings/ - Configuration options for build constraints, cache control, dependency resolution

## Internal References

For deep technical details, see:
- `references/python-build-cache.md` - Why Python build cache doesn't auto-update
- `references/uv-cli-reference.md` - UV command workflows and examples

## Troubleshooting Checklist

When encountering issues:

- [ ] Does `uv run <command>` work? (Rules out code issues)
- [ ] Are there stale artifacts in `build/`, `dist/`, `*.egg-info`?
- [ ] Which installation mode am I using? (production/editable/local)
- [ ] Did I recently add new files?
- [ ] Did I update `pyproject.toml` dependencies or entry points?
- [ ] Am I using the right `which <command>` version?
- [ ] Have I tried cleaning and reinstalling?

## Exit Codes

Common uv exit codes:
- `0` - Success
- `1` - General error
- `2` - Command line usage error
- `101` - Package not found
- `102` - Version conflict
