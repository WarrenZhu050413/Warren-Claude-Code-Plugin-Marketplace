# Claude Code Snippets Plugin - Documentation

Complete documentation for the Claude Code Snippets Plugin.

## Quick Links

- 🚀 **[Getting Started](getting-started.md)** - Installation, first test, and basic usage
- 📦 **[Installation Guide](installation.md)** - Detailed setup instructions
- ⚡ **[Quick Start](quickstart.md)** - Get running in minutes
- 📋 **[Commands Reference](commands-reference.md)** - Complete command documentation
- ⚙️ **[Configuration](configuration.md)** - Configuration system and snippet structure
- 🎨 **[Template Pattern](template-pattern.md)** - Advanced template-based snippets
- 🔧 **[Multi-Config Guide](multi-config-guide.md)** - Managing multiple configurations
- 🛠️ **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

---

## Overview

The Claude Code Snippets Plugin automatically injects contextual snippets into your prompts using regex pattern matching. This provides Claude with relevant context, guidelines, and information based on keywords in your prompts.

### Key Features

- **🎯 Regex Pattern Matching**: Automatically inject snippets based on keywords anywhere in your prompt
- **📢 Usage Announcements**: Transparent notifications showing which snippets are active
- **🎨 Template Pattern**: Advanced system for complex snippets with external templates
- **🔧 CRUD Commands**: Full management via `/claude-code-snippets:*` commands
- **📚 20+ Examples**: Included example snippets for common workflows
- **🔄 Layered Config**: Base config + local config with override support

---

## Documentation Structure

### For Beginners

Start here if you're new to the plugin:

1. **[Getting Started](getting-started.md)**
   - Installation and setup
   - Your first test
   - Creating your first snippet
   - Understanding patterns
   - Snippet usage announcements

### Core Documentation

Essential reading for all users:

2. **[Commands Reference](commands-reference.md)**
   - `/create-snippet` - Create new snippets
   - `/read-snippets` - List and view snippets
   - `/update-snippet` - Modify existing snippets
   - `/delete-snippet` - Remove snippets
   - CLI tool usage

3. **[Configuration](configuration.md)**
   - Configuration system (base + local)
   - Config file structure
   - Snippet file structure
   - Pattern syntax and examples
   - Advanced configuration

### Advanced Topics

For power users and complex use cases:

4. **[Template Pattern](template-pattern.md)**
   - What is the template pattern?
   - Architecture and structure
   - Real-world example (HTML snippet)
   - Creating template-based snippets
   - Best practices and benefits

### Problem Solving

When things go wrong:

5. **[Troubleshooting](troubleshooting.md)**
   - Snippet not injecting
   - Pattern not matching
   - Configuration errors
   - Hook not loading
   - Template pattern issues
   - Debugging tips

---

## Quick Reference

### Installation

```bash
/plugin marketplace add WarrenZhu050413/Warren-Claude-Code-Plugin-Marketplace
/plugin install claude-code-snippets@warren-claude-code-plugin-marketplace
```

### Test the Plugin

```
HTML Explain Claude Code Marketplace
```

### Create a Snippet

```bash
/claude-code-snippets:create-snippet docker
```

### List Snippets

```bash
/claude-code-snippets:read-snippets
```

### Update a Snippet

```bash
/claude-code-snippets:update-snippet docker
```

### Delete a Snippet

```bash
/claude-code-snippets:delete-snippet docker
```

---

## How It Works

### The Hook System

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

### Pattern Matching

- All patterns are **regex** (regular expressions)
- Matching is **case-insensitive**
- Patterns can match **anywhere** in your prompt
- Multiple snippets can match the same prompt

### Usage Announcements

All snippets automatically announce when they're active:

**Single snippet:**
```
📎 **Active Context**: HTML
```

**Multiple snippets:**
```
📎 **Active Contexts**: HTML, docker
```

This appears at the very beginning of Claude's response, providing transparency.

---

## Common Use Cases

### 1. Domain-Specific Knowledge

Create snippets for specialized domains:
- Medical terminology and guidelines
- Legal citation formats
- Scientific notation standards
- Industry-specific best practices

**Example:**
```bash
/claude-code-snippets:create-snippet medical
# Pattern: medical, diagnosis, treatment
# Content: Medical terminology, HIPAA guidelines, etc.
```

### 2. Project Context

Inject project-specific information:
- Architecture overview
- Coding conventions
- API endpoints
- Database schema

**Example:**
```bash
/claude-code-snippets:create-snippet myproject
# Pattern: project, codebase, architecture
# Content: Project structure, conventions, etc.
```

### 3. Workflow Automation

Automate common workflows:
- Email templates and tone guidelines
- Calendar formatting standards
- Search optimization tactics
- Testing patterns

**Example:**
```bash
/claude-code-snippets:create-snippet email
# Pattern: email, mail, gmail
# Content: Email templates, tone guidelines, etc.
```

### 4. Tool Integration

Provide context for external tools:
- Docker commands and best practices
- Git workflows
- Database queries
- API documentation

**Example:**
```bash
/claude-code-snippets:create-snippet docker
# Pattern: docker, container, dockerfile
# Content: Docker commands, best practices, etc.
```

### 5. Output Formatting

Control output formats:
- HTML with CSS styling
- Markdown with specific formatting
- JSON structures
- Plain text templates

**Example:**
```
HTML Explain something
```
Claude generates a beautifully formatted HTML file with styling.

---

## Directory Structure

```
claude-code-snippets-plugin/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   ├── create-snippet.md        # /create-snippet command
│   ├── read-snippets.md         # /read-snippets command
│   ├── update-snippet.md        # /update-snippet command
│   └── delete-snippet.md        # /delete-snippet command
├── docs/
│   ├── INDEX.md                 # This file (documentation index)
│   ├── getting-started.md       # Beginner guide
│   ├── commands-reference.md    # Command details
│   ├── configuration.md         # Config system
│   ├── template-pattern.md      # Advanced templates
│   └── troubleshooting.md       # Problem solving
├── hooks/
│   └── hooks.json               # Hook configuration
├── scripts/
│   ├── config.json              # Base config (2 snippets)
│   ├── config.local.json        # Local config (20+ examples)
│   ├── snippets_cli.py          # CLI tool
│   ├── snippet_injector.py      # Hook script
│   └── snippets/
│       ├── HTML.md              # HTML snippet
│       └── nvim.md              # Neovim snippet
├── templates/
│   └── html/
│       ├── base-template.html   # HTML template
│       └── examples.md          # HTML examples
└── README.md                    # Quick overview
```

---

## Configuration Files

### Base Config (`scripts/config.json`)
- 2 basic snippets (HTML, nvim)
- Shared across all users
- Simple examples

### Local Config (`scripts/config.local.json`)
- 20+ example snippets
- Personal customizations
- Overrides base config

### Merge Behavior
- Both configs are loaded
- If same snippet name: local wins
- Otherwise: combined

---

## Example Snippets Included

The plugin includes 20+ example snippets in `config.local.json`:

- **Communication**: Email, Gmail, Google Calendar
- **Development**: Docker, HTML, Neovim, TDD
- **Testing**: Playwright, TEST keyword
- **Utilities**: Search, Clear, Text output
- **Visualization**: Subagent visualization
- **And many more!**

Browse `scripts/config.local.json` to see all available examples.

---

## Pattern Examples

### Exact Word
```json
"pattern": "\\bHTML\\b"
```
Matches: `HTML`, `html`, `HtMl`

### Multiple Keywords
```json
"pattern": "\\b(docker|container|dockerfile)\\b"
```
Matches: `docker`, `container`, `dockerfile`

### Phrase with Optional Spaces
```json
"pattern": "\\b(google\\s*calendar|gcal)\\b"
```
Matches: `google calendar`, `googlecalendar`, `gcal`

See **[Configuration](configuration.md)** for complete pattern syntax guide.

---

## Best Practices

1. **Use verification hashes** to test snippet injection
2. **Start with broad patterns** then refine if needed
3. **Use word boundaries** (`\b`) to avoid partial matches
4. **Test patterns** before committing:
   ```bash
   python3 scripts/snippets_cli.py test name "test text"
   ```
5. **Enable announcements** for transparency
6. **Create backups** before major changes
7. **Validate configuration** regularly:
   ```bash
   python3 scripts/snippets_cli.py validate
   ```

---

## Support & Resources

### Documentation
- Complete docs in `/docs` directory
- Examples in `scripts/config.local.json`
- Template example: HTML snippet

### Plugin Development
- **[CLAUDE.md](../../CLAUDE.md)** - Plugin development guide
- Marketplace documentation
- Claude Code docs: https://docs.claude.com/

### Community
- Report issues on GitHub
- Share useful snippets
- Contribute improvements

---

## What's Next?

Choose your path:

**New to the plugin?**
→ Start with **[Getting Started](getting-started.md)**

**Want to create snippets?**
→ See **[Commands Reference](commands-reference.md)**

**Need to configure patterns?**
→ Read **[Configuration](configuration.md)**

**Building complex snippets?**
→ Learn **[Template Pattern](template-pattern.md)**

**Having issues?**
→ Check **[Troubleshooting](troubleshooting.md)**

---

**Last Updated:** 2025-10-12
**Plugin Version:** Check `.claude-plugin/plugin.json`
**Author:** Fucheng Warren Zhu

---

## License

MIT License - Feel free to use, customize, and extend!
