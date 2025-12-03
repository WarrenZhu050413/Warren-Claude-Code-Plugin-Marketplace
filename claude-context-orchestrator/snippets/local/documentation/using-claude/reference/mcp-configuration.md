# MCP Server Configuration

Comprehensive guide for configuring and managing Model Context Protocol (MCP) servers in Claude Code.

---

## Overview

MCP (Model Context Protocol) servers extend Claude Code's capabilities by providing additional tools and context. This guide covers how to configure MCP servers using the `claude mcp` CLI.

---

## Claude MCP CLI Commands

### Available Commands

```bash
claude mcp [options] [command]

Commands:
  serve                                      Start the Claude Code MCP server
  add <name> <commandOrUrl> [args...]       Add an MCP server
  remove <name>                             Remove an MCP server
  list                                       List configured MCP servers
  get <name>                                Get details about an MCP server
  add-json <name> <json>                    Add MCP server with JSON configuration
  add-from-claude-desktop                   Import from Claude Desktop (Mac/WSL)
  reset-project-choices                     Reset project-scoped server approvals
  help [command]                            Display help for command
```

### Getting Help

```bash
# General help
claude mcp --help

# Command-specific help
claude mcp add --help
claude mcp add-json --help
claude mcp remove --help
```

---

## Adding MCP Servers

### Method 1: Simple Add (for stdio servers)

```bash
claude mcp add <server-name> <command> [args...] -s <scope>
```

**Example: Playwright MCP**
```bash
claude mcp add playwright npx @playwright/mcp@latest -s local
```

**Scope Options:**
- `-s local` - Project-specific (stored in `.claude.json` in project root)
- `-s global` - User-wide (stored in `~/.claude.json`)

### Method 2: JSON Configuration (for complex setups)

```bash
claude mcp add-json <name> '<json-config>' -s <scope>
```

**JSON Configuration Structure:**
```json
{
  "command": "npx",
  "args": ["@playwright/mcp@latest", "--option1", "value1"],
  "env": {
    "ENV_VAR": "value"
  }
}
```

**Example: Playwright with Extension Support**
```bash
claude mcp add-json playwright '{
  "command": "npx",
  "args": [
    "@playwright/mcp@latest",
    "--extension"
  ],
  "env": {
    "PLAYWRIGHT_MCP_EXTENSION_TOKEN": "your-token-here"
  }
}' -s local
```

**Example: Playwright with Config File**
```bash
claude mcp add-json playwright '{
  "command": "npx",
  "args": [
    "@playwright/mcp@latest",
    "--config",
    "/absolute/path/to/playwright-mcp.config.json"
  ],
  "env": {
    "PLAYWRIGHT_MCP_EXTENSION_TOKEN": "your-token-here"
  }
}' -s local
```

### Method 3: Add from Claude Desktop

```bash
claude mcp add-from-claude-desktop
```

This imports all MCP servers from your Claude Desktop configuration (Mac and WSL only).

---

## Managing MCP Servers

### List All Servers

```bash
claude mcp list
```

**Output shows:**
- Server name
- Connection status (✓ Connected / ✗ Disconnected)
- Type (stdio, HTTP)
- Command and args (for stdio)
- URL (for HTTP)

### Get Server Details

```bash
claude mcp get <server-name>
```

**Shows:**
- Scope (local/global)
- Status
- Type
- Full configuration (command, args, environment variables)
- Removal command

### Remove Server

```bash
claude mcp remove <server-name> -s <scope>
```

**Examples:**
```bash
# Remove local server
claude mcp remove playwright -s local

# Remove global server
claude mcp remove exa -s global
```

---

## Common MCP Servers

### Playwright MCP

**Basic setup:**
```bash
claude mcp add playwright npx @playwright/mcp@latest --extension -s local
```

**With config file:**
```bash
claude mcp add-json playwright '{
  "command": "npx",
  "args": [
    "@playwright/mcp@latest",
    "--config",
    "'$(pwd)'/playwright-mcp.config.json"
  ],
  "env": {
    "PLAYWRIGHT_MCP_EXTENSION_TOKEN": "your-token"
  }
}' -s local
```

**Playwright config file structure** (`playwright-mcp.config.json`):
```json
{
  "browser": "chrome",
  "launchOptions": {
    "channel": "chrome",
    "headless": false,
    "args": [
      "--disable-extensions-except=/path/to/extension/dist",
      "--load-extension=/path/to/extension/dist"
    ]
  }
}
```

### Exa (Web Search)

```bash
claude mcp add exa "https://mcp.exa.ai/mcp?exaApiKey=YOUR_API_KEY" -s global
```

### File System MCP

```bash
claude mcp add filesystem npx @modelcontextprotocol/server-filesystem /path/to/allowed/directory -s local
```

### Database MCP (PostgreSQL)

```bash
claude mcp add postgres npx @modelcontextprotocol/server-postgres postgresql://user:pass@localhost/db -s local
```

---

## Configuration Files

### Local Configuration (`.claude.json`)

Located in project root. Example:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--extension"],
      "env": {
        "PLAYWRIGHT_MCP_EXTENSION_TOKEN": "token"
      }
    }
  }
}
```

### Global Configuration (`~/.claude.json`)

Located in home directory. Same structure as local config.

**Precedence:** Local config overrides global config.

---

## Environment Variables

MCP servers can use environment variables:

```bash
claude mcp add-json myserver '{
  "command": "node",
  "args": ["server.js"],
  "env": {
    "API_KEY": "secret-key",
    "DEBUG": "true",
    "PORT": "3000"
  }
}' -s local
```

---

## Troubleshooting

### Check Connection Status

```bash
claude mcp list
```

Look for ✓ Connected or ✗ Disconnected status.

### View Server Logs

MCP servers output to stderr. To see logs:

1. Check Claude Code terminal output
2. Look for `[MCP:server-name]` prefixed messages

### Common Issues

**Server won't connect:**
- Verify command/path is correct
- Check environment variables are set
- Ensure dependencies are installed (e.g., `npm install`)

**Server disconnects:**
- Check for errors in Claude Code terminal
- Verify server process isn't crashing
- Review server-specific documentation

**Permission issues:**
- Ensure file permissions are correct
- For local servers, check `.claude.json` is writable
- For global servers, check `~/.claude.json` is writable

### Reset Project Choices

If you've approved/rejected project-scoped servers:

```bash
claude mcp reset-project-choices
```

This clears all stored choices for the current project.

---

## MCP Server Best Practices

1. **Use local scope for project-specific servers** - Keeps project dependencies isolated
2. **Use global scope for general-purpose servers** - Exa, filesystem access, etc.
3. **Version lock MCP packages** - Use specific versions instead of `@latest` for stability
4. **Document environment variables** - Include `.env.example` in projects
5. **Test connection after adding** - Run `claude mcp list` to verify ✓ Connected status
6. **Keep tokens secure** - Don't commit tokens to git, use environment variables

---

## Example: Complete Playwright Setup

**Step 1: Create config file**
```bash
cat > playwright-mcp.config.json << 'EOF'
{
  "browser": "chrome",
  "launchOptions": {
    "channel": "chrome",
    "headless": false,
    "args": [
      "--disable-extensions-except=$(pwd)/dist",
      "--load-extension=$(pwd)/dist"
    ]
  }
}
EOF
```

**Step 2: Add MCP server**
```bash
claude mcp add-json playwright "{
  \"command\": \"npx\",
  \"args\": [
    \"@playwright/mcp@latest\",
    \"--config\",
    \"$(pwd)/playwright-mcp.config.json\"
  ],
  \"env\": {
    \"PLAYWRIGHT_MCP_EXTENSION_TOKEN\": \"your-token-here\"
  }
}" -s local
```

**Step 3: Verify**
```bash
claude mcp list
# Should show: playwright: ... - ✓ Connected

claude mcp get playwright
# Shows full configuration details
```

---

## MCP Server Documentation

For server-specific documentation:

- **Playwright MCP**: https://github.com/microsoft/playwright-mcp
- **MCP Specification**: https://modelcontextprotocol.io/
- **Official MCP Servers**: https://github.com/modelcontextprotocol/servers
- **Claude Code Docs**: https://docs.claude.com/en/docs/claude-code/

---

## Quick Reference

```bash
# Add server (simple)
claude mcp add <name> <command> [args...] -s local

# Add server (JSON)
claude mcp add-json <name> '<json>' -s local

# List servers
claude mcp list

# Get server info
claude mcp get <name>

# Remove server
claude mcp remove <name> -s local

# Import from Claude Desktop
claude mcp add-from-claude-desktop

# Get help
claude mcp --help
claude mcp <command> --help
```
