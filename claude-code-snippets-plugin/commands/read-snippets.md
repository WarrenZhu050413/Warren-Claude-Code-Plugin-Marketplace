---
description: List and view configured snippets
---

# Read Snippets

Lists all configured snippets with their patterns and status.

## Phase 1: Parse & Validate

Parse `$ARGUMENTS` for optional snippet name:
- **No arguments**: List all snippets (summary view)
- **With name**: Show detailed view of specific snippet

Validate that snippet name (if provided) is non-empty and doesn't contain invalid characters.

## Phase 2: Execute CLI

```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py list ${name:+$name} --snippets-dir ../commands/warren 2>&1
```

## Phase 3: Format Output

### For List (no name provided):

```
📚 Configured Snippets ({count} total, {enabled} enabled)

{for each snippet:}
  {icon} {name}
     Pattern: {pattern}
     Alternatives: {count} ({list first 3...})
     File: {file} ({size})
     Status: {✓ Enabled | ✗ Disabled}

Summary:
  Total: {total_count}
  Enabled: {enabled_count}
  Disabled: {disabled_count}

💡 Use `/read-snippets {name}` to view full snippet content
```

### For Specific Snippet (name provided):

```
📄 Snippet: {name}

📋 Configuration:
  Pattern: {pattern}
  Alternatives: {count}
    • {list all alternatives}

  File: {file} ({size})
  Status: {✓ Enabled | ✗ Disabled}
  Verification Hash: {hash}

📝 Full Content:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{display full file content}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Quick Actions:
  • Update: /update-snippet {name}
  • Delete: /delete-snippet {name}
  • Test: Type "{first_alternative}" to trigger injection
```

## Phase 4: Handle Errors

**If snippet not found:**
```
❌ Snippet '{name}' not found.

Available snippets: {list all names}

Did you mean one of these?
```

**If no snippets configured:**
```
📭 No snippets configured yet.

Create your first snippet with:
/create-snippet {name}

💡 Snippets automatically inject context when their pattern matches your message!
```

### Common Edge Cases

**Snippet name with special characters:**
```
❌ Error: Snippet name may contain special characters.

Try quoting the name: /read-snippets "my-snippet-name"
```

**Corrupted configuration:**
```
❌ Error: Failed to parse snippets configuration.

The config.json file may be corrupted. To fix:
1. Check backups/ directory for recent backup
2. Restore from backup, or
3. Delete config.json to start fresh (will lose all snippets)
```

**Permission denied:**
```
❌ Error: Permission denied reading snippets directory.

Check permissions: ls -la /Users/wz/.claude/plugins/.../commands/warren/
```

## Important Notes

- **Show icons**: ✓ for enabled, ✗ for disabled
- **Format sizes**: Convert bytes to KB/MB
- **Group by status**: Show enabled first, then disabled
- **Highlight patterns**: Make pattern alternatives clear
- **Be helpful**: Suggest actions user can take
