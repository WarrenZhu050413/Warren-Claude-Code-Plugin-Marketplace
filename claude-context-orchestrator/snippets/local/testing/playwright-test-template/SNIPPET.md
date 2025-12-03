---
name: Playwright Test Template
description: Copy-paste template for new Playwright E2E tests with all best practices (headless mode, tracing, proper selectors, form patterns)
keywords: [playwright, test, e2e, template, testing]
---

# Playwright Test Template

Copy-paste starting point for new Playwright tests with battle-tested patterns.

## Usage

```bash
# Copy template to new test file
cp template.py test_my_workflow.py

# Run test (headless by default)
python test_my_workflow.py

# Run with visible browser
HEADED=1 python test_my_workflow.py

# Debug with trace viewer
playwright show-trace /tmp/trace_my_workflow_FAILED.zip
```

## Template

```python
"""Test [workflow name]."""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect


def test_workflow():
    """Test [description of what this workflow does]."""

    print("\n" + "="*80)
    print("TEST: [Workflow Name]")
    print("="*80)

    # Use headless by default, override with HEADED=1
    headless = os.getenv('HEADED') != '1'
    slow_mo = 0 if headless else 300  # Slow down in headed mode for visibility

    print(f"  🖥️  Mode: {'Headless' if headless else 'Headed'}")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chromium', headless=headless, slow_mo=slow_mo)
        context = browser.new_context()

        # Enable tracing for debugging
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = context.new_page()

        # Capture console logs
        logs = []
        page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

        try:
            # Navigate to app
            print("\n[1/N] Loading app...")
            page.goto('http://localhost:3000')
            page.wait_for_load_state('networkidle')

            # PATTERN: Fill form → Wait enabled → Click
            print("\n[2/N] Filling form...")

            # Step 1: Fill inputs first (buttons are usually disabled until forms validate)
            input_field = page.locator('input[placeholder="Enter name"]')
            expect(input_field).to_be_visible(timeout=5000)
            input_field.fill("test value")

            textarea_field = page.locator('textarea[placeholder="Description"]')
            expect(textarea_field).to_be_visible(timeout=5000)
            textarea_field.fill("test description")

            # Step 2: Wait for button to be enabled, then click
            print("\n[3/N] Submitting form...")
            submit_btn = page.locator('button:has-text("Submit")')
            expect(submit_btn).to_be_visible(timeout=5000)
            expect(submit_btn).to_be_enabled(timeout=5000)  # Critical!
            submit_btn.click()

            # Step 3: Verify result (use regex for emoji-containing text)
            print("\n[4/N] Verifying result...")
            success_msg = page.locator('text=/Success/')
            expect(success_msg).to_be_visible(timeout=10000)

            # Take screenshot at key steps
            page.screenshot(path='/tmp/test_workflow_success.png')

            print("\n" + "="*80)
            print("✅ TEST PASSED: [Workflow Name]")
            print("="*80)

            # Save trace on success
            context.tracing.stop(path="/tmp/trace_workflow_SUCCESS.zip")
            print("  📊 Trace saved: /tmp/trace_workflow_SUCCESS.zip")
            print("     View with: playwright show-trace /tmp/trace_workflow_SUCCESS.zip")

            return True

        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            page.screenshot(path='/tmp/test_workflow_failed.png')

            # Print console logs for debugging
            print(f"\n  📋 Console Logs (last 20):")
            for log in logs[-20:]:
                print(f"     {log}")

            # Save trace on failure
            context.tracing.stop(path="/tmp/trace_workflow_FAILED.zip")
            print("  📊 Trace saved: /tmp/trace_workflow_FAILED.zip")

            return False

        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
            page.screenshot(path='/tmp/test_workflow_error.png')

            print(f"\n  📋 Console Logs (last 20):")
            for log in logs[-20:]:
                print(f"     {log}")

            context.tracing.stop(path="/tmp/trace_workflow_ERROR.zip")
            print("  📊 Trace saved: /tmp/trace_workflow_ERROR.zip")

            return False

        finally:
            print("\nClosing browser...")
            browser.close()


if __name__ == "__main__":
    success = test_workflow()
    exit(0 if success else 1)
```

## Key Patterns Included

### 1. Headless Mode with Trace Viewer
- Defaults to headless (no window disruption)
- Captures full trace for debugging
- Override with `HEADED=1` for development

### 2. Proper Form Flow
- Fill all inputs FIRST
- Wait for button to be enabled
- Then click button

### 3. Robust Selectors
- Use attribute selectors: `input[placeholder="..."]`
- Button-specific: `button:has-text("...")`
- Emoji-safe: `text=/regex/`

### 4. Triple Debugging
- Screenshots at key steps
- Trace recording for timeline/DOM
- Console log capture for errors

### 5. Comprehensive Error Handling
- Separate handling for assertions vs exceptions
- Console logs on failure
- Different trace files for success/failure/error

## Customization Checklist

- [ ] Replace `[Workflow Name]` with actual workflow name
- [ ] Update step count `[1/N]` based on actual steps
- [ ] Replace selectors with actual app selectors
- [ ] Adjust timeouts if needed (default 5s visible, 10s for slow operations)
- [ ] Update localhost port if not 3000
- [ ] Add additional verification steps as needed

## Tips

**Finding selectors:**
```python
# Run in headed mode to inspect
HEADED=1 python test.py

# Or use Playwright inspector
PWDEBUG=1 python test.py
```

**Common selector patterns:**
```python
# Text with emoji
page.locator('text=/Mission Control/')

# Button text
page.locator('button:has-text("Create")')

# Input by placeholder
page.locator('input[placeholder*="keyword"]')

# Nth element (when multiple match)
page.locator('button:has-text("Submit")').nth(0)
```

**Debugging:**
1. Check console logs first (fastest)
2. View screenshot for visual state
3. Open trace for step-by-step DOM inspection
