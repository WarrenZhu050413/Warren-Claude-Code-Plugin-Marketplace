---
name: Using CLIs Effectively
description: Best practices and patterns for discovering, using, and integrating with command-line interfaces
---

# Using CLIs Effectively

## Skill Overview

This skill teaches you how to effectively discover, use, and integrate with command-line interfaces (CLIs), with particular focus on custom Python CLIs and tool wrappers.

## Discovery Process

### 1. Start with Help

**Always begin with `--help`:**

```bash
# Basic help
<cli> --help

# Subcommand help
<cli> <subcommand> --help

# Some CLIs use -h
<cli> -h
```

**Example:**
```bash
python3 snippets_cli.py --help
python3 snippets_cli.py update --help
```

### 2. Explore the Source

**For Python CLIs, read the argparse setup:**

```bash
# Find the CLI file
find ~/.claude -name "*cli.py" | grep snippets

# Read the main function and argparse setup
grep -A 50 "argparse" <cli_file>
grep -A 20 "add_argument" <cli_file>
```

**Look for:**
- Subcommands (create, update, delete, list)
- Required vs optional arguments
- Flag types (store_true, choices, etc.)
- Default values

### 3. List Current State

**Before modifying anything, understand what exists:**

```bash
# List all items
<cli> list

# Get specific item details
<cli> get <name>

# Show current configuration
<cli> config show
```

## Safe Usage Patterns

### 1. Dry Run First

**Test commands without making changes:**

```bash
# Many CLIs support dry-run
<cli> update <item> --dry-run
<cli> delete <item> --dry-run --verbose
```

### 2. Use Verbose Mode

**See what's happening:**

```bash
<cli> update <item> --verbose
<cli> update <item> -v
<cli> update <item> --debug
```

### 3. Create Backups

**Before destructive operations:**

```bash
# Check for backup flags
<cli> delete <item> --backup
<cli> update <item> --backup-dir ~/backups

# Or manually backup
cp config.json config.json.backup
```

### 4. Validate Before Execute

**Use get/show commands to verify:**

```bash
# 1. Check current state
<cli> get <name>

# 2. Plan your changes
<cli> update <name> --pattern "new-pattern" --dry-run

# 3. Execute
<cli> update <name> --pattern "new-pattern"

# 4. Verify
<cli> get <name>
```

## Common CLI Patterns

### CRUD Operations

Most CLIs follow CRUD patterns:

```bash
# Create
<cli> create <name> --pattern "..." --file content.md

# Read/List
<cli> list
<cli> get <name>

# Update
<cli> update <name> --pattern "new-pattern"
<cli> update <name> --file new-content.md

# Delete
<cli> delete <name>
<cli> delete <name> --force  # Skip confirmation
```

### Configuration Management

**Multiple config files:**

```bash
# Default (usually local config)
<cli> update <name> --pattern "..."

# Specific config
<cli> update <name> --pattern "..." --config work

# Base config
<cli> update <name> --pattern "..." --base
```

### Output Formats

**Get machine-readable output:**

```bash
# JSON output
<cli> list --json
<cli> get <name> --json

# Pipe to jq for filtering
<cli> list --json | jq '.[] | select(.enabled == true)'

# TSV for spreadsheets
<cli> list --format tsv
```

## Integration Patterns

### 1. Scripting CLIs

**Write scripts that use CLIs:**

```bash
#!/bin/bash
set -e  # Exit on error

# Function to safely update snippet
update_snippet() {
    local name="$1"
    local pattern="$2"

    # Check if exists
    if ! snippets_cli.py get "$name" >/dev/null 2>&1; then
        echo "Error: Snippet '$name' not found"
        return 1
    fi

    # Update with backup
    snippets_cli.py update "$name" \
        --pattern "$pattern" \
        --backup

    echo "Updated $name"
}

# Use the function
update_snippet "download-pdf" "\\bDOWNLOAD\\b[.:;,]?"
```

### 2. Error Handling

**Check exit codes:**

```bash
if <cli> update <name> --pattern "..."; then
    echo "Success"
else
    echo "Failed with exit code $?"
    exit 1
fi
```

### 3. Parsing Output

**Extract information from CLI output:**

```bash
# Get JSON and parse
pattern=$(<cli> get <name> --json | jq -r '.pattern')

# Or use grep
<cli> get <name> | grep "pattern:" | cut -d'"' -f2
```

## Real Example: Snippets CLI

### Discovery

```bash
# 1. Find the CLI
find ~/.claude -name "snippets_cli.py"

# 2. Get help
python3 snippets_cli.py --help
python3 snippets_cli.py update --help

# 3. List current snippets
python3 snippets_cli.py list | head -20
```

### Safe Update Workflow

```bash
cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/scripts

# 1. Check current state
python3 snippets_cli.py get download-pdf

# Output shows:
# "pattern": "\\b(DOWNLOAD|PDF)\\b[.:;,]?"

# 2. Update pattern only
python3 snippets_cli.py update download-pdf \
    --pattern "\\bDOWNLOAD\\b[.:;,]?"

# 3. Verify change
python3 snippets_cli.py get download-pdf | grep pattern

# 4. Check it works
python3 snippets_cli.py list | grep -A 5 "download-pdf"
```

### Update Pattern and Content

```bash
# Update both at once
python3 snippets_cli.py update download-pdf \
    --pattern "\\bDOWNLOAD\\b[.:;,]?" \
    --file ~/new-content.md

# Or update from another snippet
python3 snippets_cli.py get other-snippet --json | \
    jq -r '.content' | \
    python3 snippets_cli.py update download-pdf --content -
```

## Advanced Patterns

### Batch Operations

**Update multiple items:**

```bash
# Using a loop
for snippet in mail gcal post; do
    python3 snippets_cli.py update "$snippet" --enabled true
done

# Or with xargs
echo "mail gcal post" | xargs -n1 python3 snippets_cli.py get
```

### Programmatic Usage

**Use CLIs from Python:**

```python
import subprocess
import json

def get_snippet(name):
    """Get snippet details via CLI"""
    result = subprocess.run(
        ['python3', 'snippets_cli.py', 'get', name, '--json'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None

def update_pattern(name, pattern):
    """Update snippet pattern via CLI"""
    result = subprocess.run(
        ['python3', 'snippets_cli.py', 'update', name,
         '--pattern', pattern],
        capture_output=True,
        text=True
    )
    return result.returncode == 0
```

### Testing CLI Changes

**Before committing changes:**

```bash
# 1. Backup current config
cp config.local.json config.local.json.backup

# 2. Make changes
python3 snippets_cli.py update <name> --pattern "..."

# 3. Test in Claude
# (Send a message that should trigger the snippet)

# 4. If broken, restore
cp config.local.json.backup config.local.json

# 5. If working, commit
git add config.local.json
git commit -m "Update: Changed <name> pattern"
```

## Troubleshooting

### CLI Not Found

```bash
# Find it
find ~/.claude -name "*cli.py"
find ~/Desktop -name "*cli.py"

# Check PATH
which <cli-command>

# Use full path
python3 /full/path/to/cli.py
```

### Permission Denied

```bash
# Make executable
chmod +x <cli-file>

# Or use python3 directly
python3 <cli-file>
```

### Invalid Arguments

```bash
# Check help for exact syntax
<cli> <subcommand> --help

# Check if argument name is correct
# (sometimes --dry-run vs --dryrun)

# Read the source to be sure
grep "add_argument.*dry" <cli-file>
```

### Config File Issues

```bash
# Validate JSON
cat config.local.json | python3 -m json.tool

# Check file exists
ls -la config*.json

# Check permissions
ls -la config.local.json
```

## Best Practices Summary

1. **Always check `--help` first**
2. **Read the source for Python CLIs** (argparse section)
3. **List before modifying** (understand current state)
4. **Use dry-run when available**
5. **Enable verbose mode** for debugging
6. **Create backups** before destructive operations
7. **Validate after changes** (get/show commands)
8. **Check exit codes** in scripts
9. **Use JSON output** for programmatic use
10. **Document your CLI usage** (scripts, examples)

## Related Skills

- **MANAGESKILL** - Managing and creating Agent Skills
- **TDD** - Test-driven development for CLI tools
- **DEEPSEARCH** - Finding CLIs and their documentation

## Quick Reference Card

```bash
# Discovery
<cli> --help
<cli> <cmd> --help
grep -r "argparse" <cli-dir>

# Safe Operations
<cli> get <name>              # Check before modify
<cli> update <name> --dry-run # Test first
<cli> delete <name> --backup  # Backup first

# Common Patterns
<cli> list                    # Show all
<cli> create <name> [opts]    # Create new
<cli> update <name> [opts]    # Modify existing
<cli> delete <name>           # Remove

# Output Formats
<cli> list --json            # Machine readable
<cli> get <name> --verbose   # Detailed info

# Configuration
<cli> cmd --config work      # Named config
<cli> cmd --base             # Base config
<cli> cmd                    # Default (local)
```
