---
name: "Markdown Preview"
description: "Auto-preview created markdown files with nvim MarkdownPreview"
---

# Markdown Preview Protocol

When creating markdown artifacts, automatically preview them using:

```bash
nvim -c "MarkdownPreview" {filepath}
```

Run in background to avoid blocking.

## Implementation

After writing any `.md` file:
1. Run: `nvim -c "MarkdownPreview" /path/to/file.md` with `run_in_background: true`
2. Browser opens with live preview
3. Continue working while preview runs
