---
description: Update the HTML output style snippet (HTML.md) with new formatting instructions
---

# Update HTML Output Style

## Arguments

Input: `$ARGUMENTS`

## Instructions

1. **Parse arguments**:
   - Extract the update description or changes from `$ARGUMENTS`
   - If `-f` or `--force` flag is present, skip confirmation
   - If no arguments provided, ask user what changes they want to make

2. **Locate snippet file**:
   - Path: `~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts/snippets/HTML.md`
   - This is the ONLY file you should modify for HTML output styling
   - DO NOT modify `/Users/wz/.claude/output-styles/html.md` (deprecated location)

3. **Review current content** (UNLESS `-f` or `--force`):
   - Read the current HTML.md snippet
   - Show user a summary of what will change
   - Ask: "Proceed with these changes to HTML.md snippet? (yes/no)"
   - If no, abort
   - If yes, proceed

4. **Make the changes**:
   - Apply the requested updates to `scripts/snippets/HTML.md`
   - Common update patterns:
     - CSS style changes (colors, layouts, spacing)
     - New HTML components or patterns
     - JavaScript functionality updates
     - Dark mode theme adjustments
     - Mermaid diagram configuration

5. **Verify update**:
   - Ensure the `VERIFICATION_HASH` is updated to track changes
   - Confirm the YAML frontmatter is intact:
     ```yaml
     ---
     SNIPPET_NAME: HTML
     ANNOUNCE_USAGE: true
     ---
     ```

6. **Inform user**:
   - Confirm: "✅ Updated HTML.md snippet at scripts/snippets/HTML.md"
   - Note: "Changes will apply to all future HTML outputs that reference this snippet"
   - Remind: "The snippet is injected automatically via hooks - no restart needed"

## Example Usage

```bash
# With description
/update-html-style Add better support for code block newlines in <pre> tags

# With force flag (skip confirmation)
/update-html-style --force Update dark mode colors for better contrast

# Interactive mode
/update-html-style
```

## Important Notes

- **Single Source of Truth**: `HTML.md` snippet is the ONLY place to define HTML output styling
- **No output-styles directory**: Do not modify files in `/Users/wz/.claude/output-styles/` - that's deprecated
- **Automatic injection**: The snippet is injected via hooks, so changes apply immediately
- **Version tracking**: Update `VERIFICATION_HASH` to track significant changes
- **Backup recommended**: Consider backing up before major changes (use `--force` to skip)

## Common Update Scenarios

### Scenario 1: Fix code block formatting
```
/update-html-style Ensure <pre> tags use white-space: pre-wrap for proper newlines
```

### Scenario 2: Add new CSS component
```
/update-html-style Add .info-box CSS class for informational callouts
```

### Scenario 3: Update dark mode colors
```
/update-html-style --force Adjust dark mode --chinese-red to #DC143C for better visibility
```

### Scenario 4: Add JavaScript functionality
```
/update-html-style Add scroll-to-top button functionality to JavaScript section
```

## Technical Details

**File Structure:**
- Location: `scripts/snippets/HTML.md`
- Format: Markdown with YAML frontmatter
- Injection: Via `UserPromptSubmit` hook when HTML output is needed
- Scope: Applies to all HTML documentation, analysis, and plan outputs

**Best Practices:**
1. Test changes with sample HTML output before committing
2. Update `VERIFICATION_HASH` after significant changes
3. Document rationale for major styling decisions
4. Keep CSS compact and performance-optimized
5. Ensure dark mode compatibility for all new styles
6. Follow existing naming conventions (.chinese-red, .jade-green, etc.)

## Troubleshooting

**Issue**: Changes not applying
- **Cause**: Snippet might be cached
- **Fix**: Restart Claude Code session or clear cache

**Issue**: Syntax error after update
- **Cause**: Malformed CSS or JavaScript
- **Fix**: Validate CSS/JS syntax before saving

**Issue**: Dark mode broken
- **Cause**: Missing `[data-theme="dark"]` overrides
- **Fix**: Add corresponding dark mode styles for new components
