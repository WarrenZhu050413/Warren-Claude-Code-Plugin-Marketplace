# Claude Code Snippets Plugin

A Claude Code plugin that automatically injects context snippets into your prompts using regex pattern matching anywhere in your input, from any file!

It has been tremendously helpful for me to provide different context to my agents in a composable way. I hope it is also helpful for you :).

## What Does This Do?

This plugin uses a **hook** that listens to all your prompts and automatically injects relevant context when it detects certain keywords. For example:

- Type "Can you help me with HTML?" → Automatically injects HTML formatting guidelines
- Type "I need docker help" → Automatically injects your Docker cheat sheet
- Type "Check this search query" → Automatically injects search optimization tactics

The magic happens through **regex pattern matching anywhere in your prompt** - not just slash commands at the start!

## Features

- **Regex-based injection**: Match patterns anywhere in your prompt, not just at the beginning
- **CRUD commands**: Create, read, update, and delete snippets via slash commands
- **Multi-file snippets**: Combine multiple files into one snippet
- **Verification hashes**: Test that snippets are actually being injected
- **Enable/disable**: Toggle snippets on/off without deleting them
- **Automatic hook**: No manual work needed - just type naturally!

## Installation

### Step 1: Copy Plugin to Claude Code Directory

```bash
# Clone or copy the plugin to your Claude Code plugins directory
cp -r claude-code-snippets-plugin ~/.claude/plugins/claude-code-snippets
```

### Step 2: Enable the Plugin

Use Claude Code's plugin system to enable:

```bash
claude
# Then in Claude:
/plugin enable claude-code-snippets
```

Or manually enable by adding to your Claude Code config.

### Step 3: Verify Installation

Test that the hook is working:

```bash
claude -p "Can you help me with HTML?"
```

If you see HTML formatting instructions automatically included in the context, it's working!

## Quick Start

### Testing the Example HTML Snippet

The plugin comes with one example snippet already configured. Test it:

```bash
# This should automatically inject HTML instructions
claude -p "Create a simple HTML page for me"

# You should see the verification hash in the response:
# Look for: "VERIFICATION_HASH: a1b2c3d4e5f6g7h8"
```

If you see that verification hash mentioned, **the snippet was successfully injected!** 🎉

### Creating Your First Custom Snippet

```bash
claude
# Then use the create-snippet command:
/claude-code-snippets:create-snippet docker

# Follow the prompts to:
# 1. Set pattern keywords (e.g., "docker, container, dockerfile")
# 2. Provide content (paste directly or load from file)
# 3. Automated tests run and display results
# 4. Full snippet content shown for verification
```

### Viewing All Snippets

```bash
claude
/claude-code-snippets:read-snippets
```

### Testing Pattern Matching

After creating a snippet, test it:

```bash
# Try using the keyword in your prompt
claude -p "I need help with docker containers"

# The snippet should automatically inject!
```

## Configuration

### Configuration Files

The plugin uses a **layered configuration system** in `scripts/`:

- **config.json**: Base configuration (committed to git, shared with all users)
- **config.local.json**: Your personal configuration (gitignored, private to you)
- **snippets/\*.md**: Your actual snippet content files

### Layered Configuration System

The plugin loads both configuration files and **merges them intelligently**:

1. **Base config (`config.json`)**:
   - Committed to git
   - Contains example/shared snippets
   - Updated by plugin maintainer

2. **Local config (`config.local.json`)**:
   - **Gitignored** - never committed
   - Your personal snippets
   - **Overrides base config** by snippet name

3. **Merge behavior**:
   - If a snippet name exists in both configs, **local wins**
   - Otherwise, snippets from both configs are combined
   - Result: You get base examples + your personal snippets

**Example**:

```json
// config.json (base - 1 snippet)
{
  "mappings": [
    {
      "name": "HTML",
      "pattern": "\\bHTML\\b\\.?",
      "snippet": ["snippets/HTML.md"],
      "enabled": true
    }
  ]
}

// config.local.json (your personal - overrides HTML, adds 21 more)
{
  "mappings": [
    {
      "name": "HTML",
      "pattern": "\\bHTML\\b\\.?",
      "snippet": ["snippets/HTML.md"],  // Your custom HTML snippet
      "enabled": true
    },
    {
      "name": "docker",
      "pattern": "\\b(docker|container)\\b",
      "snippet": ["snippets/docker.md"],
      "enabled": true
    }
    // ... 20 more personal snippets
  ]
}

// Result: 22 snippets loaded (your HTML overrides base HTML)
```

### Config Structure

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

### Pattern Examples

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
│   └── warren/                  # Personal snippets (gitignored)
│       └── *.md
├── hooks/
│   └── hooks.json               # Hook configuration
├── scripts/
│   ├── config.json              # Base configuration (committed)
│   ├── config.local.json        # Personal configuration (gitignored)
│   ├── snippets_cli.py          # CLI tool for CRUD operations
│   ├── snippet_injector.py      # Hook script (runs automatically)
│   └── snippets/
│       └── HTML.md              # Example snippet
├── tests/
│   ├── shared/                  # Shared test files
│   └── warren/                  # Personal tests (gitignored)
├── .gitignore                   # Excludes personal files
└── README.md                    # This file
```

**Gitignored directories** (personal, never committed):
- `commands/warren/` - Your personal snippet files
- `tests/warren/` - Your personal test files
- `scripts/config.local.json` - Your personal snippet configuration

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

### Configuration Files

The plugin includes an **example `config.local.json`** with useful, non-sensitive commands I personally find helpful:

**Included example snippets**:
- Email/Gmail automation context
- Google Calendar helpers
- Search optimization tactics
- HTML formatting guidelines
- Code testing patterns (Playwright, TEST keyword)
- Neovim configuration helpers
- Subagent visualization
- Text/clear commands
- And many more!

**Note**: These are **real snippets I use** that don't expose sensitive information. They're committed to the repo as examples you can learn from or use directly.

**To customize**:
```bash
# Edit the config directly
cd scripts/
vim config.local.json

# Or copy and modify
cp config.local.json config.my-custom.json
```

**Why publish config.local.json?**
- ✅ Shows real-world usage patterns
- ✅ Ready to use out of the box with 20+ snippets
- ✅ You can see how I organize my snippets
- ✅ Easy to customize for your workflow
- ✅ Sensitive snippets are kept separate (gitignored)

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

## Support & Contributing

- **Issues**: Report bugs or request features via GitHub issues
- **Documentation**: Claude Code plugin docs at https://docs.claude.com/en/docs/claude-code/plugins.md
- **Custom snippets**: Share your useful snippets with the community!

## License

MIT License - Feel free to customize and extend!
