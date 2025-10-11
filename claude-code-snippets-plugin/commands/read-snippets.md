---
description: List and view configured snippets
---

# Read Snippets

Lists all configured snippets with their patterns and status.

## Usage

Parse `$ARGUMENTS` for optional snippet name. If provided, show detailed view of that snippet. Otherwise, list all snippets.

## Execute

```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py list ${name:+$name} --snippets-dir ../commands/warren 2>&1
```

## Output Formatting

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

## Error Handling

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

## Important Notes

- **Show icons**: ✓ for enabled, ✗ for disabled
- **Format sizes**: Convert bytes to KB/MB
- **Group by status**: Show enabled first, then disabled
- **Highlight patterns**: Make pattern alternatives clear
- **Be helpful**: Suggest actions user can take
