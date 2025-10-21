---
description: List and view configured snippets
---

# Read Snippets

Lists all configured snippets with their patterns and status.

## Phase 0: CLI Help Check (**MANDATORY FIRST STEP**)

**CRITICAL**: Before ANY other operation, ALWAYS check the CLI help to understand current available options.

```bash
# Get main help
main_help=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py --help 2>&1)

# Get list subcommand help
list_help=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py list --help 2>&1)
```

**Parse the help output to extract:**
- Available options (e.g., `--show-content`, `--show-stats`)
- Global options (e.g., `--config`, `--snippets-dir`, `--use-base-config`, `--format`)
- Positional arguments (e.g., optional `name` parameter)
- Output format options

**Store parsed options for validation in Phase 1.**

## Phase 1: Parse & Validate

Parse `$ARGUMENTS` for optional snippet name:
- **No arguments**: List all snippets (summary view)
- **With name**: Show detailed view of specific snippet
- **Config target**: Whether to use base config (--use-base-config flag) - defaults to local config

Validate that snippet name (if provided) is non-empty and doesn't contain invalid characters.

## Phase 2: Execute CLI

```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py ${use_base_config:+--use-base-config} list ${name:+$name} --snippets-dir ../commands/local 2>&1
```

**Note about --use-base-config:**
- **Without flag** (default): Lists snippets from `config.local.json` (personal snippets)
- **With flag**: Lists snippets from `config.json` (global/shared snippets) only
- Most users want personal snippets, so default is correct
- Use `--use-base-config` to view only global/shared snippets

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

Check permissions: ls -la /Users/wz/.claude/plugins/.../commands/local/
```

## Important Notes

- **Show icons**: ✓ for enabled, ✗ for disabled
- **Format sizes**: Convert bytes to KB/MB
- **Group by status**: Show enabled first, then disabled
- **Highlight patterns**: Make pattern alternatives clear
- **Be helpful**: Suggest actions user can take
