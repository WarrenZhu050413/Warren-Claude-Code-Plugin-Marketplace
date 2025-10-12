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

## Phase 3: Build Preview & Request Approval

**IMPORTANT**: ALWAYS show preview and ask for confirmation unless `--force` is provided.

### Generate Deletion Preview

Display complete details of what will be deleted:

```
═══════════════════════════════════════════════════════════
⚠️  PREVIEW: Deletion of '{name}' Snippet
═══════════════════════════════════════════════════════════

📋 SNIPPET DETAILS:
  Name: {name}
  Pattern: {pattern}
  Alternatives: {count} ({list them})
  File: {file} ({size})
  Status: {✓ Enabled | ✗ Disabled}

🗑️  ACTIONS TO BE PERFORMED:
  ✖ Remove snippet from configuration
  ✖ Delete snippet file: {file}
  ✓ Create backup at: backups/{timestamp}_{name}/
     Format: YYYYMMDD_HHMMSS (e.g., 20251012_143022_{name}/)

⚠️  IMPORTANT:
  This action cannot be undone (except via backup restoration).
  Backup will include: {name}.md + config_backup.json

═══════════════════════════════════════════════════════════
```

### Request Approval

**CRITICAL**: Do NOT delete without explicit approval.

```
🚦 Do you want to delete this snippet?

Options:
  [Y] Yes - Delete snippet with backup
  [N] No - Cancel, do not delete
  [D] Details - Show current snippet content before deciding

Your choice [Y/N/D]:
```

Handle responses:
- **Y/yes**: Proceed to Phase 4 (Execute CLI)
- **N/no**: Cancel operation
- **D/details**: Show full snippet content, then re-ask

If user says NO:
```
❌ Deletion cancelled. Snippet '{name}' was not deleted.
```

If user requests Details:
```bash
echo ""
echo "📄 Current Snippet Content:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/commands/snippets/${name}.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
# Re-ask for confirmation
```

## Phase 4: Execute CLI

Only after confirmation (Phase 3 approval received):

```bash
result=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py delete "$name" --backup --snippets-dir ../commands/warren 2>&1)
exit_code=$?
```

## Phase 5: Handle Result

### On Success

```
✅ Snippet '{name}' deleted successfully!

📦 Backup created:
  Location: backups/20251012_143022_{name}/
  Timestamp format: YYYYMMDD_HHMMSS
  Files:
    • {name}.md ({size})
    • config_backup.json

💡 To restore this snippet:
  1. Copy files from backup directory
  2. Run: /create-snippet {name} --file backups/20251012_143022_{name}/{name}.md

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

### Common Edge Cases

**Snippet in use during deletion:**
```
⚠️  Warning: This snippet may be currently loaded in active sessions.

Deletion will take effect immediately for new messages.
Active sessions may still reference old snippet until restart.

Continue with deletion? [y/N]:
```

**Backup directory full:**
```
❌ Error: Cannot create backup - disk space full.

Options:
1. Free up space and retry
2. Delete old backups from backups/ directory
3. Skip backup (dangerous): --no-backup flag
```

**Permission denied on delete:**
```
❌ Error: Permission denied deleting snippet file.

Check permissions: ls -la /Users/wz/.claude/plugins/.../commands/warren/snippets/
You may need to fix permissions: chmod 644 {file}
```

**Backup creation fails:**
```
❌ Error: Snippet deleted but backup creation failed.

Snippet: {name} has been removed from configuration
Warning: No backup was created
File may be at: {original_path} (if not cleaned up)

Recommendation: Manually backup remaining files
```

## Phase 6: Verification

After successful deletion, verify and show remaining snippets:

```bash
# List remaining snippets to confirm deletion
remaining=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py list --snippets-dir ../commands/warren 2>&1)

echo ""
echo "📚 Remaining Snippets:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$remaining"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✓ Verified: '{name}' is no longer in the configuration."
```

This provides closure and confirms the deletion was successful.

## Important Notes

- **ALWAYS create backup**: Unless explicitly disabled
- **ALWAYS ask confirmation**: Unless `--force` is provided
- **Show what's being deleted**: Full details before confirmation
- **Provide restore instructions**: Tell user how to undo
- **Be extra cautious**: Deletion is serious - make it clear
- **Validate first**: Check snippet exists before asking confirmation
