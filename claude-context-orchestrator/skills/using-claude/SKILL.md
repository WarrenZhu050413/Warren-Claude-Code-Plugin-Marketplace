---
name: using-claude
description: Working with Claude Code features, debugging hooks, MCP integration, snippet verification, headless automation, and Agent SDK. Use this skill when the user asks about Claude Code features, hooks, memory, statusline, debugging, MCP servers, headless use patterns, CI/CD automation, Python/TypeScript Agent SDK, or building custom agents.
---

# Using Claude

## Purpose

This skill provides comprehensive guidance for working with Claude Code features, including:
- Accessing official Claude Code documentation
- Debugging hooks, plugins, and snippets
- Configuring and managing MCP (Model Context Protocol) servers
- Verifying snippet injection and functionality
- **Headless use patterns** - Automation, CI/CD, batch processing
- **Agent SDK patterns** - Building custom agents in Python and TypeScript

## When to Use

- User asks about Claude Code features (hooks, memory, statusline, commands, snippets, Agent SDK)
- Need to debug Claude Code hooks or plugins
- Working with MCP server configuration (Playwright, Exa, filesystem, etc.)
- Verifying snippet functionality and verification hashes
- Testing modifications to Claude Code configurations
- Accessing the latest Claude Code documentation
- **Headless automation** - CI/CD, batch processing, scripted workflows
- **Agent SDK** - Building custom agents, programmatic access, tool creation

---

# Documentation Access

## Fetch Documentation Directly

When the user mentions Claude Code features, hooks, memory, statusline, or Agent SDK, **ALWAYS fetch the latest documentation directly using curl** instead of relying on training data.

## Available Documentation URLs

### Claude Code Features

**1. Hooks System** - User prompt hooks, file artifacts hooks, custom integrations
```bash
curl -s https://docs.claude.com/en/docs/claude-code/hooks.md
```

**2. Memory System** - Memory management, memory blocks, memory context
```bash
curl -s https://docs.claude.com/en/docs/claude-code/memory.md
```

**3. Statusline Configuration** - Custom statusline setup, formatting, configuration
```bash
curl -s https://docs.claude.com/en/docs/claude-code/statusline.md
```

**4. Snippets System** - Snippet management, pattern matching, injection
```bash
curl -s https://docs.claude.com/en/docs/claude-code/snippets.md
```

**5. Commands** - Slash commands, custom commands, command system
```bash
curl -s https://docs.claude.com/en/docs/claude-code/commands.md
```

**6. Quick Start Guide** - Getting started with Claude Code
```bash
curl -s https://docs.claude.com/en/docs/claude-code/quickstart.md
```

**7. Configuration** - General Claude Code configuration
```bash
curl -s https://docs.claude.com/en/docs/claude-code/configuration.md
```

### Agent SDK

**8. TypeScript Agent SDK** - Building agents with TypeScript/JavaScript
```bash
curl -s https://docs.claude.com/en/api/agent-sdk/typescript.md
```

**9. Python Agent SDK** - Building agents with Python
```bash
curl -s https://docs.claude.com/en/api/agent-sdk/python.md
```

**10. Agent SDK Overview** - General agent concepts
```bash
curl -s https://docs.claude.com/en/api/agent-sdk/overview.md
```

## Usage Pattern

When user asks about any of these topics:

1. **Identify the relevant documentation URL(s)**
2. **Fetch using curl** - Use the Bash tool with the curl command
3. **Read and apply** - Parse the markdown and provide accurate answers based on the fetched content

### Example Workflow

```
User: "How do I create a user prompt submit hook?"

You should:
1. Fetch: curl -s https://docs.claude.com/en/docs/claude-code/hooks.md
2. Read the fetched content
3. Provide accurate answer based on current documentation
```

## Common Topics → Documentation Mapping

| User Topic | Documentation to Fetch |
|-----------|----------------------|
| "hook", "user-prompt-submit-hook", "file-artifacts hook" | hooks.md |
| "memory", "memory blocks", "memory context" | memory.md |
| "statusline", "status bar", "statusline config" | statusline.md |
| "snippet", "snippet injection", "pattern matching" | snippets.md |
| "slash command", "custom command", "/command" | commands.md |
| "TypeScript agent", "TS SDK", "JavaScript SDK" | typescript.md |
| "Python agent", "Python SDK" | python.md |
| "claude code config", "configuration", "settings" | configuration.md |

## Documentation Fetching Best Practices

1. **Always fetch before answering** - Don't rely on potentially outdated training data
2. **Fetch multiple if needed** - If the question spans multiple topics, fetch all relevant docs
3. **Parse markdown carefully** - The docs are in markdown format with code examples
4. **Use code examples** - The docs include runnable examples, share them with users
5. **Check for updates** - If docs seem outdated, mention that to the user

## Error Handling

If curl fails:
- Try the URL without `.md` extension (might be an HTML page)
- Check if the documentation has moved
- Inform the user that you couldn't fetch the latest docs and will use training data (with disclaimer)

## Documentation Base URL

All Claude documentation is under: `https://docs.claude.com/`

Common paths:
- `/en/docs/claude-code/` - Claude Code features
- `/en/api/agent-sdk/` - Agent SDK documentation
- `/en/api/` - API documentation

---

# Headless Use Patterns

## Overview

Headless mode enables Claude Code usage in **non-interactive, automated environments** such as:
- **CI/CD pipelines** - Automated code review, testing, deployment
- **Batch processing** - Process multiple files or tasks programmatically
- **Scripted automation** - Integrate Claude into existing workflows
- **Background tasks** - Long-running operations without user interaction

## Quick Start

**One-shot command with JSON output:**
```bash
claude --output-format "stream-json" -p "task" | jq .
```

**Headless automation:**
```bash
claude --permission-mode bypassPermissions --max-turns 5 -p "automate task"
```

**Session continuation:**
```bash
# Capture session ID
SESSION=$(claude --debug -p "first task" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)

# Continue session
claude -c "$SESSION" -p "follow-up task"
```

## Common Patterns

### CI/CD Code Review
```bash
claude --permission-mode bypassPermissions \
       --allowed-tools "Read,Grep,Glob" \
       --max-turns 5 \
       --output-format compact-text \
       -p "review code for security issues" > review.md
```

### Batch File Processing
```bash
for file in src/**/*.js; do
    claude --permission-mode bypassPermissions \
           --max-turns 3 \
           -p "Review and fix $file"
done
```

### Output Parsing
```bash
# Extract cost
claude --output-format "stream-json" -p "task" | \
  jq -r 'select(.type == "result") | .total_cost_usd'

# Get result
claude --output-format "compact-json" -p "task" | \
  jq '.messages[-1].content[0].text'
```

## Complete Guide

**For comprehensive headless patterns including:**
- Output formats (stream-json, compact-json, compact-text)
- Permission modes for automation
- Tool restrictions
- Session management
- Error handling and retries
- GitHub Actions integration
- Cost monitoring

See **[reference/headless-patterns.md](reference/headless-patterns.md)** for complete documentation.

---

# Agent SDK Patterns

## Overview

Build custom agents programmatically with the **Claude Agent SDK** in Python or TypeScript.

**Features:**
- **Conversation management** - Multi-turn interactions with memory
- **Custom tools** - Define MCP tools with `@tool` decorator
- **Permission control** - Fine-grained capability restrictions
- **Context management** - Automatic compaction and optimization
- **Session control** - Resume, fork, and manage conversations

## Installation

**Python:**
```bash
pip install claude-agent-sdk
```

**TypeScript:**
```bash
npm install @anthropic-ai/claude-agent-sdk
```

## Quick Start - Python

### Simple Query
```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="What is 2+2?",
    options=ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        allowed_tools=[]
    )
):
    if message.type == "result":
        print(message.result)
```

### Continuous Conversation
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async with ClaudeSDKClient(options=ClaudeAgentOptions()) as client:
    # First question
    await client.query("Remember: my name is Alice")
    async for msg in client.receive_response():
        if msg.type == "result": break

    # Follow-up - Claude remembers context
    await client.query("What's my name?")
    async for msg in client.receive_response():
        if msg.type == "result": break
```

### Custom Tools
```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args):
    return {"content": [{"type": "text", "text": f"Sum: {args['a'] + args['b']}"}]}

server = create_sdk_mcp_server(name="calc", tools=[add])

options = ClaudeAgentOptions(
    mcp_servers={"calc": server},
    allowed_tools=["mcp__calc__add"]
)
```

## Quick Start - TypeScript

```typescript
import { query, tool, createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

// Simple query
for await (const msg of query({prompt: "task", options: {permissionMode: 'bypassPermissions'}})) {
  if (msg.type === 'result') console.log(msg.result);
}

// Custom tool
const myTool = tool('add', 'Add numbers', z.object({a: z.number(), b: z.number()}),
  async (args) => ({content: [{type: 'text', text: `Sum: ${args.a + args.b}`}]}));

const server = createSdkMcpServer({name: 'calc', tools: [myTool]});
```

## Key Concepts

### When to Use What

**`query()`** - One-off tasks, independent questions
**`ClaudeSDKClient`** - Continuous conversations, follow-ups, chat interfaces

### Permission Modes

- `bypassPermissions` - Auto-approve everything (automation)
- `acceptEdits` - Auto-approve file edits only
- `plan` - Planning mode, no execution
- `default` - Standard permissions (requires interaction)

### Loading Project Context (CLAUDE.md)

```python
options = ClaudeAgentOptions(
    system_prompt={"type": "preset", "preset": "claude_code"},
    setting_sources=["project"],  # Loads CLAUDE.md files
    allowed_tools=["Read", "Write", "Edit"]
)
```

## Complete Guide

**For comprehensive Agent SDK patterns including:**
- Programmatic subagents
- Permission handlers
- Session management (resume, fork)
- Custom MCP tools
- Streaming input
- Error handling
- Cost monitoring
- TypeScript and Python examples

See **[reference/agent-sdk-patterns.md](reference/agent-sdk-patterns.md)** for complete documentation.

---

# Debugging Claude Code

## Overview

This section provides guidance on testing modifications to Claude Code itself, including hook configurations, plugin changes, and snippet updates, using the `claude` CLI with debug mode.

## Key Testing Commands

### 1. One-Shot Testing with Debug Mode

Test modifications without entering interactive mode:

```bash
# Basic one-shot test with debug output
claude --debug -p "your test prompt here"

# Structured JSON output for parsing
claude --debug --verbose --output-format "stream-json" -p "test prompt" | jq .

# Test with specific working directory
cd /path/to/test/directory
claude --debug -p "test prompt"

# Test hook triggers
claude --debug -p "keyword that triggers hook"
```

**Why `--debug`?**
- Writes detailed debug logs to `~/.claude/debug/{session_id}/`
- Shows system initialization, tools, MCP servers, slash commands
- Reveals session_id for conversation continuation
- Displays hook execution, pattern matching, script paths
- Essential for debugging plugin/hook configurations

**Debug Output Structure:**
```json
{
  "type": "system",
  "subtype": "init",
  "cwd": "/working/directory",
  "session_id": "f4abda12-6884-44f2-ae60-228eeb924482",
  "tools": ["Task", "Bash", "Read", "Write", ...],
  "mcp_servers": [{"name": "exa", "status": "connected"}],
  "model": "claude-sonnet-4-5-20250929",
  "slash_commands": ["exp-create", "exp-list", ...]
}
```

**Debug Logs Location:** `~/.claude/debug/{session_id}/`
- Complete conversation transcript
- Hook execution details
- Tool calls and responses
- Error traces and warnings

### 2. Continue Conversation After One-Shot

You can continue the conversation from a one-shot command using the session_id from debug output:

```bash
# Start with one-shot test and capture session_id
claude --debug --verbose --output-format "stream-json" -p "test my hook" | jq . > /tmp/debug.json
SESSION_ID=$(jq -r '.session_id' /tmp/debug.json | head -1)

# Continue conversation with session_id
claude --debug -p "did the hook work?" -c "$SESSION_ID"

# Alternative: Continue most recent conversation
claude -c

# Continue with another one-shot using session_id
claude --debug --verbose --output-format "stream-json" -p "test another aspect" -c "$SESSION_ID" | jq .
```

**Session Continuation Examples:**

```bash
# Example 1: Test hook, then verify
❯ claude --debug --verbose --output-format "stream-json" -p "hi" | jq .
{
  "type": "system",
  "subtype": "init",
  "session_id": "f4abda12-6884-44f2-ae60-228eeb924482",
  ...
}

❯ claude --debug -p "did I say hi before?" -c f4abda12-6884-44f2-ae60-228eeb924482
# Claude will have context from previous message

# Example 2: Verify debug logs exist
❯ ls ~/.claude/debug/f4abda12-6884-44f2-ae60-228eeb924482/
# Contains complete conversation transcript
```

**Use Cases:**
- Initial automated test, then manual exploration
- Scripted test sequences with conversation memory
- Iterative debugging workflows across multiple commands
- Verify hook effects persist across conversation turns

### 3. Debug Logs Deep Dive

**Location:** `~/.claude/debug/{session_id}/`

Debug logs contain complete execution traces for detailed post-mortem analysis:

```bash
# List all debug sessions
ls -lth ~/.claude/debug/ | head -20

# Find most recent session
LATEST=$(ls -t ~/.claude/debug/ | head -1)
echo "Latest session: $LATEST"

# View complete logs for a session
cat ~/.claude/debug/$LATEST/*

# Search for specific patterns in logs
grep -r "UserPromptSubmit" ~/.claude/debug/$LATEST/
grep -r "SNIPPET_NAME" ~/.claude/debug/$LATEST/
grep -r "hook.*matched" ~/.claude/debug/$LATEST/

# Monitor logs in real-time (for long-running commands)
tail -f ~/.claude/debug/$LATEST/*

# Extract key information
cat ~/.claude/debug/$LATEST/* | grep -E "(session_id|tools|mcp_servers|slash_commands)"
```

**What's in Debug Logs:**
- **System initialization**: Session ID, working directory, available tools
- **MCP server status**: Which servers connected/failed
- **Tool calls**: Every tool invoked with parameters and responses
- **Hook execution**: Pattern matching, script paths, output
- **Error traces**: Complete stack traces for debugging
- **Conversation turns**: Full request/response cycle

**Debug Log Analysis Example:**

```bash
# Scenario: Testing if a snippet injection worked

# 1. Run test and capture session_id
OUTPUT=$(claude --debug --verbose --output-format "stream-json" -p "docker help" | jq .)
SESSION_ID=$(echo "$OUTPUT" | jq -r 'select(.session_id != null) | .session_id' | head -1)

# 2. Check if UserPromptSubmit hook fired
cat ~/.claude/debug/$SESSION_ID/* | grep "UserPromptSubmit"

# 3. Verify snippet content was injected
cat ~/.claude/debug/$SESSION_ID/* | grep -A 50 "user-prompt-submit-hook"

# 4. Check for snippet announcement in response
cat ~/.claude/debug/$SESSION_ID/* | grep "Active Context"

# 5. Verify verification hash was present
cat ~/.claude/debug/$SESSION_ID/* | grep "VERIFICATION_HASH"
```

**Debugging Failed Hooks:**

```bash
# Check if hook pattern matched
grep -r "hook.*matched" ~/.claude/debug/$SESSION_ID/

# Check for script execution errors
grep -r "error\|Error\|ERROR" ~/.claude/debug/$SESSION_ID/

# Verify script path was correct
grep -r "command.*python3.*scripts" ~/.claude/debug/$SESSION_ID/

# Check hook output
grep -r "hook.*output" ~/.claude/debug/$SESSION_ID/
```

## Testing Hook Configurations

### Workflow

1. **Modify hook configuration** (e.g., `hooks/hooks.json` or `plugin.json`)

2. **Verify configuration** with `/hooks` command:
   ```bash
   claude -p "/hooks"
   ```

3. **Test hook trigger with debug mode**:
   ```bash
   # Use --debug to capture full execution details
   claude --debug -p "prompt containing trigger keyword"
   ```

4. **Check debug output and logs** for:
   - Matching hook patterns
   - Script execution paths
   - Command output/errors
   - Success/failure status
   - Full execution trace in `~/.claude/debug/{session_id}/`

5. **Review debug logs**:
   ```bash
   # Find your session_id from the debug output, then:
   cat ~/.claude/debug/{session_id}/*
   # Or tail for real-time monitoring:
   tail -f ~/.claude/debug/{session_id}/*
   ```

6. **Iterate**: Adjust configuration based on debug output and logs

### Hook Testing Checklist

- [ ] JSON syntax is valid (use `jq` or JSON validator)
- [ ] Hook patterns match correctly (test regex separately)
- [ ] Script paths are absolute (use `${CLAUDE_PLUGIN_ROOT}`)
- [ ] Scripts have execution permissions (`chmod +x`)
- [ ] Environment variables are accessible
- [ ] Commands work when run manually
- [ ] Tool names match exactly (case-sensitive)

### Example: Testing a UserPromptSubmit Hook

```bash
# 1. Check hook is registered
claude -p "/hooks"

# 2. Test with trigger keyword (debug mode with JSON output)
claude --debug --verbose --output-format "stream-json" -p "docker containers" | jq . | tee /tmp/test.json

# 3. Extract session_id for continuation
SESSION_ID=$(jq -r 'select(.session_id != null) | .session_id' /tmp/test.json | head -1)
echo "Session ID: $SESSION_ID"

# 4. Verify snippet injection in debug logs
cat ~/.claude/debug/$SESSION_ID/* | grep -A 10 "UserPromptSubmit"

# 5. Continue conversation to verify context persists
claude --debug -p "what snippet was active?" -c "$SESSION_ID"

# 6. Review complete debug logs
ls -lh ~/.claude/debug/$SESSION_ID/
cat ~/.claude/debug/$SESSION_ID/*
```

## Testing Snippet Configurations

### Pattern Matching Tests

```bash
# Test if snippet triggers correctly (CLI tool)
cd /path/to/plugin/scripts
python3 snippets_cli.py test snippet-name "test prompt with keywords" --snippets-dir ../commands/local

# Test via live interaction with debug mode
claude --debug --verbose --output-format "stream-json" -p "prompt with snippet keywords" | jq .

# Extract session_id and check debug logs for snippet injection
SESSION_ID=$(claude --debug -p "test keyword" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
cat ~/.claude/debug/$SESSION_ID/* | grep "SNIPPET_NAME"
```

### Verification Hash Testing

Add a unique verification hash to your snippet:

```markdown
**VERIFICATION_HASH:** `8d3a7f1b9c4e2056`
```

Then test if it's injected:

```bash
claude -p "what is the verification hash for testing?"
# Should return: 8d3a7f1b9c4e2056
```

### Snippet Testing Workflow

1. **Create/modify snippet**
2. **Test pattern matching** (CLI tool)
3. **Test live injection** (`claude --debug`)
4. **Verify hash** (one-shot question)
5. **Test announcement** (check for Active Context message)
6. **Continue conversation** (verify context persists)

## Testing Plugin Changes

### Full Plugin Test Workflow

```bash
# 1. Modify plugin (hooks, commands, snippets)

# 2. Restart Claude Code (required for changes to take effect)
# Exit any running sessions, then start fresh

# 3. Verify plugin loaded
claude -p "/plugin list"

# 4. Test commands
claude -p "/your-command test-input"

# 5. Test hooks with debug mode
claude --debug -p "trigger your hook"

# 6. Test snippets
claude --debug -p "keywords that trigger snippet"

# 7. Continue conversation to verify state
claude -c -p "confirm the context is still active"
```

## Common Pitfalls

### Forgetting to Restart

**Issue:** Plugin/hook changes don't take effect

**Solution:** Exit Claude Code and restart after configuration changes

### Relative Paths in Hooks

**Issue:** Scripts can't be found

**Solution:** Use absolute paths or `${CLAUDE_PLUGIN_ROOT}`

```json
// ❌ Wrong
"command": "./scripts/hook.py"

// ✅ Right
"command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/hook.py"
```

### Not Using Debug Mode

**Issue:** Can't see what's happening during execution, no logs saved

**Solution:** Always use `--debug` when testing

```bash
# ❌ Limited visibility, no logs
claude -p "test"

# ✅ Full debugging output with logs
claude --debug -p "test"

# ✅ Structured JSON output for parsing
claude --debug --verbose --output-format "stream-json" -p "test" | jq .

# ✅ Check debug logs afterward
ls ~/.claude/debug/  # List all session directories
cat ~/.claude/debug/{session_id}/*  # View specific session logs
```

### Testing in Wrong Directory

**Issue:** Hooks/snippets don't trigger as expected

**Solution:** Test in appropriate working directory

```bash
# Be explicit about where you test
cd /path/to/test/project
claude --verbose -p "test"
```

## Best Practices

1. **Always use `--debug`** when testing modifications - saves logs to `~/.claude/debug/{session_id}/`
2. **Capture session_id** for conversation continuation and log review
3. **Test incrementally**: One change at a time
4. **Create verification hashes**: Unique identifiers to confirm injection
5. **Review debug logs**: Check `~/.claude/debug/{session_id}/` for complete execution trace
6. **Automate tests**: Create bash scripts for repeatable testing with session tracking
7. **Test conversation continuity**: Use `-c {session_id}` to verify state persists
8. **Manual script testing**: Run scripts directly before testing in Claude
9. **Check permissions**: Ensure scripts are executable
10. **Use absolute paths**: Avoid relative path issues with `${CLAUDE_PLUGIN_ROOT}`
11. **Restart after changes**: Plugin/hook changes require restart
12. **Document test cases**: Keep track of what should happen and expected session IDs

## Quick Reference

```bash
# Test hook execution with debug mode
claude --debug -p "trigger keyword"

# Get structured JSON output
claude --debug --verbose --output-format "stream-json" -p "test" | jq .

# Capture session_id for continuation
SESSION_ID=$(claude --debug -p "test" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)

# Continue conversation with session_id
claude --debug -p "follow-up test" -c "$SESSION_ID"

# Review debug logs
ls ~/.claude/debug/  # List all sessions
cat ~/.claude/debug/$SESSION_ID/*  # View specific session
tail -f ~/.claude/debug/$SESSION_ID/*  # Monitor in real-time

# Test snippet pattern matching (CLI)
python3 snippets_cli.py test snippet-name "test prompt" --snippets-dir ../commands/local

# Verify plugin loaded
claude -p "/plugin list"

# Check hook configuration
claude -p "/hooks"

# Automated test script with session tracking
#!/bin/bash
OUT=$(claude --debug --verbose --output-format "stream-json" -p "test 1" | jq .)
SESSION_ID=$(echo "$OUT" | jq -r 'select(.session_id != null) | .session_id' | head -1)
echo "Session: $SESSION_ID"

# Check debug logs
cat ~/.claude/debug/$SESSION_ID/* | grep "expected" && echo "✅" || echo "❌"

# Continue and test
claude --debug -p "test 2" -c "$SESSION_ID" | grep "expected" && echo "✅" || echo "❌"
```

## Resources

- [CLI Reference](https://docs.claude.com/en/docs/claude-code/cli-reference.md)
- [Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks.md)
- [Interactive Mode](https://docs.claude.com/en/docs/claude-code/interactive-mode.md)
- [Troubleshooting Guide](https://docs.claude.com/en/docs/claude-code/troubleshooting.md)

---

# MCP Server Configuration

## Overview

MCP (Model Context Protocol) servers extend Claude Code's capabilities by providing additional tools and context. This section covers how to configure MCP servers using the `claude mcp` CLI.

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

## MCP Server Best Practices

1. **Use local scope for project-specific servers** - Keeps project dependencies isolated
2. **Use global scope for general-purpose servers** - Exa, filesystem access, etc.
3. **Version lock MCP packages** - Use specific versions instead of `@latest` for stability
4. **Document environment variables** - Include `.env.example` in projects
5. **Test connection after adding** - Run `claude mcp list` to verify ✓ Connected status
6. **Keep tokens secure** - Don't commit tokens to git, use environment variables

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

## MCP Server Documentation

For server-specific documentation:

- **Playwright MCP**: https://github.com/microsoft/playwright-mcp
- **MCP Specification**: https://modelcontextprotocol.io/
- **Official MCP Servers**: https://github.com/modelcontextprotocol/servers
- **Claude Code Docs**: https://docs.claude.com/en/docs/claude-code/

## MCP Quick Reference

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

---

# Snippet Verification

## Overview

When the user mentions "snippetV" or "snippet-verify", perform a comprehensive snippet verification check to ensure snippets are correctly injected into context.

## Verification Process

### Step 1: Identify Injected Snippets

Search your current context for snippet tags and verification hashes. Look for:
- XML-style tags like `<snippet_name>...</snippet_name>`
- Lines containing `**VERIFICATION_HASH:** \`hash\``

List all snippets found in your context with their extracted hashes.

### Step 2: Get Ground Truth from CLI

Run this command to retrieve the authoritative snippet list with hashes:

```bash
cd ~/.claude/snippets && ./snippets-cli.py list --show-content
```

Parse the JSON output to extract:
- Snippet names
- Patterns
- Verification hashes (found in content as `**VERIFICATION_HASH:** \`...\``)
- File paths
- Enabled status

### Step 3: Cross-Verify

Compare the hashes found in your context against the CLI ground truth:

- ✅ **Match**: Hash in context matches CLI hash → Snippet correctly injected
- ❌ **Mismatch**: Hash differs → Snippet outdated or corrupted
- ⚠️ **Missing in Context**: Snippet in CLI but not in your context → Not triggered
- ⚠️ **Missing Hash**: Snippet tag present but no hash found → Verification impossible

### Step 4: Report Results

Present a clear verification report with proper line breaks for readability:

```
📋 Snippet Verification Report

INJECTED SNIPPETS IN CONTEXT:

✅ snippet-name (hash) - Verified

❌ snippet-name (hash) - MISMATCH (expected: correct_hash)

⚠️ snippet-name - Missing hash

ALL SNIPPETS IN CLI:

• snippet-name: hash (pattern: regex)

• snippet-name: hash (pattern: regex)

SUMMARY:

• Total in CLI: X

• Injected in context: Y

• Verified: Z

• Mismatches: M

• Missing hashes: N
```

## Important Notes

- The verification hash is a unique identifier generated when the snippet is created/updated
- It uses Python's hashlib and includes timestamp for uniqueness
- Hashes are embedded directly in snippet content as `**VERIFICATION_HASH:** \`hash\``
- The CLI command `list --show-content` is the authoritative source
- Always use Bash tool to run the CLI command, don't assume values

## Example CLI Output Format

```json
{
  "success": true,
  "operation": "list",
  "data": {
    "snippets": [
      {
        "name": "codex",
        "pattern": "\\b(codex|cdx)\\b",
        "file": "snippets/codex.md",
        "enabled": true,
        "content": "<codex>\n**VERIFICATION_HASH:** `95f6ccff3c85627c`\n..."
      }
    ]
  }
}
```

Extract the hash from the content field using regex or string parsing.

---

# Advanced Testing Patterns

## Automated Test Suites

Create bash test scripts:

```bash
#!/bin/bash
# test_my_plugin.sh

echo "🧪 Testing Plugin: my-plugin"

# Test 1: Snippet exists
echo "Test 1: Snippet registration..."
claude -p "/plugin list" | grep -q "my-plugin" && echo "✅ PASS" || echo "❌ FAIL"

# Test 2: Pattern matching
echo "Test 2: Pattern matching..."
output=$(claude -p "test keyword" 2>&1)
echo "$output" | grep -q "expected content" && echo "✅ PASS" || echo "❌ FAIL"

# Test 3: Verification hash
echo "Test 3: Verification hash..."
output=$(claude -p "what is the verification hash?" 2>&1)
echo "$output" | grep -q "8d3a7f1b9c4e2056" && echo "✅ PASS" || echo "❌ FAIL"

# Test 4: Conversation continuity
echo "Test 4: Conversation continuity..."
claude -p "start test" > /dev/null
output=$(claude -c -p "continue test" 2>&1)
echo "$output" | grep -q "expected response" && echo "✅ PASS" || echo "❌ FAIL"
```

## JSON Output for Programmatic Testing

```bash
# Get JSON output for parsing
claude --debug --verbose -p "test" --output-format json > test-output.json

# Parse with jq
cat test-output.json | jq '.responses[].text'
```

## Limiting Turns for Testing

```bash
# Limit agentic turns for faster testing
claude --max-turns 3 -p "test prompt"
```

## Debugging Tips

### 1. Check Hook Execution

```bash
# Use debug mode to see full execution details
claude --debug -p "trigger keyword"

# With JSON output for programmatic analysis
claude --debug --verbose --output-format "stream-json" -p "trigger keyword" | jq .

# Review debug logs for complete execution trace
SESSION_ID=$(claude --debug -p "test" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
cat ~/.claude/debug/$SESSION_ID/* | less
```

### 2. Test Scripts Manually

```bash
# Run hook script directly to verify it works
/absolute/path/to/script.py "test input"
```

### 3. Validate JSON Configurations

```bash
# Check JSON syntax
jq . hooks/hooks.json

# Validate plugin manifest
jq . .claude-plugin/plugin.json
```

### 4. Check File Permissions

```bash
# Scripts must be executable
ls -la /path/to/script.py
chmod +x /path/to/script.py
```

### 5. Use Verification Hashes

Add unique hashes to track content injection:

```markdown
**VERIFICATION_HASH:** `unique-hash-12345`
```

Test with: `claude -p "what is the verification hash?"`

---

# Summary of Best Practices

## Documentation
- Always fetch latest docs with curl instead of relying on training data
- Fetch multiple docs if question spans multiple topics
- Include code examples from documentation in responses

## Debugging
- Always use `--debug` when testing modifications
- Capture session_id for continuation and log review
- Review debug logs in `~/.claude/debug/{session_id}/` for complete traces
- Test incrementally, one change at a time
- Create verification hashes to confirm injection

## MCP Configuration
- Use local scope for project-specific servers
- Use global scope for general-purpose servers
- Version lock MCP packages for stability
- Test connection after adding servers
- Keep tokens secure

## Snippet Verification
- Use verification hashes to track content integrity
- Always run CLI command to get authoritative snippet list
- Cross-verify hashes between context and CLI
- Report mismatches clearly to user

## Testing
- Test scripts manually before using in hooks
- Check permissions on all scripts
- Use absolute paths with `${CLAUDE_PLUGIN_ROOT}`
- Restart Claude Code after configuration changes
- Document test cases and expected outcomes
