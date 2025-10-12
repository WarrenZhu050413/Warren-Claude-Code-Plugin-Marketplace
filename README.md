# Warren Claude Code Plugin Marketplace

A personal plugin marketplace for Claude Code, featuring plugins for snippet injection, spending tracking, and more.

## About

This marketplace contains custom plugins for Claude Code with advanced features like:

- **Snippet injection system** with regex pattern matching
- **Template-based snippets** for complex output formats (HTML, etc.)
- **Spending tracking** for Claude Code API usage
- **Conversation memory** for persistent context

## Available Plugins

### 🎯 Claude Code Snippets Plugin

Automatically inject context snippets into prompts using regex pattern matching. Includes template pattern support for complex outputs.

**Key Features:**
- Regex-based snippet injection
- Template system (base templates + examples)
- Automatic usage announcements
- CRUD commands for snippet management
- 20+ example snippets included

**Example:** The HTML snippet uses a template pattern with `base-template.html` + `examples.md` for rich HTML output.

[Read more →](claude-code-snippets-plugin/README.md)

### 📊 Spending Tracker Plugin

Track your Claude Code API spending with detailed statistics.

[Read more →](spending-tracker-plugin/README.md)

### 💬 Conversation Memory Plugin

Persistent conversation memory across sessions.

[Read more →](conversation-memory-plugin/README.md)

## Installation

### Step 1: Add the Marketplace

```bash
/plugin marketplace add WarrenZhu050413/Warren-Claude-Code-Plugin-Marketplace
```

Or using the full GitHub URL:

```bash
/plugin marketplace add https://github.com/WarrenZhu050413/Warren-Claude-Code-Plugin-Marketplace
```

### Step 2: Install Plugins

```bash
# Install snippets plugin
/plugin install claude-code-snippets@warren-claude-code-plugin-marketplace

# Install spending tracker
/plugin install spending-tracker@warren-claude-code-plugin-marketplace

# Install conversation memory
/plugin install conversation-memory@warren-claude-code-plugin-marketplace
```

## Plugin Development Guide

For comprehensive plugin development documentation including the **template pattern** for complex snippets, see:

**[CLAUDE.md - Plugin Development Guide](CLAUDE.md)**

Key topics covered:
- Plugin structure and manifest
- Command files (slash commands)
- **Snippet files** (context injection)
- **Template pattern** for complex snippets (NEW!)
- Hooks configuration
- Best practices and gotchas
- Testing and publishing

### Template Pattern Example

The marketplace includes a complete implementation of the template pattern in the `claude-code-snippets-plugin`:

```
claude-code-snippets-plugin/
├── snippets/
│   └── HTML.md                    # Instructions for Claude
└── templates/
    └── html/
        ├── base-template.html     # Complete HTML template
        └── examples.md            # Usage examples
```

This pattern separates:
- **Instructions** (snippet file) - What Claude should do
- **Templates** (template files) - Reusable assets
- **Examples** (examples file) - Reference documentation

[See full documentation →](CLAUDE.md#template-pattern-for-complex-snippets)

## Marketplace Structure

```
warren-claude-code-plugin-marketplace/
├── .claude-plugin/
│   └── marketplace.json           # Marketplace manifest
├── CLAUDE.md                      # Plugin development guide
├── claude-code-snippets-plugin/   # Snippet injection system
├── spending-tracker-plugin/       # API spending tracker
├── conversation-memory-plugin/    # Conversation persistence
└── README.md                      # This file
```

The `.claude-plugin/marketplace.json` file defines all available plugins.

## Resources

- [Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference.md)
- [Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md)
- [Plugins Overview](https://docs.claude.com/en/docs/claude-code/plugins.md)
- [Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks.md)

## Owner

Maintained by Fucheng Warren Zhu (wzhu@college.harvard.edu)

## License

MIT License - Feel free to use, customize, and contribute!
