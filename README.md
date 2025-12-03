# Warren Claude Code Plugin Marketplace

A personal plugin marketplace for Claude Code.

## Available Plugins

| Plugin | Description |
|--------|-------------|
| **claude-context-orchestrator** | Hybrid context management with Agent Skills + snippets |
| **spending-tracker** | Track Claude Code API spending |
| **gmail-plugin** | Gmail CLI integration (`/gmail`, `/gmail:setup`) |
| **gcal-plugin** | Google Calendar CLI integration (`/gcal`, `/gcal:setup`) |

## Installation

### Add the Marketplace

```bash
/plugin marketplace add WarrenZhu050413/Warren-Claude-Code-Plugin-Marketplace
```

### Install Plugins

```bash
/plugin install claude-context-orchestrator@warren-claude-code-plugin-marketplace
/plugin install spending-tracker@warren-claude-code-plugin-marketplace
/plugin install gmail-plugin@warren-claude-code-plugin-marketplace
/plugin install gcal-plugin@warren-claude-code-plugin-marketplace
```

## Gmail Setup

1. Install plugin: `/plugin install gmail-plugin@warren-claude-code-plugin-marketplace`
2. Install CLI:
   ```bash
   cd gmail-integration-plugin/scripts/gmaillm
   make install
   ```
3. Run `/gmail:setup` to configure OAuth

## Google Calendar Setup

1. Install plugin: `/plugin install gcal-plugin@warren-claude-code-plugin-marketplace`
2. Install CLI: `uv tool install gcallm`
3. Run `/gcal:setup` to configure OAuth

## Structure

```
warren-claude-code-plugin-marketplace/
├── claude-context-orchestrator/   # Skills & snippets
├── spending-tracker-plugin/       # Spending tracking
├── gmail-plugin/                  # Gmail commands
├── gcal-plugin/                   # Calendar commands
└── gmail-integration-plugin/      # gmaillm CLI source
```

## Owner

Maintained by Fucheng Warren Zhu (wzhu@college.harvard.edu)
