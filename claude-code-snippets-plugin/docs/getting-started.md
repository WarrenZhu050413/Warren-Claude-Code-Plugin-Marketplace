# Getting Started

This guide will help you get up and running with the Claude Code Snippets Plugin.

## Quick Start

### Installation

The plugin is already installed if you followed the marketplace installation steps. If not:

```bash
/plugin marketplace add WarrenZhu050413/Warren-Claude-Code-Plugin-Marketplace
/plugin install claude-code-snippets@warren-claude-code-plugin-marketplace
```

### Your First Test

Try this command to test the HTML snippet:

```
HTML Explain Claude Code Marketplace
```

You should see:
1. Claude announces: `📎 **Active Context**: HTML`
2. An HTML file is created in `claude_html/` directory
3. The file opens automatically in your browser

### How It Works

The plugin uses a **hook** that intercepts every prompt you send and checks for pattern matches:

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

## Creating Your First Snippet

### Method 1: Using the Command (Recommended)

```bash
/claude-code-snippets:create-snippet docker

# Follow the interactive prompts:
# 1. Pattern keywords: docker, container, dockerfile
# 2. Content: [paste your Docker cheat sheet]
# 3. Automated tests run automatically
# 4. Full snippet content displayed
```

### Method 2: Manual Creation

1. **Create the snippet file**:
   ```bash
   cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts
   vim snippets/docker.md
   ```

2. **Add content**:
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

   **VERIFICATION_HASH:** `abc123def456`

   ## Docker Commands

   [Your Docker cheat sheet content here...]
   ```

3. **Configure the snippet**:
   ```bash
   vim config.json
   ```

   Add:
   ```json
   {
     "mappings": [
       {
         "name": "docker",
         "pattern": "\\b(docker|container|dockerfile)\\b",
         "snippet": ["snippets/docker.md"],
         "enabled": true
       }
     ]
   }
   ```

4. **Test the snippet**:
   ```bash
   python3 snippets_cli.py test docker "I need help with docker"
   ```

## Understanding Patterns

The `pattern` field uses **regex** (regular expressions):

### Common Patterns

```javascript
// Match exact word (case-insensitive)
"\\bHTML\\b"
// Matches: "HTML", "html", "HtMl"
// Doesn't match: "htmlparse", "inHTML"

// Match multiple alternatives
"\\b(docker|container|dockerfile)\\b"
// Matches any of: "docker", "container", "dockerfile"

// Match phrases with optional spaces
"\\b(google\\s*calendar|gcal)\\b"
// Matches: "google calendar", "googlecalendar", "gcal"

// All patterns are case-insensitive by default
```

### Testing Patterns

Before creating a snippet, test your pattern:

```bash
cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts
python3 snippets_cli.py test mysnippet "your test text here"
```

## Snippet Usage Announcements

All snippets automatically announce when they're active:

### Single Snippet
```
You: "Help me with HTML"

Claude: 📎 **Active Context**: HTML

[Response with HTML context...]
```

### Multiple Snippets
```
You: "Help me with HTML and docker"

Claude: 📎 **Active Contexts**: HTML, docker

[Response with both HTML and docker context...]
```

This provides **transparency** so you always know which context is being injected.

## Available Commands

All commands are prefixed with the plugin name:

### `/claude-code-snippets:create-snippet`
Create a new snippet with interactive guidance.

```bash
/claude-code-snippets:create-snippet docker
```

### `/claude-code-snippets:read-snippets`
List all configured snippets.

```bash
# List all snippets
/claude-code-snippets:read-snippets

# Show specific snippet
/claude-code-snippets:read-snippets docker
```

### `/claude-code-snippets:update-snippet`
Update an existing snippet's pattern or content.

```bash
/claude-code-snippets:update-snippet docker
```

### `/claude-code-snippets:delete-snippet`
Delete a snippet (creates backup by default).

```bash
/claude-code-snippets:delete-snippet docker
```

See [Commands Reference](commands-reference.md) for detailed documentation.

## Example Snippets Included

The plugin includes **20+ example snippets** in `config.local.json`:

- Email/Gmail automation
- Google Calendar helpers
- Search optimization
- HTML formatting
- Code testing (Playwright, TEST)
- Neovim configuration
- And many more!

Browse `scripts/config.local.json` to see what's available.

## Next Steps

- **[Configuration](configuration.md)** - Learn about the configuration system
- **[Template Pattern](template-pattern.md)** - Create advanced snippets with templates
- **[Commands Reference](commands-reference.md)** - Detailed command documentation
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## Tips for Beginners

1. **Start simple**: Create a basic snippet with a simple pattern first
2. **Test patterns**: Always test your regex patterns before committing
3. **Use verification hashes**: Add `VERIFICATION_HASH` to verify injection works
4. **Start with examples**: Study the included example snippets in `config.local.json`
5. **Use commands**: The `/create-snippet` command is easier than manual creation
6. **Enable announcements**: Keep `ANNOUNCE_USAGE: true` for transparency
