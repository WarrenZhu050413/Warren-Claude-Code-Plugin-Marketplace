# Evaluation: Python Package Build Cache Issues

## Metadata

```json
{
  "date": "2025-10-28",
  "session_name": "main",
  "context": "Python package build cache causing stale installations",
  "reproducible_prompt": "Help me understand why 'make install' doesn't show my latest code changes but 'uv run gmail' does",
  "skills_invoked": []
}
```

## Summary

User encountered issue where `make install` didn't show latest code changes (workflows command missing) while `uv run gmail` worked correctly. Root cause was Python's build system caching a wheel snapshot during non-editable installs, which doesn't automatically include files added after the cache was created.

## Problem Description

**Symptoms:**
- Globally installed command (`gmail`) missing new workflows subcommand
- Local execution (`uv run gmail`) showed the workflows command correctly
- User had recently added `gmaillm/commands/workflows.py`

**Initial Hypothesis:**
Stale build artifacts in `build/`, `dist/`, or `*.egg-info` directories

**Actual Root Cause:**
1. Previous installation had been in editable mode (`--editable`)
2. At some point switched to non-editable install
3. Non-editable install builds a wheel package (snapshot) that caches source code state
4. New files added after wheel creation don't appear in the package
5. Global install uses cached wheel in `~/.local/share/uv/tools/`
6. `uv run gmail` bypasses global install and uses local source directly

## Solution Implemented

Updated Makefile to include `clean` dependency for `install` target:

```makefile
install: clean
	@echo "📦 Installing gmaillm globally..."
	@echo "   Cleaning stale build artifacts first..."
	$(UV) tool install --force .
	@echo "✅ Installed globally!"
	@echo ""
	@echo "⚠️  Note: After code changes, run 'make install' again to rebuild."
	@echo "   Or use 'make dev' + 'uv run gmail' for instant changes."
```

This ensures:
1. Build artifacts (`build/`, `dist/`, `*.egg-info`) are removed before each install
2. Fresh wheel is built from current source code
3. All new files are included in the package
4. No stale cache issues

## Key Learnings

### 1. Python Installation Modes

**Three modes with different behaviors:**

| Mode | Command | Updates Automatically? | Use Case |
|------|---------|----------------------|----------|
| Editable | `uv tool install --editable .` | Yes (symlinks to source) | Active development |
| Production | `uv tool install .` | No (cached wheel) | Stable releases |
| Local Env | `uv sync` + `uv run` | Yes (uses source) | Development (recommended) |

### 2. Why `uv run` Worked but Global Install Didn't

- `uv run <command>` executes from local environment created by `uv sync`
- Local environment uses source code directly (similar to editable mode)
- Global install (`uv tool install`) creates isolated environment with cached wheel
- These are completely separate: `~/.local/share/uv/tools/` vs project directory

### 3. Build Artifact Lifecycle

**Artifacts created during `pip install .` or `uv tool install .`:**
```
build/          → Temporary build files
dist/           → Built wheel (.whl) and source distribution (.tar.gz)
*.egg-info/     → Package metadata (list of files, dependencies, entry points)
```

**Why they cause stale installs:**
- Wheel contains snapshot of source code at build time
- `*.egg-info` lists files that existed when metadata was generated
- New files added after these are created won't be included
- Even `--force` flag reuses cached artifacts if not cleaned

### 4. Makefile Pattern for Reliability

**Dependency chain ensures correct order:**
```makefile
install: clean   # MUST clean before install
	uv tool install --force .

clean:
	rm -rf build/ dist/ *.egg-info
```

This is more reliable than:
```makefile
# BAD: User might forget to clean
install:
	uv tool install --force .
```

## Alternative Solutions Considered

1. **Keep editable mode** - User rejected, wanted production build behavior
2. **Manual clean before install** - Error-prone, easy to forget
3. **Auto-reinstall on file changes** - Too complex, requires file watching
4. **Hybrid approach** (install-dev + install targets) - User rejected, wanted simplicity

**Final choice:** Clean dependency (simplest, most reliable)

## Files Modified

1. `Makefile` - Updated `install` target to use `clean` dependency and removed `--editable` flag
2. `gmail-integration-plugin/CLAUDE.md` - Added "Installation and Build Issues" section
3. Created `snippets/local/development/python-package-build-cache.md` - Comprehensive troubleshooting guide
4. Updated `CLAUDE.md` (main plugin guide) - Added "Understanding Installation Modes" section

## Documentation Created

### New Snippet: `python-package-build-cache.md`

**Coverage:**
- Symptoms of stale build cache
- Root cause explanation
- Three solution approaches (clean before install, editable mode, local env)
- Build artifacts reference
- Installation modes comparison table
- Debugging steps
- Common gotchas
- Real-world example

**Value:** Prevents future confusion about why code changes don't appear after install

### Project Guide Updates

**Added to gmail-integration-plugin/CLAUDE.md:**
- Stale Build Cache section (symptoms, cause, solution, alternatives)
- Installation modes comparison
- When to use each mode

**Added to main CLAUDE.md:**
- "Understanding Installation Modes" section before testing instructions
- Makefile pattern for preventing stale builds
- Links between installation approaches

## Impact

**Immediate:**
- `make install` now reliably shows latest code changes
- No more confusion about why global install differs from `uv run`

**Long-term:**
- Pattern documented for other Python CLI projects
- Troubleshooting guide available for similar issues
- Clear explanation prevents repeating same debugging process

## Patterns Worth Capturing

### Pattern: Makefile Dependency Chain for Clean Builds

```makefile
target: dependency1 dependency2
	commands

# Example
install: clean
	build commands
```

**Why it works:**
- Make guarantees dependencies run first
- No manual step to remember
- Atomic operation (clean + install)

### Pattern: Local Environment vs Global Install

**When debugging "code not updating" issues:**

1. Try `uv run <command>` - if it works, build cache is the problem
2. Check which command is running: `which <command>`
3. Clean build artifacts: `rm -rf build/ dist/ *.egg-info`
4. Reinstall: `uv tool install --force .`

### Pattern: Preventing Stale Builds in Python Packages

**Essential clean targets:**
```bash
rm -rf build/        # Temporary build files
rm -rf dist/         # Distribution archives
rm -rf *.egg-info    # Package metadata
```

**Optional but recommended:**
```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +
```

## Questions This Eval Answers

1. **Q:** Why doesn't my Python CLI show latest changes after `pip install .`?
   **A:** Non-editable installs cache a wheel snapshot. Clean build artifacts before reinstalling.

2. **Q:** What's the difference between `uv run` and globally installed command?
   **A:** `uv run` uses local source, global install uses cached wheel. Different locations.

3. **Q:** When should I use editable vs production install?
   **A:** Editable for active development, production for stable releases. Local env (`uv run`) recommended for development.

4. **Q:** How do I prevent stale build cache?
   **A:** Use `install: clean` dependency in Makefile to force fresh builds.

## Reproducible Test Case

```bash
# Setup
cd my-python-cli-project
uv sync

# Add new file
echo 'print("new feature")' > myproject/commands/newcmd.py

# Non-editable install (stale)
uv tool install --force .
myproject newcmd  # Command not found ❌

# But local works
uv run myproject newcmd  # Works! ✅

# Fix by cleaning first
rm -rf build/ dist/ *.egg-info
uv tool install --force .
myproject newcmd  # Now works! ✅
```

## Related Issues

- Python packaging gotcha that affects all CLI tools built with setuptools/pip
- Especially common when adding new entry points or modules
- `uv` uses same underlying build system (PEP 517/518) so inherits this behavior
- Not specific to `uv` - same issue with `pip`, `poetry`, `pipx`, etc.

## Tools and Commands Used

```bash
# Debugging
which gmail                    # Check which version is running
uv run gmail --help            # Test local version
gmail --help                   # Test global version

# Cleaning
rm -rf build/ dist/ *.egg-info

# Installation
uv tool install --force .      # Production (cached wheel)
uv tool install --editable .   # Development (symlinks)
uv sync && uv run gmail        # Local environment

# Makefile
make clean                     # Clean build artifacts
make install                   # Clean + install
make dev                       # Setup local environment
```

## Success Criteria Met

✅ Identified root cause (cached wheel snapshot)
✅ Implemented reliable solution (clean dependency)
✅ Documented for future reference
✅ Updated project guides
✅ Created reusable troubleshooting snippet
✅ Tested solution works

## Future Improvements

**Potential enhancements:**
1. Add `make verify` target that compares global vs local versions
2. Create pre-commit hook that warns about stale global install
3. Add CI check that tests production build (not just local)

**Related documentation:**
- Could expand snippet with examples for `poetry`, `pipx`, `hatch`
- Could add flowchart for "which installation mode should I use?"
- Could create skill for "debugging Python CLI tools"

---

**Evaluation Date:** 2025-10-28
**Session:** main
**Skills Invoked:** None (direct problem-solving)
**Pattern Captured:** Makefile clean dependency for reliable Python package builds
