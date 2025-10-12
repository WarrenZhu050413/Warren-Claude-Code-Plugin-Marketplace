# Claude Code Snippets Plugin - Complete Documentation

## Table of Contents

- [Configuration System](#configuration-system)
- [Config Structure](#config-structure)
- [Pattern Examples](#pattern-examples)
- [Available Commands](#available-commands)
- [How It Works](#how-it-works)
- [Directory Structure](#directory-structure)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)
- [Development & Customization](#development--customization)
- [Tips & Best Practices](#tips--best-practices)

---

## Configuration System

Note that the plugin loads both configuration files. If a snippet name exists in both configs, local wins.

1. **Base config (`config.json`)**:
   - Minimal shared examples
   - Contains 2 snippets (HTML, nvim)
   - Simple starting point

2. **Example config (`config.local.json`)**:
   - **Contains 20+ example snippets** from real usage
   - Shows patterns for email, calendar, search, HTML, testing, etc.
   - **Committed to repo** as learning examples
   - References files in `commands/warren/` (your personal snippets directory)
   - **Overrides base config** by snippet name

3. **Merge behavior**:
   - If a snippet name exists in both configs, **local wins**
   - Otherwise, snippets from both configs are combined
   - Result: You get base examples + example snippets

**What's included in config.local.json**:

- 20+ real-world snippet examples
- Patterns for common workflows (email, calendar, HTML, search, etc.)
- Non-sensitive snippets only (sensitive ones are gitignored)
- References your personal snippets in `commands/warren/`

**To use the examples**:

1. Browse `config.local.json` to see what's available
2. Create your own snippets in `commands/warren/` to match the patterns
3. Or modify the patterns to match your own workflow

**Example**:

```json
// config.json (base - 2 snippets)
{
  "mappings": [
    {
      "name": "HTML",
      "pattern": "\\bHTML\\b\\.?",
      "snippet": ["snippets/HTML.md"],
      "enabled": true
    },
    {
      "name": "nvim",
      "pattern": "\\b(nvim|neovim)\\b",
      "snippet": ["snippets/nvim.md"],
      "enabled": true
    }
  ]
}

// config.local.json (example snippets - 20+ examples)
{
  "mappings": [
    {
      "name": "mail",
      "pattern": "\\b(email|mail|gmail)\\b",
      "snippet": ["../commands/warren/mail.md"],
      "enabled": true
    },
    {
      "name": "gcal",
      "pattern": "\\b(calendar|gcal)\\b",
      "snippet": ["../commands/warren/gcal.md"],
      "enabled": true
    }
    // ... 20+ more example snippets
  ]
}

// Result: All snippets loaded and available as examples
```

## Config Structure

```json
{
  "mappings": [
    {
      "name": "HTML",
      "pattern": "\\bHTML\\b\\.?",
      "snippet": ["snippets/HTML.md"],
      "enabled": true,
      "separator": "\n"
    }
  ]
}
```

## Pattern Examples

The `pattern` field uses **regex**:

```javascript
// Match exact word (case-insensitive)
"\\bHTML\\b"; // Matches: "HTML", "html", but not "htmlparse"

// Match multiple alternatives
"\\b(docker|container|dockerfile)\\b"; // Matches any of these words

// Match phrases with optional spaces
"\\b(google\\s*calendar|gcal)\\b"; // Matches: "google calendar", "googlecalendar", "gcal"

// Case doesn't matter - all patterns are matched case-insensitively
```

## Available Commands

All commands are prefixed with the plugin name:

### `/claude-code-snippets:create-snippet`

Create a new snippet with regex pattern matching. Features:

- Interactive guidance for missing information
- Automatic regex pattern formatting
- Automated test suite generation & execution
- Full snippet content display for verification

**Example**:

```
/claude-code-snippets:create-snippet docker
# Then follow prompts for pattern and content
# Tests run automatically after creation
```

### `/claude-code-snippets:read-snippets`

List all configured snippets with beautiful formatting.

**Example**:

```
/claude-code-snippets:read-snippets
# Or for specific snippet:
/claude-code-snippets:read-snippets docker
```

### `/claude-code-snippets:update-snippet`

Update an existing snippet's pattern or content. Features:

- Shows current state before changes
- **Mandatory preview** of all proposed changes
- **Explicit approval gate** (Y/N/D/M options)
- Verification testing after update

**Example**:

```
/claude-code-snippets:update-snippet docker
# Shows preview, asks for approval before applying
```

### `/claude-code-snippets:delete-snippet`

Delete a snippet (creates backup by default). Features:

- Shows what will be deleted
- Confirmation prompt (unless --force)
- Automatic backup creation
- Restore instructions provided

**Example**:

```
/claude-code-snippets:delete-snippet docker
```

## How It Works

### 1. Hook System

The plugin uses a `UserPromptSubmit` hook that runs on **every prompt** you send:

```
You type: "I need help with HTML formatting"
         ↓
Hook intercepts → Checks all regex patterns
         ↓
"HTML" matches \bHTML\b pattern!
         ↓
Injects snippets/HTML.md into context
         ↓
Claude receives your prompt + HTML snippet
```

### 2. Pattern Matching

- All patterns are **regex** (regular expressions)
- Matching is **case-insensitive**
- Patterns can match **anywhere** in your prompt
- Multiple snippets can match the same prompt

### 3. Snippet Files

- Stored in `scripts/snippets/*.md`
- Can be multiple files combined with separators
- Support verification hashes for testing

## Directory Structure

```
~/.claude/plugins/claude-code-snippets/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   ├── create-snippet.md        # /create-snippet command
│   ├── read-snippets.md         # /read-snippets command
│   ├── update-snippet.md        # /update-snippet command
│   ├── delete-snippet.md        # /delete-snippet command
│   └── warren/                  # Example personal snippets (committed)
│       ├── *.md                 # 20+ example snippets
│       └── sensitive/           # Gitignored sensitive snippets
├── hooks/
│   └── hooks.json               # Hook configuration
├── scripts/
│   ├── config.json              # Base configuration (2 snippets)
│   ├── config.local.json        # Example configuration (20+ snippets, committed)
│   ├── snippets_cli.py          # CLI tool for CRUD operations
│   ├── snippet_injector.py      # Hook script (runs automatically)
│   └── snippets/
│       ├── HTML.md              # Shared HTML snippet
│       └── nvim.md              # Shared nvim snippet
├── tests/
│   └── warren/                  # Example test files (committed)
│       ├── *.sh                 # Test scripts for snippets
│       └── sensitive/           # Gitignored sensitive tests
├── .gitignore                   # Excludes only sensitive files
└── README.md                    # This file
```

**Gitignored directories** (sensitive only):

- `commands/warren/sensitive/` - Sensitive snippet files only
- `tests/warren/sensitive/` - Sensitive test files only
- **Everything else is committed as examples**, including `config.local.json`

## Advanced Usage

### Multi-File Snippets

Combine multiple files into one snippet:

```json
{
  "name": "multitest",
  "pattern": "\\b(multitest|multi-test)\\b",
  "snippet": ["snippets/multitest_part1.md", "snippets/multitest_part2.md"],
  "separator": "\n\n---\n\n",
  "enabled": true
}
```

### Temporarily Disable a Snippet

Edit `config.json` and set `"enabled": false`:

```json
{
  "name": "HTML",
  "pattern": "\\bHTML\\b",
  "snippet": ["snippets/HTML.md"],
  "enabled": false // <-- Temporarily disabled
}
```

### Verification Hashes

Add verification hashes to test injection:

```markdown
# My Snippet

**VERIFICATION_HASH:** `abc123def456`

Your content here...
```

Then test: "Can you tell me the verification hash?" - If Claude returns the hash, injection worked!

## Troubleshooting

### Snippet Not Injecting

1. **Check pattern**: Does it match your prompt?

   ```bash
   cd ~/.claude/plugins/claude-code-snippets/scripts
   python3 snippets_cli.py test HTML "testing HTML here"
   ```

2. **Check if enabled**: Look in `config.json` for `"enabled": true`

3. **Check file exists**:

   ```bash
   ls ~/.claude/plugins/claude-code-snippets/scripts/snippets/
   ```

4. **Check hook is loaded**:
   ```bash
   claude --debug
   # Should show: "Loaded hook: snippet-injector"
   ```

### Pattern Not Matching

Test your regex pattern:

```bash
cd ~/.claude/plugins/claude-code-snippets/scripts
python3 snippets_cli.py test mysnippet "your test text here"
```

### CLI Commands Not Found

Make sure the script is executable:

```bash
chmod +x ~/.claude/plugins/claude-code-snippets/scripts/snippets_cli.py
chmod +x ~/.claude/plugins/claude-code-snippets/scripts/snippet_injector.py
```

## Examples

### Example 1: Docker Cheat Sheet

```bash
# Create snippet
/claude-code-snippets:create-snippet docker

# When prompted:
Pattern keywords: docker, container, dockerfile
Content: [paste your Docker cheat sheet]

# Automated tests run automatically
# Full snippet content displayed for verification

# Now whenever you mention "docker", it auto-injects!
claude -p "How do I optimize my docker image?"
```

### Example 2: Search Optimization Guide

```bash
# Create snippet
/claude-code-snippets:create-snippet search

# Pattern: \b(search|searching|websearch)\b
# Content: Your search optimization tactics

# Auto-injects on:
claude -p "Help me search for Python tutorials"
```

### Example 3: Project-Specific Context

```bash
# Create snippet
/claude-code-snippets:create-snippet myproject

# Pattern: \b(myproject|project|codebase)\b
# Content: Architecture overview, conventions, etc.

# Auto-injects on:
claude -p "In my project, how should I structure this?"
```

## Development & Customization

### Example Snippets in config.local.json

The plugin includes **20+ example snippets** in `config.local.json` to help you get started:

**What's included**:

- Email/Gmail automation context
- Google Calendar helpers
- Search optimization tactics
- HTML formatting guidelines
- Code testing patterns (Playwright, TEST keyword)
- Neovim configuration helpers
- Subagent visualization
- Text/clear commands
- And many more!

**Important notes**:

- ✅ **Committed to repo as examples** - these are real patterns I use
- ✅ **Non-sensitive only** - sensitive snippets are in `commands/warren/sensitive/` (gitignored)
- ✅ **Ready to use** - browse and learn from 20+ real-world examples
- ✅ **References personal directory** - points to `commands/warren/` for snippet files
- ✅ **Easy to customize** - modify patterns or content to fit your workflow

**To use these examples**:

1. Browse `scripts/config.local.json` to see available patterns
2. Check `commands/warren/` for the actual snippet files
3. Use the snippets as-is, or customize them to your needs
4. Add your own sensitive snippets in `commands/warren/sensitive/` (automatically gitignored)

**To customize**:

```bash
# View examples
cd scripts/
cat config.local.json

# Edit existing snippets
vim config.local.json

# Add your own in the sensitive directory (gitignored)
mkdir -p ../commands/warren/sensitive
vim ../commands/warren/sensitive/my-private-snippet.md
```

### Direct Config Editing

For base/shared snippets, edit `scripts/config.json`:

```json
{
  "mappings": [
    {
      "name": "custom",
      "pattern": "\\b(custom|pattern|here)\\b",
      "snippet": ["snippets/custom.md"],
      "enabled": true,
      "separator": "\n"
    }
  ]
}
```

For personal snippets, edit `scripts/config.local.json` (gitignored).

### Creating Snippets Manually

1. Create file: `scripts/snippets/mysnippet.md`
2. Add to `config.local.json` (for personal) or `config.json` (for shared)
3. Reload Claude Code

### Python CLI Tool

Direct CLI usage:

```bash
cd ~/.claude/plugins/claude-code-snippets/scripts

# Create
python3 snippets_cli.py create mysnippet \
  --pattern '\b(my|snippet)\b' \
  --content "Your content here"

# List
python3 snippets_cli.py list --show-stats

# Update
python3 snippets_cli.py update mysnippet \
  --pattern '\b(new|pattern)\b'

# Delete
python3 snippets_cli.py delete mysnippet --backup

# Test pattern
python3 snippets_cli.py test mysnippet "test text with my keyword"

# Validate
python3 snippets_cli.py validate
```

## Tips & Best Practices

1. **Use verification hashes** to test that snippets are actually injecting
2. **Start with broad patterns** then refine if getting too many matches
3. **Use word boundaries** (`\b`) to avoid partial word matches
4. **Group related content** into multi-file snippets with clear separators
5. **Disable rather than delete** snippets you might want later
6. **Test patterns** before creating snippets: `/snippets/test-pattern`
