# Mypy Setup Guide for gmaillm

**Status**: Configuration created, ready to add to project
**Created**: 2025-10-29

---

## Overview

This guide explains how to add static type checking with mypy to the gmaillm project. A `mypy.ini` configuration file has been created with appropriate settings.

---

## Benefits of Adding Mypy

### 1. Complements Runtime Validation

gmaillm already has runtime type validation (`validators/runtime.py`), and mypy adds **compile-time** type checking:

| Feature | Runtime Validation | Static Type Checking (mypy) |
|---------|-------------------|----------------------------|
| **When** | Function call time | Before code runs |
| **Catches** | Wrong model types | Type mismatches, missing attributes |
| **Cost** | Runtime overhead | Zero runtime cost |
| **Coverage** | Decorated functions only | Entire codebase |

**Together**: Defense-in-depth type safety!

### 2. IDE Integration

With mypy:
- Real-time type error highlights in VS Code/PyCharm
- Better autocomplete and IntelliSense
- Refactoring becomes safer

### 3. Documentation

Type hints serve as inline documentation:

```python
# Before (unclear)
def process_email(email, formatter):
    ...

# After (self-documenting)
def process_email(email: EmailFull, formatter: RichFormatter) -> str:
    ...
```

---

## Installation

### Step 1: Add mypy to Dev Dependencies

```bash
# Add mypy and Pydantic plugin
uv add --dev mypy

# Install types for third-party libraries
uv add --dev types-PyYAML
```

**Note**: The `mypy.ini` file is already configured and ready to use.

### Step 2: Verify Installation

```bash
uv run mypy --version
# Should output: mypy 1.x.x
```

### Step 3: Run Initial Check

```bash
uv run mypy gmaillm/
```

**Expected Output**: Many errors initially (this is normal for adding mypy to existing code).

---

## Configuration Explanation

The included `mypy.ini` uses a **gradual adoption** strategy:

### Lenient Settings (Starting Point)

```ini
disallow_untyped_defs = False  # Allow functions without type hints
disallow_any_generics = False   # Allow List instead of List[str]
ignore_missing_imports = True   # Don't error on libraries without stubs
```

**Why**: Allows gradual adoption without blocking development.

### Pydantic Plugin

```ini
plugins = pydantic.mypy

[pydantic-mypy]
init_forbid_extra = True        # Catch unknown fields
init_typed = True               # Type-check __init__
warn_untyped_fields = True      # Warn about fields without types
```

**Why**: Ensures Pydantic models are properly typed.

### Per-Module Settings

```ini
[mypy-tests.*]
disallow_untyped_defs = False  # Lenient for test code

[mypy-googleapiclient.*]
ignore_missing_imports = True  # Google libraries lack stubs
```

**Why**: Different standards for different code sections.

---

## Gradual Adoption Strategy

### Phase 1: Baseline (Week 1)

**Goal**: Get mypy running without errors

```bash
# Run mypy to see current state
uv run mypy gmaillm/ > mypy_baseline.txt

# Review errors, categorize by severity
```

**Common Issues**:
- Missing return type annotations
- Implicit `Any` types
- Third-party library stubs missing

**Fix**: Add type stubs for third-party libraries, add `# type: ignore` comments for known issues.

### Phase 2: New Code (Week 2-3)

**Goal**: All new code must pass mypy

```bash
# Add to Makefile
mypy:
    uv run mypy gmaillm/

# Add to CI/CD pipeline (fail on errors in new files)
```

**Workflow**:
1. Write new code with type hints
2. Run `make mypy` before committing
3. Fix any type errors

### Phase 3: Incremental Strictness (Month 2)

**Goal**: Enable stricter checks one at a time

```ini
# In mypy.ini, enable gradually:
check_untyped_defs = True       # Week 4
disallow_incomplete_defs = True # Week 6
disallow_untyped_calls = True   # Week 8
```

**Process**:
1. Enable one strict setting
2. Fix resulting errors module-by-module
3. Commit fixes
4. Repeat

### Phase 4: Full Strict Mode (Month 3+)

**Goal**: Enable full strict mode

```ini
[mypy]
strict = True
```

**Result**: Maximum type safety, zero type-related bugs.

---

## Adding Mypy to Makefile

Add these targets to `Makefile`:

```makefile
.PHONY: typecheck mypy-baseline mypy-strict

# Run mypy type checking
typecheck:
    @echo "🔍 Running mypy..."
    uv run mypy gmaillm/

# Generate baseline of current errors
mypy-baseline:
    @echo "📊 Generating mypy baseline..."
    uv run mypy gmaillm/ > mypy_baseline.txt
    @echo "Baseline saved to mypy_baseline.txt"

# Run mypy in strict mode (for testing)
mypy-strict:
    @echo "🔒 Running mypy in strict mode..."
    uv run mypy --strict gmaillm/
```

Usage:

```bash
make typecheck      # Regular check
make mypy-baseline  # Save current state
make mypy-strict    # Preview strict mode
```

---

## Common Type Errors and Fixes

### 1. Missing Return Type

**Error**:
```
error: Function is missing a return type annotation
```

**Fix**:
```python
# Before
def process_email(email):
    return email.subject

# After
def process_email(email: EmailFull) -> str:
    return email.subject
```

### 2. Implicit `Any`

**Error**:
```
error: Function is missing a type annotation for one or more arguments
```

**Fix**:
```python
# Before
def format_date(date):
    return date.strftime("%Y-%m-%d")

# After
from datetime import datetime

def format_date(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")
```

### 3. Union Types

**Error**:
```
error: Incompatible return value type (got "str | None", expected "str")
```

**Fix**:
```python
from typing import Optional

# Before
def get_body(email):
    return email.body_plain or email.body_html

# After
def get_body(email: EmailFull) -> Optional[str]:
    return email.body_plain or email.body_html
```

### 4. List Types

**Error**:
```
error: Need type annotation for "emails" (hint: "emails: List[<type>] = ...")
```

**Fix**:
```python
from typing import List

# Before
def count_unread(emails):
    return len([e for e in emails if e.is_unread])

# After
def count_unread(emails: List[EmailSummary]) -> int:
    return len([e for e in emails if e.is_unread])
```

---

## Integration with CI/CD

### GitHub Actions Example

Add to `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install uv
        uses: astral-sh/setup-uv@v1
      - name: Install dependencies
        run: uv sync --all-extras
      - name: Run mypy
        run: uv run mypy gmaillm/
      - name: Run tests
        run: uv run pytest
```

**Result**: Type errors block merging.

---

## VS Code Integration

### Setup

1. Install Python extension
2. Add to `.vscode/settings.json`:

```json
{
  "python.linting.mypyEnabled": true,
  "python.linting.enabled": true,
  "python.linting.mypyArgs": [
    "--config-file=mypy.ini"
  ],
  "python.analysis.typeCheckingMode": "basic"
}
```

3. Reload VS Code

**Result**: Type errors show as red squiggles inline.

---

## PyCharm Integration

### Setup

1. Open Settings → Tools → Python Integrated Tools
2. Set "Type checker" to "mypy"
3. Point to `mypy.ini` configuration

**Result**: Type errors show in editor gutter.

---

## Frequently Asked Questions

### Q: Should I add type hints to all code immediately?

**A**: No! Use gradual adoption:
1. Start with new code only
2. Add hints to modified code during refactoring
3. Slowly backfill existing code

### Q: What about `# type: ignore` comments?

**A**: Use sparingly for:
- Third-party libraries without stubs
- Complex dynamic code
- Temporary workarounds

**Always add reason**:
```python
result = complex_dynamic_function()  # type: ignore[attr-defined]  # Library bug #123
```

### Q: Do type hints affect runtime performance?

**A**: No! Type hints are **annotations only**:
- Not evaluated at runtime (unless you use `@validate_types`)
- Zero performance cost
- Can be optimized away by Python

### Q: What's the difference between mypy and runtime validators?

**A**: They're complementary:

```python
# mypy catches this BEFORE running:
def format_email(email: EmailFull) -> str:
    return email.subject

format_email(EmailSummary(...))  # mypy error: Expected EmailFull

# Runtime validator catches this DURING running:
@validate_pydantic(EmailFull)
def format_email(email):
    return email.subject

format_email(EmailSummary(...))  # TypeError: expected EmailFull, got EmailSummary
```

**Use both** for defense-in-depth!

---

## Next Steps

### Immediate (This Week)

1. ✅ **Configuration created** (`mypy.ini`)
2. ⏳ **Add mypy to dev dependencies**
   ```bash
   uv add --dev mypy types-PyYAML
   ```
3. ⏳ **Run baseline check**
   ```bash
   uv run mypy gmaillm/ > mypy_baseline.txt
   ```
4. ⏳ **Review baseline**, categorize errors

### Short-term (Next 2 Weeks)

1. Add `typecheck` target to Makefile
2. Fix critical type errors (if any)
3. Require mypy passing for new code
4. Document common patterns in this guide

### Long-term (Next 2 Months)

1. Enable `check_untyped_defs = True`
2. Gradually add type hints to existing code
3. Enable stricter checks incrementally
4. Add mypy to CI/CD pipeline

---

## Resources

- [Mypy Documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [Pydantic Mypy Plugin](https://docs.pydantic.dev/latest/integrations/mypy/)
- [Typing Best Practices](https://typing.readthedocs.io/en/latest/source/best_practices.html)

---

## Summary

**Status**: ✅ Ready to add mypy to project

**Benefits**:
- Catches type errors before code runs
- Complements runtime validation
- Better IDE support
- Self-documenting code

**Recommendation**:
Add mypy to dev dependencies and follow the gradual adoption strategy. Start with new code only, then backfill existing code over time.

**Configuration**: `mypy.ini` is already optimized for gradual adoption with Pydantic support.

---

**Last Updated**: 2025-10-29
**Status**: Configuration ready, awaiting addition to project
