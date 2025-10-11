# Claude Documentation Reference

**VERIFICATION_HASH:** `e3034dc421039967`


## IMPORTANT: Fetch Documentation Directly

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

## Multiple Doc Fetch Example

If user asks: "How do I create a hook that modifies memory?"

```bash
# Fetch both relevant docs
curl -s https://docs.claude.com/en/docs/claude-code/hooks.md
curl -s https://docs.claude.com/en/docs/claude-code/memory.md
```

Then synthesize the answer from both documentation sources.

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
