# Claude Agent SDK Patterns

Comprehensive guide for building custom agents with the Claude Agent SDK in Python and TypeScript.

## Overview

The Claude Agent SDK provides programmatic access to Claude Code's agent harness, enabling you to build production-ready agents with:
- **Conversation management** - Multi-turn interactions with memory
- **Tool ecosystem** - File ops, code execution, web search, MCP
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

## Python SDK Patterns

### Pattern 1: Simple One-Off Query

Use `query()` for single-exchange interactions.

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def simple_query():
    async for message in query(
        prompt="What is the capital of France?",
        options=ClaudeAgentOptions(
            permission_mode="bypassPermissions",
            allowed_tools=[]  # No tools needed
        )
    ):
        if message.type == "result":
            print(f"Answer: {message.result}")

asyncio.run(simple_query())
```

**When to use:**
- One-off questions
- Independent tasks
- No conversation history needed
- Simple automation scripts

### Pattern 2: Continuous Conversation

Use `ClaudeSDKClient` for multi-turn interactions.

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from anthropic.types import TextBlock

async def continuous_conversation():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        allowed_tools=[]
    )

    async with ClaudeSDKClient(options=options) as client:
        # First question
        await client.query("Remember: my favorite color is blue")

        async for message in client.receive_response():
            if message.type == "result":
                break

        # Follow-up - Claude remembers context
        await client.query("What's my favorite color?")

        async for message in client.receive_response():
            if message.type == "assistant":
                for block in message.message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")  # "Your favorite color is blue"
            elif message.type == "result":
                break

asyncio.run(continuous_conversation())
```

**When to use:**
- Multi-turn conversations
- Follow-up questions
- Building chat interfaces
- Context-dependent logic

### Pattern 3: Custom Tools with MCP

Create in-process tools with the `@tool` decorator.

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeSDKClient, ClaudeAgentOptions
from typing import Any

@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args: dict[str, Any]) -> dict[str, Any]:
    result = args['a'] + args['b']
    return {
        "content": [{
            "type": "text",
            "text": f"Sum: {result}"
        }]
    }

@tool("fetch_user", "Fetch user data from database", {"user_id": int})
async def fetch_user(args: dict[str, Any]) -> dict[str, Any]:
    # Simulate database fetch
    user_id = args['user_id']
    user_data = {"id": user_id, "name": f"User{user_id}", "email": f"user{user_id}@example.com"}

    return {
        "content": [{
            "type": "text",
            "text": f"User data: {user_data}"
        }]
    }

async def main():
    # Create MCP server with custom tools
    calculator = create_sdk_mcp_server(
        name="calculator",
        version="1.0.0",
        tools=[add, fetch_user]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"calc": calculator},
        allowed_tools=["mcp__calc__add", "mcp__calc__fetch_user"],
        permission_mode="bypassPermissions"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("What is 42 + 58?")

        async for message in client.receive_response():
            if message.type == "result":
                print(f"Result: {message.result}")
                break

asyncio.run(main())
```

### Pattern 4: Permission Control

Custom permission handlers for fine-grained control.

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def custom_permission_handler(tool_name: str, input_data: dict, context: dict):
    """Custom permission logic"""

    # Block writes to system directories
    if tool_name == "Write":
        file_path = input_data.get("file_path", "")
        if file_path.startswith("/system/") or file_path.startswith("/etc/"):
            return {
                "behavior": "deny",
                "message": "System directory write not allowed",
                "interrupt": True
            }

    # Redirect config file edits to sandbox
    if tool_name in ["Write", "Edit"]:
        file_path = input_data.get("file_path", "")
        if "config" in file_path.lower():
            safe_path = f"./sandbox/{file_path}"
            return {
                "behavior": "allow",
                "updatedInput": {**input_data, "file_path": safe_path}
            }

    # Allow read operations
    if tool_name in ["Read", "Grep", "Glob"]:
        return {
            "behavior": "allow",
            "updatedInput": input_data
        }

    # Ask for confirmation on everything else
    return {
        "behavior": "deny",
        "message": f"Tool {tool_name} requires confirmation",
        "interrupt": False
    }

async def main():
    options = ClaudeAgentOptions(
        can_use_tool=custom_permission_handler,
        allowed_tools=["Read", "Write", "Edit", "Grep", "Glob"]
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Update the system config file")

        async for message in client.receive_response():
            if message.type == "result":
                print(f"Done: {message.result}")
                break
```

### Pattern 5: Programmatic Subagents

Define specialized subagents programmatically.

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition

async def main():
    # Define specialized agents
    agents = {
        "code_reviewer": AgentDefinition(
            description="Expert code reviewer that checks for bugs, security issues, and best practices. Use when reviewing code.",
            tools=["Read", "Grep", "Glob"],
            prompt="""You are an expert code reviewer. Focus on:
            1. Security vulnerabilities
            2. Performance issues
            3. Code quality and best practices
            4. Test coverage
            Provide actionable feedback.""",
            model="sonnet"
        ),
        "test_generator": AgentDefinition(
            description="Generates comprehensive test suites. Use when creating tests.",
            tools=["Read", "Write", "Grep", "Glob", "Bash"],
            prompt="""You are a testing expert. Create comprehensive test suites with:
            1. Unit tests
            2. Integration tests
            3. Edge cases
            4. Clear test descriptions""",
            model="sonnet"
        )
    }

    options = ClaudeAgentOptions(
        agents=agents,
        permission_mode="acceptEdits",
        allowed_tools=["Task", "Read", "Write", "Grep", "Glob", "Bash"]
    )

    async with ClaudeSDKClient(options=options) as client:
        # Claude will automatically use the code_reviewer agent
        await client.query("Review the authentication module for security issues")

        async for message in client.receive_response():
            if message.type == "result":
                print(f"Review complete")
                break
```

### Pattern 6: Session Management

Resume, fork, and manage conversation sessions.

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def session_management():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions"
    )

    # Create initial session
    session_id = None
    async with ClaudeSDKClient(options=options) as client:
        await client.query("What is 10 + 5?")

        async for message in client.receive_response():
            if message.type == "system" and message.subtype == "init":
                session_id = message.session_id
                print(f"Session ID: {session_id}")
            elif message.type == "result":
                break

    # Resume session
    options_resume = ClaudeAgentOptions(
        resume=session_id,
        permission_mode="bypassPermissions"
    )

    async with ClaudeSDKClient(options=options_resume) as client:
        await client.query("What was the answer to my previous question?")

        async for message in client.receive_response():
            if message.type == "assistant":
                for block in message.message.content:
                    if hasattr(block, 'text'):
                        print(f"Claude: {block.text}")  # "15"
            elif message.type == "result":
                break

    # Fork session (create branch)
    options_fork = ClaudeAgentOptions(
        resume=session_id,
        fork_session=True,
        permission_mode="bypassPermissions"
    )

    async with ClaudeSDKClient(options=options_fork) as client:
        await client.query("Actually, let's try 10 + 6 instead")

        async for message in client.receive_response():
            if message.type == "result":
                print(f"Forked session complete")
                break

asyncio.run(session_management())
```

### Pattern 7: Loading Project Context (CLAUDE.md)

Load project instructions from CLAUDE.md files.

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def main():
    options = ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code"  # Use Claude Code's system prompt
        },
        setting_sources=["project"],  # Load .claude/CLAUDE.md and CLAUDE.md
        allowed_tools=["Read", "Write", "Edit", "Bash"],
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        # Claude now has access to project-specific instructions from CLAUDE.md
        await client.query("Add a new feature following our project conventions")

        async for message in client.receive_response():
            if message.type == "result":
                break

asyncio.run(main())
```

## TypeScript SDK Patterns

### Pattern 1: Simple Query

```typescript
import { query, ClaudeAgentOptions } from '@anthropic-ai/claude-agent-sdk';

async function simpleQuery() {
  for await (const message of query({
    prompt: "What is 2 + 2?",
    options: {
      permissionMode: 'bypassPermissions',
      allowedTools: []
    }
  })) {
    if (message.type === 'result') {
      console.log('Answer:', message.result);
    }
  }
}

simpleQuery();
```

### Pattern 2: Custom Tools

```typescript
import { tool, createSdkMcpServer, query } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

// Define tools with type-safe schemas
const calculateArea = tool(
  'calculate_area',
  'Calculate area of a rectangle',
  z.object({
    width: z.number(),
    height: z.number()
  }),
  async (args) => {
    const area = args.width * args.height;
    return {
      content: [{
        type: 'text',
        text: `Area: ${area} square units`
      }]
    };
  }
);

const fetchData = tool(
  'fetch_data',
  'Fetch data from API',
  z.object({
    endpoint: z.string(),
    id: z.number()
  }),
  async (args) => {
    // Simulate API call
    const data = { endpoint: args.endpoint, id: args.id, status: 'success' };
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(data, null, 2)
      }]
    };
  }
);

async function main() {
  const server = createSdkMcpServer({
    name: 'my-tools',
    version: '1.0.0',
    tools: [calculateArea, fetchData]
  });

  for await (const message of query({
    prompt: "What's the area of a 5x10 rectangle?",
    options: {
      mcpServers: { 'tools': server },
      allowedTools: ['mcp__tools__calculate_area', 'mcp__tools__fetch_data'],
      permissionMode: 'bypassPermissions'
    }
  })) {
    if (message.type === 'result') {
      console.log('Result:', message.result);
    }
  }
}

main();
```

### Pattern 3: Streaming Input

```typescript
import { query } from '@anthropic-ai/claude-agent-sdk';

async function* messageStream() {
  yield { type: 'text', text: 'Analyze this data:' };
  await new Promise(resolve => setTimeout(resolve, 500));
  yield { type: 'text', text: 'Temperature: 25°C' };
  await new Promise(resolve => setTimeout(resolve, 500));
  yield { type: 'text', text: 'Humidity: 60%' };
  await new Promise(resolve => setTimeout(resolve, 500));
  yield { type: 'text', text: 'What patterns do you see?' };
}

async function main() {
  for await (const message of query({
    prompt: messageStream(),
    options: {
      permissionMode: 'bypassPermissions'
    }
  })) {
    if (message.type === 'assistant') {
      console.log('Claude:', message.message);
    }
  }
}

main();
```

### Pattern 4: Programmatic Agents

```typescript
import { query, AgentDefinition } from '@anthropic-ai/claude-agent-sdk';

async function main() {
  const agents: Record<string, AgentDefinition> = {
    'security_auditor': {
      description: 'Security expert that audits code for vulnerabilities. Use for security reviews.',
      tools: ['Read', 'Grep', 'Glob'],
      prompt: 'You are a security expert. Check for: SQL injection, XSS, CSRF, auth issues, secrets in code.',
      model: 'sonnet'
    },
    'performance_optimizer': {
      description: 'Performance expert that optimizes code. Use for performance issues.',
      tools: ['Read', 'Write', 'Edit', 'Bash'],
      prompt: 'You are a performance expert. Profile code, identify bottlenecks, suggest optimizations.',
      model: 'sonnet'
    }
  };

  for await (const message of query({
    prompt: "Review this codebase for security issues",
    options: {
      agents,
      permissionMode: 'acceptEdits',
      allowedTools: ['Task', 'Read', 'Write', 'Edit', 'Grep', 'Glob', 'Bash']
    }
  })) {
    if (message.type === 'result') {
      console.log('Security audit complete');
    }
  }
}

main();
```

## Common Patterns

### Error Handling

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def with_error_handling():
    try:
        async with ClaudeSDKClient() as client:
            await client.query("complex task")

            async for message in client.receive_response():
                if message.type == "result":
                    if message.subtype == "error_during_execution":
                        print(f"Error occurred during execution")
                    elif message.subtype == "error_max_turns":
                        print(f"Hit max turns limit")
                    break

    except Exception as e:
        print(f"SDK error: {e}")
```

### Cost Monitoring

```python
async def monitor_costs():
    total_cost = 0.0

    async with ClaudeSDKClient() as client:
        await client.query("analyze this project")

        async for message in client.receive_response():
            if message.type == "result":
                cost = message.total_cost_usd
                total_cost += cost
                print(f"Task cost: ${cost:.4f}")
                print(f"Total cost: ${total_cost:.4f}")
                break
```

### Interrupting Long-Running Tasks

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient

async def interruptible_task():
    async with ClaudeSDKClient() as client:
        await client.query("Count from 1 to 1000 slowly")

        # Let it run for a bit
        await asyncio.sleep(5)

        # Interrupt
        await client.interrupt()
        print("Task interrupted!")

        # Send new command
        await client.query("Just say hello instead")

        async for message in client.receive_response():
            if message.type == "result":
                break
```

## Best Practices

### 1. Choose the Right SDK Function

- **`query()`** - Single exchanges, independent tasks
- **`ClaudeSDKClient`** - Continuous conversations, follow-ups

### 2. Set Permission Modes Appropriately

- **`bypassPermissions`** - Fully automated, trusted environments
- **`acceptEdits`** - Auto-approve file edits in controlled scenarios
- **`plan`** - Dry-run mode for testing
- **`default`** - Interactive use (not SDK-friendly)

### 3. Restrict Tools

Always use `allowed_tools` or `disallowed_tools` to limit capabilities:

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob"],  # Read-only
    permission_mode="bypassPermissions"
)
```

### 4. Handle Settings Sources

Control which filesystem settings to load:

```python
# SDK-only (no filesystem dependencies)
options = ClaudeAgentOptions()  # setting_sources defaults to None

# Load project CLAUDE.md files
options = ClaudeAgentOptions(
    setting_sources=["project"],
    system_prompt={"type": "preset", "preset": "claude_code"}
)

# Load all settings (legacy behavior)
options = ClaudeAgentOptions(
    setting_sources=["user", "project", "local"]
)
```

### 5. Monitor Costs

Parse result messages to track token usage and costs:

```python
if message.type == "result":
    print(f"Cost: ${message.total_cost_usd}")
    print(f"Tokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out")
```

### 6. Use Max Turns

Prevent runaway execution:

```python
options = ClaudeAgentOptions(
    max_turns=10  # Limit to 10 conversation turns
)
```

### 7. Implement Timeouts

Use asyncio timeouts for time-critical operations:

```python
import asyncio

try:
    await asyncio.wait_for(process_task(), timeout=300)  # 5 minutes
except asyncio.TimeoutError:
    print("Task timed out")
```

## Quick Reference

### Python

```python
# Simple query
async for msg in query(prompt="task", options=ClaudeAgentOptions(permission_mode="bypassPermissions")):
    if msg.type == "result": print(msg.result)

# Continuous conversation
async with ClaudeSDKClient(options=options) as client:
    await client.query("first question")
    async for msg in client.receive_response():
        if msg.type == "result": break
    await client.query("follow-up")
    async for msg in client.receive_response():
        if msg.type == "result": break

# Custom tool
@tool("name", "description", {"arg": type})
async def handler(args): return {"content": [{"type": "text", "text": "result"}]}

# Create MCP server
server = create_sdk_mcp_server(name="srv", tools=[handler])
```

### TypeScript

```typescript
// Simple query
for await (const msg of query({prompt: "task", options: {permissionMode: 'bypassPermissions'}})) {
  if (msg.type === 'result') console.log(msg.result);
}

// Custom tool
const myTool = tool('name', 'description', z.object({arg: z.string()}), async (args) => ({
  content: [{type: 'text', text: 'result'}]
}));

// Create MCP server
const server = createSdkMcpServer({name: 'srv', tools: [myTool]});
```

## Resources

- **Python SDK Docs**: https://docs.claude.com/en/api/agent-sdk/python
- **TypeScript SDK Docs**: https://docs.claude.com/en/api/agent-sdk/typescript
- **SDK Overview**: https://docs.claude.com/en/api/agent-sdk/overview
- **Python SDK GitHub**: https://github.com/anthropics/claude-agent-sdk-python
- **TypeScript SDK GitHub**: https://github.com/anthropics/claude-agent-sdk-typescript
