---
name: "Copy to Clipboard"
description: "Use when user wants to copy content to clipboard (pbcopy). Triggers on PBCOPY, COPY, CLIPBOARD keywords."
pattern: "\\b(PBCOPY|COPY|CLIPBOARD)\\b[.,;:!?]?"
---

# Copy to Clipboard

When user requests copying content to clipboard:

1. **Use `pbcopy` command** - Pipe content directly to clipboard
2. **No confirmation needed** - Just execute the command
3. **Format properly** - Use heredoc for multi-line content

## Pattern

```bash
cat << 'EOF' | pbcopy
[content here]
EOF
```

## Examples

**Single line:**
```bash
echo "content" | pbcopy
```

**Multi-line:**
```bash
cat << 'EOF' | pbcopy
Line 1
Line 2
Line 3
EOF
```

**From variable:**
```bash
printf "%s" "$content" | pbcopy
```

## Rules

- Execute immediately without asking
- Confirm after with brief message: "Copied to clipboard"
- Use heredoc with `'EOF'` to preserve formatting
- Don't add extra newlines unless requested
