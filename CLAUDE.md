# Claude Code Plugin Development Guide

**VERIFICATION_HASH:** `9f2e4a8c6d1b5730`

A concise guide to plugin development for Claude Code, focused on structure and best practices.

---

## Quick Reference

### Essential Documentation
- **[Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference.md)** - Complete plugin structure
- **[Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md)** - Marketplace setup
- **[Plugins Overview](https://docs.claude.com/en/docs/claude-code/plugins.md)** - How plugins work
- **[Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks.md)** - Hook configuration and events

---

## Plugin Structure

### Minimal Plugin

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # REQUIRED: Plugin manifest
├── commands/                # Optional: Slash commands
│   └── my-command.md
├── snippets/                # Optional: Context snippets
│   └── my-snippet.md
└── README.md                # Recommended
```

### Plugin Manifest (`.claude-plugin/plugin.json`)

```json
{
  "name": "my-plugin",           // REQUIRED: kebab-case
  "version": "1.0.0",            // REQUIRED: semver
  "description": "Brief desc",   // REQUIRED
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "commands": "./commands",      // Optional: relative path
  "snippets": "./snippets"       // Optional: relative path
}
```

**Key Rules:**
- All paths MUST be relative: `./commands`, `./snippets`
- Never use absolute paths
- Plugin name MUST be kebab-case
- Version MUST follow semver (X.Y.Z)

---

## Marketplace Structure

### Marketplace Manifest (`.claude-plugin/marketplace.json`)

```json
{
  "name": "marketplace-name",
  "owner": {
    "name": "Owner Name",
    "email": "owner@example.com"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "version": "1.0.0",
      "description": "Brief description",
      "source": "./plugin-directory"
    }
  ]
}
```

**Installation:**
```bash
# Add marketplace
/plugin marketplace add username/repo

# Install plugin
/plugin install plugin-name@marketplace-name
```

---

## Command Files

### Structure

```markdown
---
description: Brief description (shows in /help)
---

# Command Title

## Arguments

Input: `$ARGUMENTS`

## Instructions

1. **Parse arguments**:
   - Check for flags: `-f`, `--force`
   - Extract main input from `$ARGUMENTS`
   - Validate input

2. **Ask for confirmation** (unless `-f` or `--force`):
   - Show what will change
   - Wait for yes/no
   - Proceed only if yes

3. **Execute action**:
   - Perform operation
   - Handle errors gracefully
   - Confirm completion

## Example Usage

```
/my-command example input
/my-command --force another example
```

## Notes

- Important notes here
```

**Key Points:**
- **MUST have YAML frontmatter** with `description`
- **ALWAYS use `$ARGUMENTS`** for user input
- **Ask for confirmation** for create/update/delete (unless forced)
- **No confirmation** for read-only operations

---

## Snippet Files

### Structure

Snippets provide contextual instructions to Claude through the `UserPromptSubmit` hook. They follow a similar structure to commands but serve as continuous context rather than one-time actions.

```markdown
---
description: Brief description of what this snippet provides
SNIPPET_NAME: unique-identifier
ANNOUNCE_USAGE: true
---

# Snippet Title

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: snippet-name

If multiple snippets are detected, combine them:

📎 **Active Contexts**: snippet1, snippet2, snippet3

---

**VERIFICATION_HASH:** `unique-hash-here`

[Main instructions for Claude...]

## Section 1: Core Instructions

[Detailed instructions...]

## Section 2: Additional Guidance

[More instructions...]
```

**Key Points:**
- **YAML frontmatter** with `description`, `SNIPPET_NAME`, and `ANNOUNCE_USAGE`
- **Announcement block** at the top (tells Claude to announce active contexts)
- **Verification hash** for content integrity tracking
- **Clear section structure** for organization
- **Instructions are directives** to Claude, not conversational

---

## Template Pattern for Complex Snippets

For snippets that require external files (templates, examples), use this pattern:

### Directory Structure

```
my-plugin/
├── snippets/
│   └── my-snippet.md          # Main snippet with instructions
└── templates/
    └── my-template/
        ├── base-template.html  # Base template file
        └── examples.md         # Usage examples
```

### Template-Based Snippet Structure

```markdown
---
description: Snippet description
SNIPPET_NAME: my-snippet
ANNOUNCE_USAGE: true
---

# My Snippet Title

**INSTRUCTION TO CLAUDE**: Announcement block...

---

**VERIFICATION_HASH:** `hash-here`

## Primary Purpose

Main instructions for Claude...

## File Handling Instructions

1. **ALWAYS** create output directory: `mkdir -p output/`
2. Write to: `output/{description}.ext`
3. Open file after writing

## Template System

**Base Template:** `${CLAUDE_PLUGIN_ROOT}/templates/my-template/base-template.html`
- Contains all structure and styling
- Ready to use - just add content
- Includes feature X, Y, Z

**Examples & Reference:** `${CLAUDE_PLUGIN_ROOT}/templates/my-template/examples.md`
- Complete component examples
- Usage patterns
- Best practices

**Workflow:**
1. Read the base template: `${CLAUDE_PLUGIN_ROOT}/templates/my-template/base-template.html`
2. Replace `{{PLACEHOLDER}}` with actual content
3. Add custom content in designated section
4. Reference examples.md for patterns if needed

## Component Selection Guide

Quick reference table for choosing the right patterns:

| Use Case | Pattern | When to Use |
|----------|---------|-------------|
| Feature A | Pattern 1 | Scenario 1 |
| Feature B | Pattern 2 | Scenario 2 |

## Design Principles

### Principle 1: Title
- **Rule 1**: Description
- **Rule 2**: Description

### Principle 2: Title
- **Rule 1**: Description
- **Rule 2**: Description

## Common Patterns

### Pattern 1

\```language
# Example code
\```

### Pattern 2

\```language
# Example code
\```

## Best Practices

1. **Practice 1**: Explanation
2. **Practice 2**: Explanation
```

### Real-World Example: HTML Output Snippet

The `claude-code-snippets-plugin/snippets/HTML.md` demonstrates this pattern:

**Structure:**
```
claude-code-snippets-plugin/
├── snippets/
│   └── HTML.md                    # Main snippet with instructions
└── templates/
    └── html/
        ├── base-template.html     # Complete HTML template
        └── examples.md            # Component examples
```

**Key Features:**
- **Base template** contains all CSS, JavaScript, and HTML structure
- **Placeholders** like `{{TITLE}}` and `<!-- CONTENT GOES HERE -->`
- **Examples file** shows complete usage patterns
- **Workflow instructions** tell Claude to read template → replace placeholders → add content

**Benefits:**
1. **Separation of concerns** - Instructions separate from templates
2. **Reusability** - Templates can be used independently
3. **Maintainability** - Update template without changing snippet instructions
4. **Discoverability** - Examples file serves as reference documentation

### Template Pattern Best Practices

**1. Use `${CLAUDE_PLUGIN_ROOT}` for paths:**

✅ **Good:**
```markdown
**Base Template:** `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
```

❌ **Bad:**
```markdown
**Base Template:** `./templates/html/base-template.html`
```

**2. Provide clear workflow steps:**

```markdown
**Workflow:**
1. Read the base template: `${CLAUDE_PLUGIN_ROOT}/templates/...`
2. Replace `{{PLACEHOLDER}}` with actual content
3. Add content in designated section
4. Reference examples.md for patterns
```

**3. Include quick reference tables:**

Component selection guides help Claude choose the right patterns quickly.

**4. Keep snippet focused on instructions:**

The snippet file should contain instructions and references, not embed large templates inline.

**5. Document placeholder format:**

Clearly specify what placeholders exist and how to replace them.

---

## Hooks

**IMPORTANT:** When writing or configuring hooks, ALWAYS consult the **[Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks.md)** documentation for the correct structure and format.

### Hook Configuration (`hooks/hooks.json`)

Hooks can be defined in either `hooks/hooks.json` or inline in `plugin.json`.

**Correct Structure:**

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "pattern",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/my-script.py"
          }
        ]
      }
    ]
  }
}
```

**Common Events:**
- `UserPromptSubmit` - Before user prompt is processed
- `PreToolUse` - Before tool execution
- `PostToolUse` - After tool execution
- `Notification` - System notifications
- `SessionStart` / `SessionEnd` - Session lifecycle

**Key Rules:**
- ALWAYS use `${CLAUDE_PLUGIN_ROOT}` for script paths (not relative paths like `./`)
- Events are organized by event name as keys
- Each event contains an array of matchers
- `matcher` field is required (use `".*"` to match all)
- Hook type can be `command`, `validation`, or `notification`

**Example - User Prompt Hook:**

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/snippet_injector.py"
          }
        ]
      }
    ]
  }
}
```

**Plugin Manifest Reference:**

In `plugin.json`, add:
```json
{
  "hooks": "./hooks/hooks.json"
}
```

---

## Best Practices

### 1. Always Parse `$ARGUMENTS`

✅ **Good:**
```markdown
1. **Parse arguments**:
   - Extract snippet type from `$ARGUMENTS`
   - Check for `-f` or `--force` flag
```

❌ **Bad:**
```markdown
1. **Do the thing**
   - Just do it
```

### 2. Confirmation Pattern

**For destructive operations (create/update/delete):**

```markdown
**Ask for confirmation** (UNLESS `-f` or `--force`):
- Show user what will change
- Ask: "Proceed? (yes/no)"
- If no, abort
- If yes, proceed
```

**For read operations:**
- No confirmation needed

### 3. Backup Before Destructive Ops

```markdown
**Create backup**:
- Copy to `[filename].backup.[timestamp]`
- Inform user of backup location
```

### 4. Clear Error Messages

✅ **Good:**
```
❌ Error: File not found: ~/.claude/snippets/mail.md

Suggestion: Run `/create-snippet mail` to create it.
```

❌ **Bad:**
```
Error: File not found
```

### 5. Helpful Feedback

```markdown
✅ Created: ~/.claude/snippets/mail.md
✅ Backup: ~/.claude/snippets/mail.md.backup.20251010_123456

Next steps:
1. Restart Claude Code
2. Test with `/read-snippets`
```

---

## Common Gotchas

### 1. Absolute Paths

❌ **Wrong:**
```json
{
  "commands": "/Users/me/.claude/plugins/my-plugin/commands"
}
```

✅ **Right:**
```json
{
  "commands": "./commands"
}
```

### 2. Missing Frontmatter

❌ **Wrong:**
```markdown
# My Command
...
```

✅ **Right:**
```markdown
---
description: Brief description
---

# My Command
...
```

### 3. Not Parsing `$ARGUMENTS`

Commands MUST parse `$ARGUMENTS` - it contains everything after the command name.

### 4. No Confirmation for Destructive Ops

ALWAYS ask for confirmation before create/update/delete (unless `-f`/`--force`).

### 5. Plugin Name Mismatch

Directory name and manifest `name` should match:
```
my-plugin/                           # Directory
  .claude-plugin/
    plugin.json: { "name": "my-plugin" }  # Must match
```

### 6. Forgetting `.gitignore`

```gitignore
.env
*.backup.*
.DS_Store
node_modules/
```

### 7. Hardcoded Credentials

Never commit credentials. Use `.env` files (and gitignore them).

### 8. Not Restarting Claude Code

After editing plugins, MUST restart Claude Code or reload plugin to see changes.

---

## Testing Before Installation

### Understanding Installation Modes

**Python Package Installation Modes:**

**Editable Install:**
- Changes to source code reflect immediately
- Best for: Active development
- Command: `uv tool install --editable .` or `pip install -e .`
- How it works: Creates symlinks to source directory

**Production Install:**
- Builds cached wheel snapshot
- Best for: Stable releases, production deployments
- Command: `uv tool install .` or `pip install .`
- Requires: Reinstall after code changes
- Common issue: Stale build cache if not cleaned first

**Local Environment (Recommended for Development):**
- No global install needed
- Command: `uv sync` then `uv run <command>`
- Always uses current source code
- Best for: Fastest iteration cycle

**Preventing Stale Builds:**
```makefile
install: clean
	uv tool install --force .

clean:
	rm -rf build/ dist/ *.egg-info
```

### 1. Create Local Test Marketplace

```bash
mkdir -p test-marketplace/.claude-plugin

cat > test-marketplace/.claude-plugin/marketplace.json <<EOF
{
  "name": "test-marketplace",
  "owner": {
    "name": "Test",
    "email": "test@example.com"
  },
  "plugins": [
    {
      "name": "my-plugin",
      "version": "1.0.0",
      "description": "Test",
      "source": "../my-plugin"
    }
  ]
}
EOF
```

### 2. Install Locally

```bash
# Add test marketplace (use absolute path)
/plugin marketplace add file:///absolute/path/to/test-marketplace

# Install plugin
/plugin install my-plugin@test-marketplace

# Test command
/my-command test input

# Verify in help
/help | grep my-command
```

### 3. Pre-Release Checklist

- [ ] Plugin manifest is valid JSON
- [ ] All paths are relative
- [ ] Commands have frontmatter
- [ ] `$ARGUMENTS` parsing works
- [ ] Confirmation prompts work (unless forced)
- [ ] Error messages are helpful
- [ ] No hardcoded paths or credentials
- [ ] `.gitignore` configured
- [ ] README is accurate
- [ ] Version number updated

---

## Publishing to Marketplace

### 1. Add Plugin Entry

In marketplace's `.claude-plugin/marketplace.json`:

```json
{
  "plugins": [
    {
      "name": "my-plugin",
      "version": "1.0.0",
      "description": "Brief description",
      "source": "./my-plugin"
    }
  ]
}
```

### 2. Users Install Via

```bash
/plugin marketplace add username/marketplace-repo
/plugin install my-plugin@marketplace-name
```

### 3. Document in README

```markdown
## Installation

1. Add marketplace:
   ```bash
   /plugin marketplace add username/marketplace-repo
   ```

2. Install plugin:
   ```bash
   /plugin install my-plugin@marketplace-name
   ```

3. Verify:
   ```bash
   /help
   ```
```

---

## File Naming Conventions

**Commands:**
- Use kebab-case: `create-snippet.md`, `update-config.md`
- Be descriptive: `setup-oauth.md` not `setup.md`

**Snippets:**
- Use lowercase: `mail.md`, `calendar.md`
- Keep short and memorable

---

## Troubleshooting

**Plugin not loading:**
- Check manifest exists at `.claude-plugin/plugin.json`
- Validate JSON (use jsonlint.com)
- Ensure paths are relative
- Restart Claude Code

**Commands not appearing:**
- Check YAML frontmatter exists
- Verify `commands` path in manifest
- Files must end in `.md`
- Run `/help` to verify

**Changes not taking effect:**
- Restart Claude Code after editing plugins

---

## Resources

- [Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference.md)
- [Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md)
- [Plugins Overview](https://docs.claude.com/en/docs/claude-code/plugins.md)
- [Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks.md)
- [MCP Specification](https://modelcontextprotocol.io)

**Examples in this marketplace:**
- `claude-code-snippets-plugin` - Snippet injection system
- `gmail-gcal-mcp-plugin` - Gmail & Calendar automation

---

## Modification Log

This section tracks modifications to this guide and the marketplace.

### 2025-10-16
- **Added**: `skills-warren` plugin to marketplace
  - Created new plugin for custom Apache-licensed skills
  - Includes Apache 2.0 compliance snippet
  - Prepared for adaptation of Anthropic example-skills:
    - mcp-builder
    - skill-creator
    - theme-factory
    - webapp-testing
    - artifacts-builder
  - Full LICENSE and NOTICE files included
  - Plugin structure: `.claude-plugin/plugin.json`, `snippets/`, `skills/`

### 2025-10-12
- Initial guide created
- Documented plugin development best practices
- Added template patterns for complex snippets
- Included hooks reference and examples

---

**Last Updated:** 2025-10-16
**Author:** Fucheng Warren Zhu

---

# Using Claude Code

## Overview

This section provides guidance for working with Claude Code programmatically and understanding its features.

**What you'll learn:**

- **Model selection** - When to use Opus, Sonnet, or Haiku
- **Documentation access** - How to fetch latest Claude Code docs
- **Headless automation** - CI/CD, batch processing, scripted workflows
- **Agent SDK** - Building custom agents in Python and TypeScript
- **Debugging** - Testing hooks, plugins, and configurations
- **MCP servers** - Configuring and managing external tools
- **Snippet verification** - Ensuring snippets inject correctly

---

## Model Selection: Opus vs Sonnet vs Haiku

**Quick decision guide:**

| Use Case                                              | Model      | Why                                             |
| ----------------------------------------------------- | ---------- | ----------------------------------------------- |
| Complex reasoning, architecture design, code reviews  | **Opus**   | Highest intelligence, best at nuanced decisions |
| General coding, refactoring, debugging, documentation | **Sonnet** | Best balance of capability and speed            |
| Simple tasks, formatting, quick edits, explanations   | **Haiku**  | Fastest and most cost-effective                 |

### Detailed Guidance

#### Use Opus When:
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

#### Use Sonnet When (Default):
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

#### Use Haiku When:
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

## Documentation Access

**ALWAYS fetch the latest Claude Code documentation directly** when you need to implement any of the features.

### Available Documentation

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

### Usage Pattern

When user asks about Claude Code features:

1. **Identify relevant documentation** from the list above
2. **Fetch using curl** via the Bash tool
3. **Read and apply** the fetched content to answer accurately

---

## Quick Start Guides

### Headless Automation

**For CI/CD, batch processing, and scripted workflows.**

#### Basic One-Shot Command

```bash
# Simple task
claude -p "analyze this code"

# With automation settings
claude --permission-mode bypassPermissions --max-turns 5 -p "run tests and fix failures"

# Read-only analysis
claude --allowed-tools "Read,Grep,Glob" -p "review codebase structure"
```

#### Structured Output for Parsing

```bash
# JSON output for scripts
claude --output-format "stream-json" -p "task" | jq .

# Extract specific fields
claude --output-format "stream-json" -p "task" | \
  jq -r 'select(.type == "result") | .total_cost_usd'
```

#### Session Continuation

```bash
# Capture session ID
SESSION=$(claude --debug -p "first task" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)

# Continue conversation
claude -c "$SESSION" -p "follow-up task"
```

---

### Agent SDK (Python)

**For building custom agents programmatically.**

#### Installation

```bash
pip install claude-agent-sdk
```

#### Simple Query

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

#### Continuous Conversation

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

#### Custom Tools

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

---

### Agent SDK (TypeScript)

**For building custom agents in Node.js/TypeScript.**

#### Installation

```bash
npm install @anthropic-ai/claude-agent-sdk
```

#### Simple Query

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

#### Custom Tools with Zod

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

---

## Quick Decision Tree

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

## Official Documentation Links

- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/)
- [Agent SDK Overview](https://docs.claude.com/en/api/agent-sdk/overview)
- [Python SDK](https://docs.claude.com/en/api/agent-sdk/python)
- [TypeScript SDK](https://docs.claude.com/en/api/agent-sdk/typescript)
- [Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks.md)
- [MCP Specification](https://modelcontextprotocol.io/)
- Always make install after you push.