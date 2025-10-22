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

## Critical Rules

- **Always** `page.wait_for_load_state('networkidle')` before DOM inspection
- Use descriptive selectors: `text=`, `role=`, CSS, IDs
- Close browser when done
- See `examples/` for more patterns