---
name: Testing Webapps
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

Write native Python Playwright scripts to test local webapps.

**Helper**: `scripts/with_server.py` manages server lifecycle. Run with `--help` first.

## Approach

**Static HTML**: Read file → identify selectors → write script

**Dynamic webapp**:
- Server not running: Use `with_server.py`
- Server running: Navigate → wait networkidle → inspect → act

## Server Management

```bash
# Single server
python scripts/with_server.py --server "npm run dev" --port 5173 -- python automation.py

# Multiple servers
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python automation.py
```

## Script Patterns

**Automation**:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle') # CRITICAL for dynamic apps
    # automation logic here
    browser.close()
```

**Reconnaissance**:
```python
page.screenshot(path='/tmp/inspect.png', full_page=True)
page.content() # Get HTML
page.locator('button').all() # Find elements
```

## Headless Mode + Trace Viewer (Recommended for macOS)

**Problem**: Headed mode steals window focus on macOS, disrupting workflow.

**Solution**: Run headless with trace recording:

```python
import os
headless = os.getenv('HEADED') != '1'  # Default headless, override with HEADED=1

browser = p.chromium.launch(headless=headless)
context = browser.new_context()
context.tracing.start(screenshots=True, snapshots=True, sources=True)
page = context.new_page()

# ... test code ...

# Save trace on completion
context.tracing.stop(path="/tmp/trace_testname_SUCCESS.zip")
```

**Debug traces**:
```bash
playwright show-trace /tmp/trace_testname_SUCCESS.zip
```

**Why better than headed**: Step through at your own pace, inspect DOM at any point, see network requests, no window disruption.

## Selector Best Practices

**Emoji-safe text matching**:
```python
# ❌ Fails with emoji
page.locator('text="Mission Control"')

# ✅ Works with "Mission Control 🚀"
page.locator('text=/Mission Control/')
```

**Button-specific selectors**:
```python
# ❌ Too generic, matches any text
page.locator('text="Create World"')

# ✅ Specific to buttons
page.locator('button:has-text("Create World")')
```

**Form field specificity**:
```python
# ❌ Fragile, matches wrong element
page.locator('textarea').first

# ✅ Specific placeholder
page.locator('textarea[placeholder*="description"]')
page.locator('input[type="text"]').nth(2)  # If index matters
```

**Wait for both visible AND enabled**:
```python
button = page.locator('button:has-text("Submit")')
expect(button).to_be_visible(timeout=5000)
expect(button).to_be_enabled(timeout=5000)  # Critical for form buttons!
button.click()
```

## Form Testing Pattern

**Rule**: Fill → Wait for enabled → Click

**Wrong order (causes timeouts)**:
```python
# ❌ Button is disabled, causes "element not enabled" timeout
button.click()
textarea.fill("content")
```

**Correct order**:
```python
# ✅ Button becomes enabled after fill
textarea = page.locator('textarea[placeholder="description"]')
expect(textarea).to_be_visible(timeout=5000)
textarea.fill("content")

button = page.locator('button:has-text("Submit")')
expect(button).to_be_enabled(timeout=5000)  # Now enabled
button.click()
```

**Why**: Most forms disable submit buttons until validation passes. Always fill first.

## Test Setup: Database State

**Pattern for clean test runs**:
```bash
# Reset database before tests
rm -f backend/database.db
cd backend && python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"
```

**In test runner**:
```python
from pathlib import Path
import subprocess

def setup_clean_database():
    """Reset database to clean state."""
    db_path = Path("backend/database.db")
    if db_path.exists():
        db_path.unlink()
    subprocess.run([
        "python", "-c",
        "from src.database import init_db; import asyncio; asyncio.run(init_db())"
    ], cwd="backend")
```

**Why**: Prevents UUID conflicts, UNIQUE constraint violations, and flaky tests from stale data.

## Debugging Triad: Screenshot + Trace + Console

**Always capture all three**:

```python
# Setup
context.tracing.start(screenshots=True, snapshots=True, sources=True)
logs = []
page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

# During test - take screenshots at key steps
page.screenshot(path='/tmp/test_step1.png')

# On failure
context.tracing.stop(path="/tmp/trace_FAILED.zip")
print(f"Console logs (last 20):")
for log in logs[-20:]:
    print(f"  {log}")
```

**Why each matters**:
- **Screenshots**: Visual state at failure point
- **Trace**: Full interaction timeline, DOM snapshots, network activity
- **Console**: React errors, API failures, JavaScript warnings

**Debugging workflow**:
1. Check console logs for errors first (fastest)
2. View screenshot to understand visual state
3. Open trace with `playwright show-trace` to step through and inspect DOM

## Troubleshooting

### "Fix doesn't work" - Tests still fail after code change

**Symptom**: Fixed a bug but tests still fail with same error.

**Causes & Solutions**:
1. **Frontend hot reload hasn't applied changes**
   - Verify file: `grep "new code" file.jsx`
   - Check dev server console for reload confirmation
   - Hard restart: Kill dev server, `npm run dev`

2. **Browser cache**
   - Use `page.goto(..., wait_until='networkidle')`
   - Or clear: `context.clear_cookies()`

### Generic selectors match wrong elements

**Symptom**: `textarea.first` or `button.last` fails unexpectedly or matches wrong element.

**Cause**: DOM structure changed or multiple matching elements exist.

**Solution**: Use attribute selectors:
```python
# ❌ Fragile - depends on DOM order
page.locator('textarea').first

# ✅ Robust - matches specific element
page.locator('textarea[placeholder="World description"]')
page.locator('button:has-text("Create")').first  # If multiple, be specific
```

### "Element not enabled" timeouts

**Symptom**: `page.click()` times out with "element is not enabled".

**Cause**: Trying to click button before form validation passes.

**Solution**: Fill form first, then wait for enabled:
```python
# Fill all required fields first
input1.fill("value1")
input2.fill("value2")

# Then wait for button to enable
button = page.locator('button:has-text("Submit")')
expect(button).to_be_enabled(timeout=5000)
button.click()
```

## Critical Rules

- **Always** `page.wait_for_load_state('networkidle')` before DOM inspection
- **Default to headless** with trace recording for debugging without window disruption
- **Fill forms before clicking** submit buttons (they're usually disabled)
- **Use specific selectors** with attributes, not generic `.first`/`.last`
- **Capture triad**: screenshots + trace + console logs for debugging
- Close browser when done
- See `examples/` for more patterns