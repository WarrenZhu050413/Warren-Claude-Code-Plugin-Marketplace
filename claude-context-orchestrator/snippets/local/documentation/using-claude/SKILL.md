---
name: using-claude
description: Working with Claude Code features, debugging hooks, MCP integration, snippet verification, headless automation, and Agent SDK. Use this skill when the user asks about Claude Code features, hooks, memory, statusline, debugging, MCP servers, headless use patterns, CI/CD automation, Python/TypeScript Agent SDK, or building custom agents.
---

# Using Claude Code

## Overview

This skill provides guidance for working with Claude Code programmatically and understanding its features.

**What you'll learn:**

- **Model selection** - When to use Opus, Sonnet, or Haiku
- **Documentation access** - How to fetch latest Claude Code docs
- **Headless automation** - CI/CD, batch processing, scripted workflows
- **Agent SDK** - Building custom agents in Python and TypeScript
- **Debugging** - Testing hooks, plugins, and configurations
- **MCP servers** - Configuring and managing external tools
- **Snippet verification** - Ensuring snippets inject correctly

---

# Model Selection: Opus vs Sonnet vs Haiku

**Quick decision guide:**

| Use Case                                              | Model      | Why                                             |
| ----------------------------------------------------- | ---------- | ----------------------------------------------- |
| Complex reasoning, architecture design, code reviews  | **Opus**   | Highest intelligence, best at nuanced decisions |
| General coding, refactoring, debugging, documentation | **Sonnet** | Best balance of capability and speed            |
| Simple tasks, formatting, quick edits, explanations   | **Haiku**  | Fastest and most cost-effective                 |

## Detailed Guidance

### Use Opus When:
_Highest intelligence • Slower • Most expensive_

- **Architectural decisions** - Designing system architecture, evaluating trade-offs
- **Complex refactoring** - Large-scale code restructuring requiring deep understanding
- **Security audits** - Thorough security analysis and vulnerability detection
- **Code reviews** - Comprehensive review requiring contextual understanding
- **Research and exploration** - Open-ended investigation of unfamiliar codebases

**Example:**

```python
options = ClaudeAgentOptions(
    model="opus",  # Use highest intelligence
    max_turns=10
)
```

### Use Sonnet When (Default):
_Best balance • Fast • Moderate cost_

- **General development** - Day-to-day coding tasks
- **Debugging** - Finding and fixing bugs
- **Writing tests** - Creating test suites
- **Documentation** - Generating API docs, READMEs
- **Refactoring** - Standard code improvements
- **Feature implementation** - Building new functionality

**Example:**

```python
options = ClaudeAgentOptions(
    model="sonnet",  # Default choice for most tasks
    max_turns=5
)
```

### Use Haiku When:
_Fast • Cheapest • Good for simple tasks_

- **Simple edits** - Formatting, typo fixes, minor changes
- **Explanations** - Explaining code or concepts
- **Quick queries** - Simple questions that don't require deep analysis
- **Batch processing** - Processing many simple tasks where speed matters
- **Cost optimization** - When budget is a primary concern

**Example:**

```python
options = ClaudeAgentOptions(
    model="haiku",  # Fast and economical
    max_turns=3
)
```

---

# Documentation Access

**ALWAYS fetch the latest Claude Code documentation directly** when you need to implement any of the features.

## Available Documentation

```bash
# Core Features
curl -s https://docs.claude.com/en/docs/claude-code/hooks.md
curl -s https://docs.claude.com/en/docs/claude-code/memory.md
curl -s https://docs.claude.com/en/docs/claude-code/statusline.md
curl -s https://docs.claude.com/en/docs/claude-code/snippets.md
curl -s https://docs.claude.com/en/docs/claude-code/commands.md
curl -s https://docs.claude.com/en/docs/claude-code/configuration.md

# Agent SDK
curl -s https://docs.claude.com/en/api/agent-sdk/python.md
curl -s https://docs.claude.com/en/api/agent-sdk/typescript.md
curl -s https://docs.claude.com/en/api/agent-sdk/overview.md
```

## Usage Pattern

When user asks about Claude Code features:

1. **Identify relevant documentation** from the list above
2. **Fetch using curl** via the Bash tool
3. **Read and apply** the fetched content to answer accurately

---

# Quick Start Guides

## Headless Automation

**For CI/CD, batch processing, and scripted workflows.**

### Basic One-Shot Command

```bash
# Simple task
claude -p "analyze this code"

# With automation settings
claude --permission-mode bypassPermissions --max-turns 5 -p "run tests and fix failures"

# Read-only analysis
claude --allowed-tools "Read,Grep,Glob" -p "review codebase structure"
```

### Structured Output for Parsing

```bash
# JSON output for scripts
claude --output-format "stream-json" -p "task" | jq .

# Extract specific fields
claude --output-format "stream-json" -p "task" | \
  jq -r 'select(.type == "result") | .total_cost_usd'
```

### Session Continuation

```bash
# Capture session ID
SESSION=$(claude --debug -p "first task" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)

# Continue conversation
claude -c "$SESSION" -p "follow-up task"
```

**📖 Complete guide:** See [reference/headless-patterns.md](reference/headless-patterns.md)
**💻 Working example:** See `scripts/headless-example.sh`

---

## Agent SDK (Python)

**For building custom agents programmatically.**

### Installation

```bash
pip install claude-agent-sdk
```

### Simple Query

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="What is 2+2?",
    options=ClaudeAgentOptions(
        model="sonnet",  # Choose model based on task complexity
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

async with ClaudeSDKClient(options=ClaudeAgentOptions(model="sonnet")) as client:
    await client.query("Remember: my name is Alice")
    async for msg in client.receive_response():
        if msg.type == "result": break

    await client.query("What's my name?")  # Remembers context
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

**📖 Complete guide:** See [reference/agent-sdk-patterns.md](reference/agent-sdk-patterns.md)
**💻 Working example:** See `scripts/sdk-python-example.py`

---

## Agent SDK (TypeScript)

**For building custom agents in Node.js/TypeScript.**

### Installation

```bash
npm install @anthropic-ai/claude-agent-sdk
```

### Simple Query

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const msg of query({
  prompt: "What is 2+2?",
  options: {
    model: "sonnet",
    permissionMode: "bypassPermissions",
  },
})) {
  if (msg.type === "result") console.log(msg.result);
}
```

### Custom Tools with Zod

```typescript
import { tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const addTool = tool(
  "add",
  "Add two numbers",
  z.object({ a: z.number(), b: z.number() }),
  async (args) => ({
    content: [{ type: "text", text: `Sum: ${args.a + args.b}` }],
  }),
);

const server = createSdkMcpServer({ name: "calc", tools: [addTool] });
```

**📖 Complete guide:** See [reference/agent-sdk-patterns.md](reference/agent-sdk-patterns.md)
**💻 Working example:** See `scripts/sdk-typescript-example.ts`

---

## Debugging Claude Code

**Testing hooks, plugins, snippets, and configurations.**

### Debug Mode

```bash
# Always use --debug when testing modifications
claude --debug -p "test prompt"

# Structured output with debug info
claude --debug --verbose --output-format "stream-json" -p "test" | jq .

# Debug logs saved to ~/.claude/debug/{session_id}/
ls ~/.claude/debug/
```

### Testing Hooks

```bash
# 1. Check hooks are registered
claude -p "/hooks"

# 2. Test with trigger keyword
claude --debug -p "keyword that triggers hook"

# 3. Verify in debug logs
SESSION_ID=$(claude --debug -p "test" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
cat ~/.claude/debug/$SESSION_ID/* | grep "UserPromptSubmit"
```

### Testing Snippets

```bash
# Test pattern matching (CLI tool)
cd /path/to/plugin/scripts
python3 snippets_cli.py test snippet-name "test prompt with keywords"

# Test live injection
claude --debug -p "prompt with snippet keywords"
```

**📖 Complete guide:** See [reference/debugging-guide.md](reference/debugging-guide.md)

---

## MCP Server Configuration

**Configuring Model Context Protocol servers for external tools.**

### Quick Commands

```bash
# List all configured MCP servers
claude mcp list

# Add a server
claude mcp add <name> <command> [args...] -s local

# Add with JSON config (for complex setups)
claude mcp add-json <name> '<json-config>' -s local

# Get server details
claude mcp get <name>

# Remove server
claude mcp remove <name> -s local
```

### Common Examples

```bash
# Playwright MCP
claude mcp add playwright npx @playwright/mcp@latest -s local

# Exa (web search)
claude mcp add exa "https://mcp.exa.ai/mcp?exaApiKey=YOUR_KEY" -s global

# Filesystem access
claude mcp add filesystem npx @modelcontextprotocol/server-filesystem /path/to/dir -s local
```

**📖 Complete guide:** See [reference/mcp-configuration.md](reference/mcp-configuration.md)
**💻 Working examples:** See `scripts/mcp-commands.sh`

---

## Snippet Verification

**Ensuring snippets are correctly injected into context.**

### Quick Verification

When user mentions "snippetV" or "snippet-verify":

1. **Search context** for `**VERIFICATION_HASH:** \`...\``
2. **Run CLI** to get authoritative snippet list:
   ```bash
   cd ~/.claude/snippets
   ./snippets-cli.py list --show-content
   ```
3. **Compare hashes** between context and CLI
4. **Report results** with clear status indicators

### Verification Report Format

```
📋 Snippet Verification Report

INJECTED SNIPPETS:
✅ snippet-name (hash) - Verified
❌ snippet-name (hash) - MISMATCH
⚠️ snippet-name - Missing hash

SUMMARY:
• Total in CLI: X
• Injected: Y
• Verified: Z
```

**📖 Complete guide:** See [reference/snippet-verification.md](reference/snippet-verification.md)

---

# Additional Resources

## Reference Documentation

- **[Headless Patterns](reference/headless-patterns.md)** - CI/CD, batch processing, automation
- **[Agent SDK Patterns](reference/agent-sdk-patterns.md)** - Python and TypeScript SDK
- **[Debugging Guide](reference/debugging-guide.md)** - Testing hooks, plugins, snippets
- **[MCP Configuration](reference/mcp-configuration.md)** - Managing external tools
- **[Snippet Verification](reference/snippet-verification.md)** - Ensuring correct injection

## Working Scripts

- **`scripts/headless-example.sh`** - Headless automation examples
- **`scripts/sdk-python-example.py`** - Python SDK complete example
- **`scripts/sdk-typescript-example.ts`** - TypeScript SDK complete example
- **`scripts/mcp-commands.sh`** - MCP management commands

## Official Documentation

- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/)
- [Agent SDK Overview](https://docs.claude.com/en/api/agent-sdk/overview)
- [Python SDK](https://docs.claude.com/en/api/agent-sdk/python)
- [TypeScript SDK](https://docs.claude.com/en/api/agent-sdk/typescript)
- [Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks.md)
- [MCP Specification](https://modelcontextprotocol.io/)

---

# Quick Decision Tree

**"What should I use?"**

```
Need to automate Claude Code?
├─ One-off task → Headless CLI (claude -p "task")
├─ Complex automation → Python/TypeScript SDK
│  ├─ Python project → Python SDK
│  └─ Node.js project → TypeScript SDK
└─ Custom external tools → MCP servers

Need to debug?
├─ Testing hooks → Use --debug mode
├─ Testing snippets → Use snippets CLI + --debug
└─ Plugin development → Read debugging-guide.md

Need model selection?
├─ Complex reasoning → Opus
├─ General coding → Sonnet (default)
└─ Simple tasks → Haiku
```

---

**Remember:** This skill provides quick overviews. For detailed patterns and complete examples, always refer to the reference documentation linked above.
