# Multi-Config System with Priority-Based Merging

## Overview

The snippets system now supports multiple configuration files with automatic priority-based merging. This allows you to organize snippets across different contexts (personal, work, projects) while controlling which takes precedence when conflicts occur.

## Config File Patterns

Configuration files follow the pattern `config.{name}.json`:

- `config.json` - Base configuration (default priority: 0)
- `config.local.json` - Local overrides (default priority: 100)
- `config.work.json` - Work-specific snippets (default priority: 50)
- `config.personal.json` - Personal snippets (default priority: 50)
- `config.{anything}.json` - Custom named configs (default priority: 50)

## Priority System

### How It Works

1. **All config files are loaded** from the scripts directory
2. **Each has a priority** (integer, higher = more important)
3. **Snippets are merged by name** - higher priority wins
4. **Final merged config** is used by the snippet injector

### Default Priorities

| Config File | Default Priority | Purpose |
|-------------|-----------------|---------|
| `config.json` | 0 | Base/shared snippets |
| `config.local.json` | 100 | Local user overrides |
| `config.{name}.json` | 50 | Custom named configs |

### Setting Custom Priority

Add a `priority` field at the top level of any config:

```json
{
  "priority": 75,
  "mappings": [...]
}
```

Or use the CLI:

```bash
# Set priority for a named config
python3 snippets_cli.py --config-name work set-priority 80

# Set priority for local config (default target)
python3 snippets_cli.py set-priority 90

# Set priority for base config
python3 snippets_cli.py --use-base-config set-priority 5
```

## Usage Examples

### Create Snippet in Named Config

```bash
# Create work-specific snippet in config.work.json
python3 snippets_cli.py --config-name work create jira-link \
  --pattern "\\bJIRA\\b" \
  --description "Insert JIRA link helper" \
  --content "JIRA ticket helper content"
```

### View All Snippets with Source Info

```bash
# List with source config and priority
python3 snippets_cli.py --format json list --show-stats
```

Output shows:
```json
{
  "snippets": [
    {
      "name": "my-snippet",
      "source_config": "config.work.json",
      "priority": 75,
      ...
    }
  ],
  "configs": [
    {
      "filename": "config.json",
      "priority": 0,
      "snippet_count": 23
    },
    {
      "filename": "config.work.json",
      "priority": 75,
      "snippet_count": 5
    },
    {
      "filename": "config.local.json",
      "priority": 100,
      "snippet_count": 10
    }
  ]
}
```

### Override Snippet from Base Config

1. Base config has snippet "email" with pattern `\\bemail\\b`
2. Want different behavior in work context
3. Create override in work config:

```bash
python3 snippets_cli.py --config-name work create email \
  --pattern "\\bemail\\b|\\bcorporate-mail\\b" \
  --description "Corporate email helper" \
  --file work-email-template.md \
  --force
```

4. Set work config priority higher than base:

```bash
python3 snippets_cli.py --config-name work set-priority 60
```

Now the "email" snippet from `config.work.json` (priority 60) overrides the one from `config.json` (priority 0).

## Priority Resolution Examples

### Example 1: Default Behavior

**config.json** (priority 0):
```json
{
  "mappings": [
    {"name": "greeting", "pattern": "hello", ...}
  ]
}
```

**config.local.json** (priority 100):
```json
{
  "mappings": [
    {"name": "greeting", "pattern": "hey|hi", ...}
  ]
}
```

**Result**: Local version wins (priority 100 > 0)
- Pattern used: `hey|hi`
- Source: `config.local.json`

### Example 2: Three-Way Merge

**config.json** (priority 0):
```json
{
  "mappings": [
    {"name": "snippet-a", ...},
    {"name": "snippet-b", ...}
  ]
}
```

**config.work.json** (priority 50):
```json
{
  "mappings": [
    {"name": "snippet-b", ...},  // Overrides base
    {"name": "snippet-c", ...}   // New snippet
  ]
}
```

**config.local.json** (priority 100):
```json
{
  "mappings": [
    {"name": "snippet-c", ...}   // Overrides work
  ]
}
```

**Merged Result**:
- `snippet-a`: from config.json (only source)
- `snippet-b`: from config.work.json (overrides base)
- `snippet-c`: from config.local.json (highest priority)

## Best Practices

### 1. Organize by Context

```
config.json              # Shared, stable snippets
config.work.json         # Work-specific patterns
config.personal.json     # Personal shortcuts
config.project-x.json    # Project-specific helpers
config.local.json        # Personal overrides (highest priority)
```

### 2. Set Appropriate Priorities

- **Base (0)**: Shared, lowest priority
- **Project (40-60)**: Project-specific, medium priority
- **User (70-90)**: User preferences, high priority
- **Local (100)**: Personal overrides, highest priority

### 3. Document Priority Rationale

In each config, add a comment explaining the priority choice:

```json
{
  "priority": 75,
  "comment": "Work snippets override base but allow local overrides",
  "mappings": [...]
}
```

### 4. Version Control Strategy

**Commit to git**:
- `config.json` (shared)
- `config.work.json` (if team-wide)
- `config.{project}.json` (if project-specific)

**Add to .gitignore**:
- `config.local.json` (personal overrides)
- `config.*.json.bak` (backup files)

## Troubleshooting

### Check Which Config a Snippet Comes From

```bash
python3 snippets_cli.py --format json list my-snippet | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"Source: {d['snippets'][0]['source_config']} (priority: {d['snippets'][0]['priority']})\")"
```

### List All Configs and Priorities

```bash
python3 snippets_cli.py --format json list --show-stats | \
  python3 -c "import sys,json; d=json.load(sys.stdin); [print(f\"{c['filename']}: priority {c['priority']} ({c['snippet_count']} snippets)\") for c in d['data']['configs']]"
```

### Debug Priority Resolution

If a snippet isn't behaving as expected:

1. Check which config it's coming from:
   ```bash
   python3 snippets_cli.py list my-snippet --show-stats
   ```

2. View all configs' priorities:
   ```bash
   python3 snippets_cli.py list --show-stats
   ```

3. Adjust priorities if needed:
   ```bash
   python3 snippets_cli.py --config-name work set-priority 85
   ```

## Migration from Old System

The old two-config system (config.json + config.local.json) continues to work without changes:

- `config.json`: priority 0 (base)
- `config.local.json`: priority 100 (overrides)

No migration needed! The new system is backward compatible.

## Advanced: Dynamic Priority per Environment

Use environment variables to adjust priorities:

```bash
# Development: prioritize dev config
export SNIPPET_DEV_PRIORITY=90
python3 snippets_cli.py --config-name dev set-priority ${SNIPPET_DEV_PRIORITY}

# Production: prioritize prod config
export SNIPPET_PROD_PRIORITY=95
python3 snippets_cli.py --config-name prod set-priority ${SNIPPET_PROD_PRIORITY}
```

## API Reference

### CLI Commands

```bash
# Create snippet in named config
snippets_cli.py --config-name <name> create <snippet-name> ...

# Set priority for config
snippets_cli.py --config-name <name> set-priority <priority>

# List with source info
snippets_cli.py list --show-stats

# Update snippet in specific config
snippets_cli.py --config-name <name> update <snippet-name> ...

# Delete from specific config
snippets_cli.py --config-name <name> delete <snippet-name>
```

### Config File Structure

```json
{
  "priority": 50,  // Optional, defaults based on filename
  "mappings": [
    {
      "name": "snippet-name",
      "pattern": "regex-pattern",
      "snippet": ["path/to/file.md"],
      "enabled": true,
      "separator": "\n"
    }
  ]
}
```

## See Also

- [Snippet CLI Reference](../README.md)
- [Hook Configuration](../hooks/hooks.json)
- [Template Patterns](../templates/)
