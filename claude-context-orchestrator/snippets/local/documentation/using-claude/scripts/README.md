# Using Claude - Working Scripts

This directory contains executable example scripts demonstrating various Claude Code patterns.

## Available Scripts

### 1. Headless Automation (`headless-example.sh`)

Demonstrates headless automation patterns for CI/CD, batch processing, and scripted workflows.

**Usage:**
```bash
# Interactive mode
./headless-example.sh

# Run specific example
./headless-example.sh 1

# Run all examples
./headless-example.sh all
```

**Examples included:**
- Simple one-shot commands
- Structured JSON output
- Session continuation
- Headless automation with permissions
- Read-only analysis
- Batch processing
- CI/CD code review
- Cost monitoring
- Debug mode analysis
- Model selection

---

### 2. Python SDK Examples (`sdk-python-example.py`)

Comprehensive examples of the Claude Agent SDK in Python.

**Prerequisites:**
```bash
pip install claude-agent-sdk
```

**Usage:**
```bash
# Interactive mode
python3 sdk-python-example.py

# Run specific example
python3 sdk-python-example.py 1

# Run all examples
python3 sdk-python-example.py all
```

**Examples included:**
- Simple one-off query
- Continuous conversation
- Custom tools with MCP
- Model selection (Haiku/Sonnet/Opus)
- Session management (resume/fork)
- Programmatic subagents
- Error handling and cost monitoring

---

### 3. TypeScript SDK Examples (`sdk-typescript-example.ts`)

Comprehensive examples of the Claude Agent SDK in TypeScript.

**Prerequisites:**
```bash
npm install @anthropic-ai/claude-agent-sdk zod
```

**Usage:**
```bash
# Run specific example
npx ts-node sdk-typescript-example.ts 1

# Run all examples
npx ts-node sdk-typescript-example.ts all
```

**Examples included:**
- Simple one-off query
- Continuous conversation
- Custom tools with MCP
- Model selection (Haiku/Sonnet/Opus)
- Session management (resume/fork)
- Programmatic subagents
- Error handling and cost monitoring

---

### 4. MCP Server Management (`mcp-commands.sh`)

Demonstrates MCP server configuration and management operations.

**Usage:**
```bash
# Interactive mode
./mcp-commands.sh

# Run specific example
./mcp-commands.sh 1

# Run all examples
./mcp-commands.sh all
```

**Examples included:**
- List all MCP servers
- Add simple MCP server (Playwright)
- Add MCP server with JSON config
- Add Exa (web search) MCP
- Add filesystem MCP
- Get server details
- Remove MCP server
- Complete Playwright setup with config file
- Import from Claude Desktop
- Reset project choices
- Check MCP server connection status

---

## Quick Start

### Test Headless Automation
```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/using-claude/scripts
./headless-example.sh 1
```

### Test Python SDK
```bash
python3 sdk-python-example.py 1
```

### Test MCP Management
```bash
./mcp-commands.sh 1
```

---

## Environment Variables

Some examples may require environment variables:

**Anthropic API Key:**
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

**Exa API Key (for web search):**
```bash
export EXA_API_KEY="your-exa-api-key"
```

**Model Selection:**
```bash
export CLAUDE_MODEL="sonnet"  # or "haiku", "opus"
```

---

## Tips

1. **Start with simple examples first** (example 1 in each script)
2. **Read the code** - Each example is heavily commented
3. **Modify and experiment** - These are learning tools
4. **Check costs** - All examples show token usage and costs
5. **Use debug mode** - Add `--debug` to see what's happening

---

## Troubleshooting

**Script not executable:**
```bash
chmod +x script-name.sh
```

**Python dependencies missing:**
```bash
pip install claude-agent-sdk
```

**TypeScript dependencies missing:**
```bash
npm install @anthropic-ai/claude-agent-sdk zod
npm install -g ts-node typescript
```

**API key not set:**
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

---

## Related Documentation

- **[Headless Patterns](../reference/headless-patterns.md)** - Complete headless automation guide
- **[Agent SDK Patterns](../reference/agent-sdk-patterns.md)** - Complete SDK documentation
- **[MCP Configuration](../reference/mcp-configuration.md)** - MCP server setup guide
- **[Debugging Guide](../reference/debugging-guide.md)** - Testing and debugging help

---

**Last Updated:** 2025-10-26
