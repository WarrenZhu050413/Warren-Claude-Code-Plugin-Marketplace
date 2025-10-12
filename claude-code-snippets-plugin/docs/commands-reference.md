# Commands Reference

Complete reference for all snippet management commands.

## Table of Contents

- [Command Prefix](#command-prefix)
- [create-snippet](#create-snippet)
- [read-snippets](#read-snippets)
- [update-snippet](#update-snippet)
- [delete-snippet](#delete-snippet)
- [CLI Tool Usage](#cli-tool-usage)

---

## Command Prefix

All commands are prefixed with the plugin name:

```
/claude-code-snippets:<command-name>
```

---

## create-snippet

Create a new snippet with regex pattern matching.

### Usage

```bash
/claude-code-snippets:create-snippet <snippet-name> [description]
```

### Features

- Interactive guidance for missing information
- Automatic regex pattern formatting
- Automated test suite generation & execution
- Full snippet content display for verification
- Automatic `ANNOUNCE_USAGE: true` configuration

### Interactive Prompts

1. **Pattern keywords**: Enter keywords that should trigger the snippet
   - Example: `docker, container, dockerfile`
   - Converted to regex: `\b(docker|container|dockerfile)\b`

2. **Content**: Provide the snippet content
   - Paste directly into the prompt
   - Or load from a file

3. **Automated tests**: Tests run automatically after creation
   - Verifies pattern matching
   - Tests snippet injection
   - Validates configuration

4. **Content verification**: Full snippet content shown for review

### Examples

#### Basic Usage

```bash
/claude-code-snippets:create-snippet docker
```

Claude will guide you through:
```
What pattern keywords should trigger this snippet?
> docker, container, dockerfile

What content should be in this snippet?
> [You paste your Docker cheat sheet]

✅ Tests passed
✅ Snippet created: scripts/snippets/docker.md
✅ Configuration added
```

#### With Description

```bash
/claude-code-snippets:create-snippet docker Docker commands and best practices
```

### Output

- Snippet file created: `scripts/snippets/<name>.md`
- Configuration added to: `scripts/config.local.json`
- Test results displayed
- Full content shown for verification

### What Gets Created

**Snippet file** (`scripts/snippets/docker.md`):
```markdown
---
description: Docker commands and best practices
SNIPPET_NAME: docker
ANNOUNCE_USAGE: true
---

# Docker Snippet

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: docker

---

**VERIFICATION_HASH:** `generated-hash`

[Your content here...]
```

**Configuration** (`scripts/config.local.json`):
```json
{
  "name": "docker",
  "pattern": "\\b(docker|container|dockerfile)\\b",
  "snippet": ["snippets/docker.md"],
  "enabled": true
}
```

---

## read-snippets

List all configured snippets with beautiful formatting.

### Usage

```bash
# List all snippets
/claude-code-snippets:read-snippets

# Show specific snippet
/claude-code-snippets:read-snippets <snippet-name>
```

### Examples

#### List All Snippets

```bash
/claude-code-snippets:read-snippets
```

Output:
```
📋 Configured Snippets (3)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. HTML
   Pattern: \bHTML\b\.?
   Files: snippets/HTML.md
   Status: ✅ Enabled

2. docker
   Pattern: \b(docker|container|dockerfile)\b
   Files: snippets/docker.md
   Status: ✅ Enabled

3. nvim
   Pattern: \b(nvim|neovim)\b
   Files: snippets/nvim.md
   Status: ✅ Enabled
```

#### Show Specific Snippet

```bash
/claude-code-snippets:read-snippets docker
```

Output:
```
📄 Snippet: docker

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pattern: \b(docker|container|dockerfile)\b
Files: snippets/docker.md
Status: ✅ Enabled

Content Preview:
---
description: Docker commands and best practices
SNIPPET_NAME: docker
ANNOUNCE_USAGE: true
---

# Docker Snippet
[... content ...]
```

### Output Format

- List view shows all snippets with key info
- Detail view shows complete snippet configuration and content
- Status indicators: ✅ Enabled, ❌ Disabled
- File paths and pattern details

---

## update-snippet

Update an existing snippet's pattern or content.

### Usage

```bash
/claude-code-snippets:update-snippet <snippet-name>
```

### Features

- Shows current state before changes
- **Mandatory preview** of all proposed changes
- **Explicit approval gate** with options:
  - `Y` (Yes) - Apply changes
  - `N` (No) - Cancel
  - `D` (Diff) - Show detailed diff
  - `M` (Modify) - Edit the proposed changes
- Verification testing after update
- Automatic backup creation

### Workflow

1. **Current state shown**: Pattern and content displayed
2. **Propose changes**: Specify what to update
3. **Preview shown**: All changes displayed in full
4. **Approval required**: Must confirm before applying
5. **Backup created**: Original saved before changes
6. **Tests run**: Verification after update
7. **Confirmation**: Success message with details

### Examples

#### Update Pattern

```bash
/claude-code-snippets:update-snippet docker
```

```
Current state:
Pattern: \b(docker|container)\b

What would you like to update? (pattern/content/both)
> pattern

New pattern keywords:
> docker, container, dockerfile, compose

━━━ PREVIEW OF CHANGES ━━━

Pattern:
- OLD: \b(docker|container)\b
+ NEW: \b(docker|container|dockerfile|compose)\b

Content: [No changes]

Apply these changes? (Y/N/D/M)
> Y

✅ Backup created: scripts/snippets/docker.md.backup.20251012_143022
✅ Pattern updated
✅ Tests passed
✅ Update complete
```

#### Update Content

```bash
/claude-code-snippets:update-snippet docker
```

```
What would you like to update? (pattern/content/both)
> content

Provide new content:
> [You paste updated Docker cheat sheet]

━━━ PREVIEW OF CHANGES ━━━

Pattern: [No changes]

Content:
[Shows full diff of content changes]

Apply these changes? (Y/N/D/M)
> Y

✅ Update complete
```

### Approval Options

- **Y (Yes)**: Apply the changes immediately
- **N (No)**: Cancel the update, no changes made
- **D (Diff)**: Show detailed line-by-line diff
- **M (Modify)**: Go back and edit the proposed changes

---

## delete-snippet

Delete a snippet with automatic backup.

### Usage

```bash
# With confirmation prompt
/claude-code-snippets:delete-snippet <snippet-name>

# Skip confirmation (force)
/claude-code-snippets:delete-snippet <snippet-name> --force
```

### Features

- Shows what will be deleted before proceeding
- Confirmation prompt (unless `--force`)
- Automatic backup creation with timestamp
- Restore instructions provided
- Removes from both file system and configuration

### Workflow

1. **Shows details**: What will be deleted
2. **Confirmation**: Asks for approval (unless `--force`)
3. **Backup created**: Original saved with timestamp
4. **File deleted**: Snippet file removed
5. **Config updated**: Entry removed from configuration
6. **Restore info**: Instructions for recovery

### Examples

#### With Confirmation

```bash
/claude-code-snippets:delete-snippet docker
```

```
⚠️  DELETE SNIPPET: docker

This will delete:
- File: scripts/snippets/docker.md
- Configuration entry in config.local.json

Pattern: \b(docker|container|dockerfile)\b
Content preview:
[First 10 lines of content shown]

Are you sure you want to delete this snippet? (yes/no)
> yes

✅ Backup created: scripts/snippets/docker.md.backup.20251012_143530
✅ Snippet file deleted
✅ Configuration entry removed
✅ Deletion complete

To restore this snippet:
1. Copy backup: cp scripts/snippets/docker.md.backup.20251012_143530 scripts/snippets/docker.md
2. Re-add to config.local.json
3. Restart Claude Code
```

#### Force Delete (No Confirmation)

```bash
/claude-code-snippets:delete-snippet docker --force
```

```
✅ Backup created: scripts/snippets/docker.md.backup.20251012_143530
✅ Snippet deleted
```

### Backup Files

Backups are created with timestamp format:
```
<original-filename>.backup.YYYYMMDD_HHMMSS
```

Example:
```
scripts/snippets/docker.md.backup.20251012_143530
```

### Restoring Deleted Snippets

1. **Copy backup file**:
   ```bash
   cp scripts/snippets/docker.md.backup.20251012_143530 scripts/snippets/docker.md
   ```

2. **Re-add to configuration**:
   Edit `scripts/config.local.json` and add the configuration entry back.

3. **Restart Claude Code** to reload the plugin.

---

## CLI Tool Usage

For advanced users, direct CLI access is available via Python script.

### Location

```bash
cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts
```

### Commands

#### Create

```bash
python3 snippets_cli.py create <name> \
  --pattern '\b(keyword1|keyword2)\b' \
  --content "Your content here" \
  [--no-announce]  # Disable usage announcements
```

#### List

```bash
# List all snippets
python3 snippets_cli.py list

# With statistics
python3 snippets_cli.py list --show-stats

# Specific snippet
python3 snippets_cli.py list --name docker
```

#### Update

```bash
# Update pattern
python3 snippets_cli.py update <name> \
  --pattern '\b(new|pattern)\b'

# Update content
python3 snippets_cli.py update <name> \
  --content "New content"

# Update both
python3 snippets_cli.py update <name> \
  --pattern '\b(new|pattern)\b' \
  --content "New content"
```

#### Delete

```bash
# With backup
python3 snippets_cli.py delete <name> --backup

# Without backup (dangerous!)
python3 snippets_cli.py delete <name>
```

#### Test

```bash
# Test pattern matching
python3 snippets_cli.py test <name> "test text with keywords"
```

#### Validate

```bash
# Validate all snippets
python3 snippets_cli.py validate
```

### CLI Flags

- `--pattern`: Regex pattern for matching
- `--content`: Snippet content
- `--no-announce`: Disable usage announcements (CLI only)
- `--backup`: Create backup before deletion
- `--show-stats`: Show statistics in list view
- `--name`: Specify snippet name
- `--force`: Skip confirmation prompts (not all commands)

---

**Next:**
- [Configuration](configuration.md) - Configuration system details
- [Template Pattern](template-pattern.md) - Advanced template-based snippets
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
