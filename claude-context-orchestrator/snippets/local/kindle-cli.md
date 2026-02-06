
# Kindle CLI Quick Reference

Send files to Kindle via email. Installed globally via `uv tool install kindle-cli`.

## Common Commands

```bash
# Interactive picker (default mode)
kindle

# Direct send
kindle send document.pdf

# Fuzzy search mode
kindle send -f

# Multiselect (send multiple files as separate emails)
kindle send -m

# Auto-rename with Claude before sending
kindle send doc.pdf -a

# Auto-rename without confirmation prompt
kindle send doc.pdf -a -y

# Manual rename
kindle send doc.pdf -r

# Show more files per folder
kindle send -n 20

# Search additional directory
kindle send -d ~/Books

# List available files
kindle list-files

# View/modify config
kindle config
kindle config -a ~/Books      # Add directory
kindle config -r ~/Downloads  # Remove directory
```

## Supported Formats
PDF, EPUB, MOBI, DOC, DOCX, TXT, RTF, HTML (max 25MB per file)

## Configuration
Config file: `~/.config/kindle-cli/config.json`
Set kindle_email to your Kindle's email address (found in Amazon account settings).