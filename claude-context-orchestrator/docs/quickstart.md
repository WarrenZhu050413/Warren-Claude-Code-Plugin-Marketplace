# Snippets CLI - Quick Start Guide

✅ **Installation Complete!**

The `snippets` command is now installed at: `~/.local/bin/snippets`

---

## Using the Command

After restarting your terminal (or running `source ~/.zshrc`), you can use `snippets` from anywhere:

```bash
snippets list
snippets create <name> --pattern "<regex>" --description "<desc>" --content "<text>"
snippets update <name> --pattern "<new-pattern>"
snippets delete <name> --force
snippets validate
snippets test <name> "<text>"
```

---

## Quick Examples

### 1. List All Snippets
```bash
snippets list
```

### 2. List with Statistics
```bash
snippets list --show-stats
```

### 3. Create a New Snippet
```bash
snippets create hello \
  --pattern "hello|hi|hey" \
  --description "Greeting helper" \
  --content "Respond politely to greetings"
```

### 4. Test a Pattern
```bash
snippets test hello "hi there"
# Returns: matched: true
```

### 5. Update a Snippet
```bash
snippets update hello --pattern "hello"
```

### 6. Delete a Snippet (with backup)
```bash
snippets delete hello --force
```

### 7. Validate Configuration
```bash
snippets validate
```

---

## Text Output Format

For human-readable output instead of JSON:

```bash
snippets --format text list --show-stats
```

---

## Working with Different Configs

By default, changes go to `config.local.json` (gitignored).

To modify the base config (shared/committed):
```bash
snippets --use-base-config create shared-snippet \
  --pattern "shared" \
  --description "Team snippet" \
  --content "..."
```

---

## Getting Help

```bash
snippets --help              # General help
snippets create --help       # Help for create command
snippets list --help         # Help for list command
```

---

## Current Status

Run this to check everything is working:
```bash
snippets validate
```

You should see:
```json
{
  "config_valid": true,
  "files_checked": 44,
  "issues": []
}
```

---

## Uninstalling

If you ever want to remove the global command:

```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts
./uninstall.sh ~/.local/bin
```

---

## Next Steps

1. **Restart your terminal** to activate the PATH change
2. Try: `snippets list`
3. Create your first snippet!
4. Read the full guide: `cat INSTALL.md`

Enjoy! 🚀
