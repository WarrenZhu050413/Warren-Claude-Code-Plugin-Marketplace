---
name: "Clipboard Output"
description: "Copy output to macOS clipboard using pbcopy instead of writing to file"
---

# Clipboard Output Mode

When this snippet is active, output content directly to the clipboard instead of creating files.

## Usage

Use `pbcopy` to send output to the clipboard:

```bash
# Copy text directly
echo "content" | pbcopy

# Copy file contents
cat file.txt | pbcopy

# Copy command output
ls -la | pbcopy
```

## For Code Generation

When generating code or text that should go to clipboard:

1. Write to a temp file first
2. Copy to clipboard with pbcopy
3. Confirm to user what was copied

```bash
cat <<'EOF' | pbcopy
[generated content here]
EOF
echo "Copied to clipboard!"
```

## Notes

- `pbcopy` is macOS-specific
- On Linux, use `xclip -selection clipboard` instead
- Content remains in clipboard until overwritten
