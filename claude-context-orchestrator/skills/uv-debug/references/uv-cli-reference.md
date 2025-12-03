# UV CLI Reference for Troubleshooting

## Overview

This reference covers UV commands and flags commonly used for troubleshooting package installation and build issues.

## Cache Management

### uv cache clean

Remove all or specific cache entries:

```bash
# Remove ALL cache entries
uv cache clean

# Remove cache for specific package
uv cache clean <package-name>

# Example: Clean numpy cache
uv cache clean numpy
```

**When to use:**
- Suspected stale cache causing installation issues
- After manually editing cache (not recommended)
- When builds succeed locally but fail in CI

### uv cache prune

Remove unused cache entries:

```bash
# Remove all unused cache entries
uv cache prune

# CI-optimized: Remove pre-built wheels, keep source-built wheels
uv cache prune --ci
```

**When to use:**
- Disk space optimization
- CI pipelines (use `--ci` flag)
- After resolving dependency conflicts

**Difference from `clean`:**
- `clean`: Removes everything (or specific package)
- `prune`: Removes only unused entries
- `prune --ci`: Keeps wheels built from source

## Cache Refresh Options

### --refresh

Force revalidation of all cached data:

```bash
# Refresh all dependencies
uv sync --refresh

# Refresh during install
uv pip install --refresh <package>

# Refresh tool installation
uv tool install --refresh <package>
```

**When to use:**
- After package update on PyPI
- Suspected outdated cached metadata
- Testing with latest available versions

### --refresh-package

Target specific package for revalidation:

```bash
# Refresh only numpy
uv sync --refresh-package numpy

# Refresh multiple packages
uv sync --refresh-package numpy --refresh-package pandas
```

**When to use:**
- Know specific package is outdated
- Avoid full cache revalidation overhead
- Testing specific package update

### --reinstall

Ignore existing installed versions:

```bash
# Reinstall everything
uv sync --reinstall

# Reinstall specific package
uv pip install --reinstall <package>
```

**When to use:**
- Installation corrupted
- Different version needed
- Testing clean installation

**Difference from `--refresh`:**
- `--refresh`: Revalidates cache, may reuse if valid
- `--reinstall`: Forces fresh installation regardless

## Build Isolation Control

### --no-build-isolation-package

Disable build isolation for specific packages:

```bash
# Disable isolation for one package
uv pip install --no-build-isolation-package chumpy chumpy

# Disable for multiple packages
uv pip install --no-build-isolation-package pkg1 --no-build-isolation-package pkg2 pkg1 pkg2
```

**When to use:**
- Package build script needs system dependencies
- Import errors during build
- Build backend requires pre-installed modules

**Prerequisite:** Install build dependencies first:
```bash
uv pip install pip setuptools wheel
uv pip install --no-build-isolation-package <package> <package>
```

### --no-build-isolation

Disable build isolation globally:

```bash
uv pip install --no-build-isolation <package>
```

**When to use:**
- Multiple packages need system access
- Testing build with system packages
- Legacy packages with non-standard builds

## Installation Options

### --force

Force reinstallation (for `uv tool`):

```bash
# Force tool reinstall
uv tool install --force <package>

# Force tool reinstall with editable mode
uv tool install --force --editable .
```

**When to use:**
- Tool already installed, need to update
- Switching between editable/production modes
- After source code changes (non-editable mode)

### --editable

Install in editable mode:

```bash
# Install current directory as editable
uv tool install --editable .

# Install specific package as editable
uv pip install --editable /path/to/package
```

**When to use:**
- Active development
- Changes need to reflect immediately
- No reinstall after code modifications

### --reinstall-package

Reinstall specific package:

```bash
# Reinstall numpy only
uv sync --reinstall-package numpy

# Reinstall multiple packages
uv sync --reinstall-package numpy --reinstall-package pandas
```

**When to use:**
- Specific package corrupted
- Version conflict resolution
- After dependency update

## Build Configuration

### --build-constraint

Constrain build dependencies:

```bash
# Set build constraints via config
# In pyproject.toml:
[tool.uv]
build-constraint-dependencies = ["setuptools<70"]

# Or via environment
UV_BUILD_CONSTRAINT_DEPENDENCIES="setuptools<70" uv pip install <package>
```

**When to use:**
- Outdated build dependencies causing failures
- Known incompatible build dependency versions
- Reproducible build environments

### --constraint

Apply version constraints during resolution:

```bash
# Via file
uv pip install -c constraints.txt <package>

# Via config
# In pyproject.toml:
[tool.uv]
constraint-dependencies = ["numpy<2.0"]
```

**When to use:**
- Enforcing maximum versions
- Preventing incompatible upgrades
- Corporate policy requirements

## Diagnostic Commands

### uv pip show

Display package information:

```bash
# Show installed package details
uv pip show <package>

# Output includes: version, location, dependencies
```

**When to use:**
- Verify installation location
- Check installed version
- Inspect dependencies

### uv pip list

List installed packages:

```bash
# List all packages
uv pip list

# JSON output
uv pip list --format json
```

**When to use:**
- Audit installed packages
- Check for duplicates
- Compare environments

### uv pip tree

Show dependency tree:

```bash
# Full dependency tree
uv pip tree

# Reverse tree (who depends on this package)
uv pip tree --reverse <package>
```

**When to use:**
- Understand dependency relationships
- Find dependency conflicts
- Trace transitive dependencies

## Environment Management

### uv venv

Create virtual environment:

```bash
# Create with system Python
uv venv

# Create with specific Python version
uv venv -p 3.13

# Create with seed packages (pip, setuptools, wheel)
uv venv --seed
```

**When to use:**
- Isolate project dependencies
- Test different Python versions
- Reproduce CI environment

### uv sync

Synchronize environment with lock file:

```bash
# Basic sync
uv sync

# Include all extras
uv sync --all-extras

# Development dependencies only
uv sync --dev-only
```

**When to use:**
- After updating pyproject.toml
- Setting up development environment
- Syncing team dependencies

## Tool Management

### uv tool install

Install command-line tools:

```bash
# Basic install
uv tool install <package>

# With extras
uv tool install "package[extra1,extra2]"

# Specific version
uv tool install package==1.0.0
```

### uv tool uninstall

Remove installed tools:

```bash
# Uninstall tool
uv tool uninstall <package>
```

**When to use:**
- Before switching installation modes
- Cleaning up old versions
- Resolving tool conflicts

### uv tool list

List installed tools:

```bash
# Show all tools
uv tool list

# Include package versions
uv tool list --verbose
```

## Run Commands

### uv run

Execute command in project environment:

```bash
# Run Python script
uv run python script.py

# Run package entry point
uv run <command>

# Run with specific Python
uv run -p 3.13 <command>
```

**When to use:**
- Development without global install
- Testing before installation
- Avoiding installation cache issues

## Debug Flags

### --verbose

Enable verbose logging:

```bash
# Show detailed operations
uv pip install --verbose <package>

# Abbreviated form
uv pip install -v <package>
```

**When to use:**
- Diagnosing installation issues
- Understanding resolution decisions
- Reporting bugs

### --debug

Enable debug logging:

```bash
# Maximum verbosity
uv pip install --debug <package>
```

**When to use:**
- Deep troubleshooting
- Network issues
- Cache problems

### --no-cache

Disable cache for operation:

```bash
# Install without using cache
uv pip install --no-cache <package>
```

**When to use:**
- Verifying cache isn't the problem
- Testing clean installation
- CI reproducibility checks

## Cache Location Control

### --cache-dir

Specify cache directory:

```bash
# Use custom cache location
uv pip install --cache-dir /tmp/uv-cache <package>

# Via environment variable
UV_CACHE_DIR=/tmp/uv-cache uv pip install <package>
```

**When to use:**
- CI with custom cache storage
- Testing cache behavior
- Shared team cache

## Common Troubleshooting Workflows

### Workflow 1: Resolve Build Failure

```bash
# 1. Identify if UV-specific
uv venv -p 3.13 --seed
source .venv/bin/activate
pip install --use-pep517 --no-cache --force-reinstall 'package==version'

# 2. If pip fails too, install build dependencies
apt install build-essential  # Ubuntu/Debian
# or
brew install gcc  # macOS

# 3. Try again with UV
uv pip install <package>

# 4. If still fails, disable build isolation
uv pip install pip setuptools
uv pip install --no-build-isolation-package <package> <package>
```

### Workflow 2: Fix Stale Cache

```bash
# 1. Clean cache for specific package
uv cache clean <package>

# 2. Force refresh
uv pip install --refresh <package>

# 3. If still issues, clean all cache
uv cache clean

# 4. Reinstall
uv pip install --reinstall <package>
```

### Workflow 3: Debug Tool Installation

```bash
# 1. Uninstall old version
uv tool uninstall <package>

# 2. Clean build artifacts in source
cd /path/to/source
rm -rf build/ dist/ *.egg-info

# 3. Fresh install
uv tool install --force .

# 4. Verify installation
which <command>
<command> --version
```

### Workflow 4: Test Production Build

```bash
# 1. Create clean environment
uv venv test-env
source test-env/bin/activate  # or `test-env\Scripts\activate` on Windows

# 2. Install with no cache
uv pip install --no-cache --reinstall <package>

# 3. Test functionality
python -c "import <package>; print(<package>.__version__)"

# 4. Deactivate and cleanup
deactivate
rm -rf test-env
```

## Official Documentation Links

- **Cache Concepts:** https://docs.astral.sh/uv/concepts/cache/
- **Build Failures:** https://docs.astral.sh/uv/reference/troubleshooting/build-failures/
- **CLI Reference:** https://docs.astral.sh/uv/reference/cli/
- **Settings:** https://docs.astral.sh/uv/reference/settings/

## Exit Codes

```
0   - Success
1   - General error
2   - Command usage error
101 - Package not found
102 - Version conflict
```

## Environment Variables

```bash
UV_CACHE_DIR=/path/to/cache           # Cache location
UV_NO_CACHE=1                         # Disable cache
UV_PYTHON=3.13                        # Default Python version
UV_INDEX_URL=https://pypi.org/simple  # Package index
UV_EXTRA_INDEX_URL=https://...        # Additional index
UV_NO_BUILD_ISOLATION=1               # Global build isolation disable
UV_BUILD_CONSTRAINT_DEPENDENCIES      # Build dependency constraints
```

## Configuration File Priority

1. Command-line flags (highest priority)
2. Environment variables
3. `pyproject.toml` (`[tool.uv]` section)
4. `uv.toml` in project directory
5. Global config (`~/.config/uv/uv.toml`)
6. System defaults (lowest priority)

## Common Flag Combinations

**Fresh install, no cache:**
```bash
uv pip install --no-cache --reinstall <package>
```

**Debug with verbose output:**
```bash
uv pip install --verbose --debug <package>
```

**Force rebuild from source:**
```bash
uv pip install --no-binary :all: --reinstall <package>
```

**Install with custom constraints:**
```bash
uv pip install -c constraints.txt --refresh <package>
```

**Tool install with clean build:**
```bash
cd /path/to/source
rm -rf build/ dist/ *.egg-info
uv tool install --force .
```
