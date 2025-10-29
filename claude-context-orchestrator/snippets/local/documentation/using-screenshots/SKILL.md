---
name: "Using Screenshots"
description: "This snippet should be used when reading, organizing, and naming screenshots with date prefixes."
---

# Screenshot Workflow

## Reading Screenshots

When you need to analyze screenshots or images provided by the user:

1. **Default Location**: Screenshots are typically saved to `~/Desktop`
2. **Read the screenshot**: Use the Read tool to view screenshots from the Desktop
   ```
   Read tool: ~/Desktop/Screenshot_*.png
   ```

## Organizing Screenshots After Reading

**CRITICAL**: After reading any screenshot, you MUST:

1. **Rename descriptively** based on the content
2. **Add date prefix** in format: `YYYY-MM-DD`
3. **Move to organized location**: `~/Desktop/claude_screenshots/`

## Naming Convention

```
YYYY-MM-DD-{descriptive-name}.{extension}
```

**Examples:**
- `2025-10-13-login-page-error.png`
- `2025-10-13-dashboard-layout.png`
- `2025-10-13-api-response-json.jpg`

## Organization Workflow

```bash
# After reading a screenshot from Desktop:
# 1. Determine descriptive name based on content
# 2. Create directory if needed
mkdir -p ~/Desktop/claude_screenshots

# 3. Move and rename with date prefix
mv ~/Desktop/Screenshot_2023-10-13_at_10.30.45.png \
   ~/Desktop/claude_screenshots/2025-10-13-user-profile-page.png
```

## Handling Filenames with Spaces

**CRITICAL**: macOS screenshot filenames contain spaces (e.g., `Screenshot 2025-10-13 at 11.07.11 PM.png`)

**Best practice - Use glob pattern with variable in loop:**

```bash
# ✅ CORRECT - Glob pattern handles spaces automatically
cd /Users/wz/Desktop && for f in Screenshot*11.07.11*.png; do
    mv "$f" claude_screenshots/2025-10-13-descriptive-name.png
done
```

**Why this works:**
- Shell expands glob pattern correctly without manual escaping
- Variable `$f` is quoted to preserve spaces
- Works reliably with all special characters

**Alternative methods (less reliable):**
```bash
# ⚠️  Escaping spaces - error-prone with multiple spaces
mv Screenshot\ 2025-10-13\ at\ 11.07.11\ PM.png destination.png

# ⚠️  Quotes - can fail with nested quotes or special chars
mv "Screenshot 2025-10-13 at 11.07.11 PM.png" destination.png
```

**Lesson learned:** When moving files with complex filenames (spaces, special chars), prefer glob patterns with loops over manual escaping.

## Extreme Special Characters

**Problem**: Read tool fails on complex filenames (parentheses, Spanish characters, multiple periods)

**Solution**: Move → Rename → Read

```bash
mkdir -p ~/Desktop/claude_screenshots
cd ~/Desktop
i=1
for f in "Captura de pantalla 2025-10-23 a la(s) 8.20"*.png; do
  [ -f "$f" ] && mv "$f" "claude_screenshots/2025-10-23-temp-$i.png" && i=$((i+1))
done
# Read from ~/Desktop/claude_screenshots/2025-10-23-temp-*.png
# Then rename descriptively after analysis
```

**Use when**: Glob finds files but Read fails, Spanish macOS, parentheses, multiple periods

## Playwright & Extension Screenshots

When taking screenshots with Playwright or other automation tools:

**ALWAYS save directly to the organized location:**

```javascript
// Playwright example
await page.screenshot({
  path: `~/Desktop/claude_screenshots/${date}-${descriptiveName}.png`
});
```

**Python example:**
```python
from datetime import datetime
date = datetime.now().strftime('%Y-%m-%d')
screenshot_path = f'~/Desktop/claude_screenshots/{date}-{descriptive_name}.png'
driver.save_screenshot(screenshot_path)
```

## Complete Workflow Summary

1. **User shares screenshot** → Usually in `~/Desktop`
2. **Claude reads it** → Use Read tool
3. **Claude analyzes** → Understand the content
4. **Claude organizes** → Move to `~/Desktop/claude_screenshots/YYYY-MM-DD-description.ext` (use glob pattern for files with spaces)
5. **Any new screenshots taken** → Save directly to `~/Desktop/claude_screenshots/` with date-description format

## Directory Structure

```
~/Desktop/
├── claude_screenshots/
│   ├── 2025-10-13-login-error.png
│   ├── 2025-10-13-api-response.png
│   ├── 2025-10-14-dashboard-view.png
│   └── 2025-10-14-test-failure.jpg
└── [other desktop files]
```

## Benefits

- **Easy to find**: Date prefix allows chronological sorting
- **Descriptive**: Know what the screenshot contains without opening
- **Organized**: All Claude-related screenshots in one place
- **Consistent**: Same format for manual and automated screenshots
