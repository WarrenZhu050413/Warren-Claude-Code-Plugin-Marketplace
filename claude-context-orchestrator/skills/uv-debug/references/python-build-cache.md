# Python Build Cache Deep Dive

## Overview

This document explains in detail how Python's packaging system caches builds, why this causes "code not updating" issues, and the technical mechanisms behind different installation modes.

## The Build Process

### Standard Build (Non-Editable)

When running `uv tool install .` or `pip install .`:

```
Source Code → setup.py/pyproject.toml → Build Backend → Wheel → Installation
```

**Step-by-step breakdown:**

1. **Parse metadata:**
   - Read `pyproject.toml` or `setup.py`
   - Extract: name, version, dependencies, entry points
   - Determine which files to include

2. **Collect source files:**
   - Find all `.py` files in package
   - Apply MANIFEST.in rules (if exists)
   - Apply `pyproject.toml` includes/excludes

3. **Build wheel (.whl):**
   - Compile C extensions (if any)
   - Copy Python files
   - Generate metadata files
   - Create ZIP archive named `<package>-<version>-py3-none-any.whl`
   - Store in `dist/` directory

4. **Generate metadata:**
   - Create `<package>.egg-info/` directory
   - Write `SOURCES.txt` (list of source files used)
   - Write `RECORD` (list of files to install)
   - Write `entry_points.txt` (console scripts)
   - Write `requires.txt` (dependencies)

5. **Install wheel:**
   - Extract wheel to installation directory
   - Create entry point executables in `bin/`
   - Update Python's package registry

**Key files created:**

```
build/
├── lib/
│   └── mypackage/
│       └── (compiled files)
└── bdist.*/
    └── (platform-specific builds)

dist/
└── mypackage-1.0.0-py3-none-any.whl  ← The cached snapshot

mypackage.egg-info/
├── SOURCES.txt         ← Source files at build time
├── RECORD              ← Files to install
├── entry_points.txt    ← Console scripts
└── requires.txt        ← Dependencies
```

### Why It's a Snapshot

**The wheel is a frozen moment in time:**

```python
# At build time (t=0):
mypackage/
├── __init__.py      ← Included in wheel
├── cli.py           ← Included in wheel
└── commands/
    ├── send.py      ← Included in wheel
    └── read.py      ← Included in wheel

# After adding new file (t=1):
mypackage/
├── __init__.py
├── cli.py
└── commands/
    ├── send.py
    ├── read.py
    └── workflows.py  ← NOT in wheel! Built at t=0
```

**The wheel still contains only files from t=0:**
```bash
$ unzip -l dist/mypackage-1.0.0-py3-none-any.whl
  mypackage/__init__.py
  mypackage/cli.py
  mypackage/commands/send.py
  mypackage/commands/read.py
  # workflows.py is MISSING
```

**Even `--force` reinstall uses this stale wheel:**
```bash
uv tool install --force .
# Still installs the old wheel from dist/!
```

## Installation Locations

### UV Tool Install

```
~/.local/share/uv/tools/<package>/
├── bin/
│   └── <command>          ← Executable entry point
├── lib/
│   └── python3.x/
│       └── site-packages/
│           ├── <package>/  ← Package code
│           └── <package>-<version>.dist-info/
│               ├── RECORD
│               ├── entry_points.txt
│               └── METADATA
```

### Editable Install

**Instead of copying files, creates pointer:**

```
~/.local/share/uv/tools/<package>/
├── bin/
│   └── <command>
└── lib/
    └── python3.x/
        └── site-packages/
            ├── __editables__/
            │   └── <package>.pth  ← Points to source directory
            └── <package>-<version>.dist-info/
```

**The `.pth` file contains:**
```
/absolute/path/to/source/directory
```

**Python's import system:**
1. Reads `.pth` file
2. Adds path to `sys.path`
3. Imports directly from source directory
4. New files appear immediately (no reinstall)

### Local Environment (uv run)

**No global installation at all:**

```
project/
├── .venv/
│   ├── bin/
│   │   └── python  ← Local Python interpreter
│   └── lib/
│       └── python3.x/
│           └── site-packages/  ← Dependencies only
├── mypackage/  ← Source code (NOT installed)
└── pyproject.toml
```

**How `uv run` works:**

```bash
uv run mycommand
```

Internally executes:
```bash
PYTHONPATH=/path/to/project:$PYTHONPATH \
  .venv/bin/python -m mypackage.cli
```

**Import resolution:**
1. Check `PYTHONPATH` first (finds `mypackage/` in project root)
2. Import directly from source
3. No build, no cache, always latest

## Why --force Doesn't Help

**Common misconception:**
```bash
uv tool install --force .  # "Force should rebuild, right?"
```

**What `--force` actually does:**
- Uninstalls existing package
- Reinstalls from available sources
- **Does NOT** delete `build/` or `dist/`

**The problem:**

```bash
# 1. First install (builds wheel)
uv tool install .
# Creates: dist/mypackage-1.0.0-py3-none-any.whl

# 2. Add new file
touch mypackage/commands/workflows.py

# 3. Force reinstall
uv tool install --force .
# Finds existing wheel in dist/
# Reinstalls OLD wheel (still no workflows.py!)
```

**Why it finds the old wheel:**

UV's build process:
1. Check if wheel exists in `dist/` matching current version
2. If yes, use that wheel (fast!)
3. If no, build new wheel

**The version in `pyproject.toml` hasn't changed**, so UV reuses the cached wheel.

## How to Force Fresh Build

**Option 1: Clean first**
```bash
rm -rf build/ dist/ *.egg-info
uv tool install --force .
```

**Option 2: Bump version**
```toml
[project]
version = "1.0.1"  # Changed from 1.0.0
```
```bash
uv tool install --force .
# No matching wheel in dist/, builds fresh
```

**Option 3: Build explicitly**
```bash
uv build --force
uv tool install --force .
```

## Metadata Files Deep Dive

### RECORD File

Lists every file installed, with checksums:

```
mypackage/__init__.py,sha256=abc123...,1234
mypackage/cli.py,sha256=def456...,5678
mypackage/commands/send.py,sha256=ghi789...,9012
mypackage/commands/read.py,sha256=jkl012...,3456
```

**New files aren't in RECORD = won't be installed**

### entry_points.txt

Defines console scripts:

```
[console_scripts]
gmail = mypackage.cli:main
```

**This is read at install time to create executables in `bin/`**

Changes to entry points require rebuild.

### SOURCES.txt

Lists source files used during build:

```
mypackage/__init__.py
mypackage/cli.py
mypackage/commands/send.py
mypackage/commands/read.py
setup.py
pyproject.toml
```

**Diagnostic use:** If a file is missing here, it wasn't included in the build.

## Debugging Cache Issues

### Check if wheel is stale

```bash
# 1. List files in wheel
unzip -l dist/*.whl | grep -i workflows
# If empty, file not in wheel

# 2. Check SOURCES.txt
cat *.egg-info/SOURCES.txt | grep workflows
# If empty, file wasn't included in build

# 3. Check build timestamp
ls -la dist/*.whl
# If older than source files, rebuild needed
```

### Compare local vs installed

```bash
# Source files
find mypackage -name "*.py" | sort

# Installed files
find ~/.local/share/uv/tools/mypackage -name "*.py" | sort

# Diff them
diff <(find mypackage -name "*.py" | sort) \
     <(find ~/.local/share/uv/tools/mypackage -name "*.py" | sed 's|.*mypackage|mypackage|' | sort)
```

### Verify import source

```python
import mypackage
print(mypackage.__file__)
# Should point to installed location, not source
```

## Performance Trade-offs

### Why Caching Exists

**Without caching (rebuild every time):**
- Slow: Parsing, file collection, wheel building (seconds to minutes)
- Wasteful: Rebuilding unchanged code
- Inconsistent: Different builds might produce different results

**With caching (reuse wheel):**
- Fast: Just extract and copy (milliseconds)
- Efficient: Build once, install many
- Reproducible: Same wheel = same result

**The trade-off:**
- Development: Need to rebuild after changes (overhead)
- Production: Install is fast and predictable (benefit)

## Best Practices by Use Case

### Active Development
```bash
# Option 1: No install (recommended)
uv sync
uv run mycommand

# Option 2: Editable install
uv tool install --editable .

# Option 3: Makefile automation
make install  # (with clean dependency)
```

### Testing Production Build
```bash
# Clean environment
rm -rf build/ dist/ *.egg-info

# Fresh build
uv tool install --force .

# Test
mycommand --help
```

### Distribution
```bash
# Build wheel
uv build

# Upload to PyPI
uv publish

# Users install
uv tool install mypackage
# (Downloads from PyPI, no source needed)
```

## Common Scenarios

### Scenario 1: Added New Subcommand

**Problem:**
```bash
# Added mypackage/commands/workflows.py
uv tool install --force .
mycommand workflows  # Command not found
```

**Why:**
- Entry point might need updating in `pyproject.toml`
- Or file just not in cached wheel

**Solution:**
```bash
# 1. Check entry points
grep -A 5 "\[project.scripts\]" pyproject.toml

# 2. Clean and rebuild
rm -rf build/ dist/ *.egg-info
uv tool install --force .
```

### Scenario 2: Updated Dependency

**Problem:**
```bash
# Updated pyproject.toml dependencies
uv tool install --force .
# Still using old dependency version
```

**Why:**
- Wheel metadata includes dependency list
- Cached wheel has old requirements

**Solution:**
```bash
rm -rf build/ dist/ *.egg-info
uv tool install --force --reinstall-package <dependency> .
```

### Scenario 3: Moved Files

**Problem:**
```bash
# Moved mypackage/utils.py → mypackage/helpers/utils.py
uv tool install --force .
# Import still finds old location
```

**Why:**
- Old wheel still has `mypackage/utils.py`
- New file at `mypackage/helpers/utils.py` not in wheel

**Solution:**
```bash
rm -rf build/ dist/ *.egg-info
uv tool install --force .
```

## Wheel Internals

### Wheel Format

A wheel is a ZIP archive with structure:

```
mypackage-1.0.0-py3-none-any.whl
├── mypackage/           ← Package code
│   ├── __init__.py
│   └── cli.py
└── mypackage-1.0.0.dist-info/  ← Metadata
    ├── WHEEL            ← Wheel version, tags
    ├── METADATA         ← Package info (name, version, deps)
    ├── RECORD           ← File checksums
    └── entry_points.txt ← Console scripts
```

### Wheel Naming Convention

```
{distribution}-{version}-{python}-{abi}-{platform}.whl
```

Example: `mypackage-1.0.0-py3-none-any.whl`
- `mypackage` - Distribution name
- `1.0.0` - Version
- `py3` - Python 3 compatible
- `none` - No ABI requirement
- `any` - Any platform

**Pure Python wheels use `py3-none-any`**
**Compiled extensions use specific tags (e.g., `cp311-cp311-macosx_11_0_arm64`)**

## Comparison: Other Package Managers

### npm (Node.js)

```bash
npm install    # Installs to node_modules/
npm link       # Similar to editable install
```

**npm doesn't cache builds** - packages are just copied
**No build cache issues** - source and installed are always in sync

### cargo (Rust)

```bash
cargo build    # Builds to target/
cargo install  # Installs from crates.io
```

**cargo caches compiled artifacts** but rebuilds on source changes
**Incremental compilation** - only rebuilds changed files

### pip/uv (Python)

```bash
pip install .        # Builds wheel, installs
pip install -e .     # Editable install
```

**Caches wheels** - can cause stale installs
**Requires explicit rebuild** for changes to appear

## Summary

**Key Takeaways:**

1. **Wheels are snapshots** - Frozen at build time, don't auto-update
2. **Build artifacts cache** - `build/`, `dist/`, `*.egg-info` persist
3. **`--force` doesn't clean** - Reinstalls but may reuse cached wheel
4. **Editable mode works differently** - Uses symlinks, not copies
5. **`uv run` bypasses install** - Runs directly from source
6. **Clean before rebuild** - Only way to guarantee fresh build

**Mental Model:**

```
Source Code ──build──> Wheel (snapshot) ──install──> Installation
     ↓                     ↑                           ↓
   Change              Cached!                   Stale!
     ↓                     ↑                           ↓
Must clean cache to force rebuild
```

**When in doubt:**
```bash
rm -rf build/ dist/ *.egg-info && uv tool install --force .
```
