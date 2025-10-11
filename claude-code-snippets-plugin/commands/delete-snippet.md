---
description: Delete a snippet with optional backup
---

# Delete Snippet

Deletes a snippet from the configuration. Creates a backup by default.

## Phase 1: Parse & Validate

Extract from `$ARGUMENTS`:
- **Snippet name**: Which snippet to delete
- **Force flag**: `--force` or `-f` to skip confirmation

## Phase 2: Show Current State

Before deletion, show what will be deleted:

```bash
current=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py list "$name" --snippets-dir ../commands/warren 2>&1)
```

Display:

```
📄 Snippet to delete: {name}

  Pattern: {pattern}
  Alternatives: {count} ({list them})
  File: {file} ({size})
  Status: {✓ Enabled | ✗ Disabled}
```

## Phase 3: Confirmation (Unless --force)

**IMPORTANT**: ALWAYS ask for confirmation unless `--force` is provided.

```
⚠️  WARNING: You are about to delete snippet '{name}'

This will:
  • Remove snippet from configuration
  • Delete snippet file: {file}
  • Create backup at: /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/backups/{timestamp}_{name}/

⚠️  This action cannot be undone (except via backup).

Do you want to proceed? [y/N]:
```

Handle responses:
- **y/yes**: Proceed to deletion
- **n/no/anything else**: Cancel operation

If user cancels:
```
❌ Deletion cancelled. Snippet '{name}' was not deleted.
```

## Phase 4: Execute Deletion

Only after confirmation:

```bash
result=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py delete "$name" --backup --snippets-dir ../commands/warren 2>&1)
exit_code=$?
```

## Phase 5: Handle Result

### On Success

```
✅ Snippet '{name}' deleted successfully!

📦 Backup created:
  Location: /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/backups/{timestamp}_{name}/
  Files:
    • {name}.md ({size})
    • config_backup.json

💡 To restore this snippet:
  1. Copy files from backup directory
  2. Re-run /create-snippet with restored files

Configuration has been updated. Changes take effect immediately.
```

### On Error

**If snippet not found:**
```
❌ Snippet '{name}' not found.

Available snippets: {list all names}

Cannot delete a snippet that doesn't exist.
```

**If deletion fails:**
```
❌ Failed to delete snippet '{name}': {error_message}

The snippet was not deleted. Check:
  • File permissions
  • Backup directory is writable
  • Snippet file exists

No changes were made to your configuration.
```

## Important Notes

- **ALWAYS create backup**: Unless explicitly disabled
- **ALWAYS ask confirmation**: Unless `--force` is provided
- **Show what's being deleted**: Full details before confirmation
- **Provide restore instructions**: Tell user how to undo
- **Be extra cautious**: Deletion is serious - make it clear
- **Validate first**: Check snippet exists before asking confirmation
