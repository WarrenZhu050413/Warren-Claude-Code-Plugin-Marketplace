---
description: Guidance for updating HTML output style snippet (HTML.md) with new formatting instructions
SNIPPET_NAME: updating-html-style
ANNOUNCE_USAGE: true
---

# Updating HTML Output Style

## Context

When updating the HTML.md snippet that controls HTML output styling and formatting.

## Core Instructions

### 1. Single Source of Truth

**Primary snippet location**: `${CLAUDE_PLUGIN_ROOT}/scripts/snippets/HTML.md`

This is the ONLY file to modify for HTML output styling. Do NOT modify:
- `/Users/wz/.claude/output-styles/html.md` (deprecated)
- Any other HTML-related files outside the plugin

### 2. File Structure Requirements

After any updates, ensure these elements remain intact:

**YAML Frontmatter:**
```yaml
---
SNIPPET_NAME: HTML
ANNOUNCE_USAGE: true
---
```

**Verification Hash**: Must be updated after changes to track modifications

### 3. Common Update Patterns

**CSS Style Changes:**
- Color schemes (light/dark mode)
- Layout and spacing adjustments
- Typography updates
- Component styling

**HTML Components:**
- New structural patterns
- Template additions
- Accessibility improvements

**JavaScript Functionality:**
- Interactive features
- Dynamic behavior
- Utility functions

**Dark Mode:**
- `[data-theme="dark"]` overrides
- Color contrast adjustments
- Theme-specific components

### 4. Update Workflow

1. **Read current content**: Review `${CLAUDE_PLUGIN_ROOT}/scripts/snippets/HTML.md`
2. **Show planned changes**: Summarize what will be modified
3. **Request confirmation**: Ask user "Proceed with these changes? (yes/no)" (UNLESS `-f` or `--force` flag)
4. **Apply changes**: Make the requested updates
5. **Update hash**: Modify `VERIFICATION_HASH` to track changes
6. **Verify integrity**: Confirm YAML frontmatter is intact
7. **Report completion**: Confirm update location and scope

### 5. Best Practices

**Before Updating:**
- Understand current styling system
- Consider impact on existing HTML outputs
- Check dark mode compatibility
- Validate CSS/JS syntax

**During Updates:**
- Keep CSS compact and performant
- Follow existing naming conventions (`.chinese-red`, `.jade-green`, etc.)
- Maintain backward compatibility when possible
- Document rationale for major changes

**After Updates:**
- Test with sample HTML output
- Verify dark mode still works
- Confirm no syntax errors
- Update verification hash

### 6. Automatic Application

**Injection mechanism**: Via `UserPromptSubmit` hook
**Scope**: Applies to all HTML documentation, analysis, and plan outputs
**No restart needed**: Changes apply immediately to new prompts

### 7. Common Scenarios

**Fix formatting issues:**
```
Add white-space: pre-wrap to <pre> tags for proper newlines
```

**Add new components:**
```
Add .info-box CSS class for informational callouts with icon support
```

**Update colors:**
```
Adjust dark mode --chinese-red to #DC143C for better visibility
```

**Add functionality:**
```
Add scroll-to-top button with smooth scrolling to JavaScript section
```

### 8. Troubleshooting

**Changes not applying:**
- Snippet may be cached
- Try restarting Claude Code session

**Syntax errors:**
- Validate CSS/JS before saving
- Check for unclosed brackets or quotes

**Dark mode broken:**
- Ensure all new styles have `[data-theme="dark"]` overrides
- Test both light and dark themes

## User Interaction Pattern

1. **Parse arguments**: Extract update description or changes from user input
2. **Check for force flag**: `-f` or `--force` skips confirmation
3. **Review and confirm**: Show summary and ask for confirmation (unless forced)
4. **Apply updates**: Make changes to HTML.md snippet
5. **Report completion**: Confirm location and note automatic application

## Technical Context

**File Format:** Markdown with YAML frontmatter
**Hook Event:** `UserPromptSubmit`
**Pattern Matching:** Triggered when HTML output formatting is needed
**Version Tracking:** `VERIFICATION_HASH` for content integrity
