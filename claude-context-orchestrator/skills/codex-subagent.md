# Codex Subagent

Use OpenAI Codex (gpt-5.3-codex) as a subagent for hard infrastructure bugs and complex debugging tasks.

## When to Use

- Hard infrastructure bugs Opus isn't solving
- Complex multi-file debugging
- When you need a second opinion from a different model
- Robust backend/infra code that needs extra reasoning

## Configuration

MCP servers configured in `~/.mcp.json`:
- `codex` — gpt-5.3-codex with high reasoning effort
- `codex-xhigh` — gpt-5.3-codex with xhigh reasoning effort (more thorough)

## Async Pattern

For long-running Codex tasks, use the async wrapper:

```bash
# Start a task in background
~/.claude/scripts/codex-async.sh start <task_id> "<prompt>" [high|xhigh]

# Check if done
~/.claude/scripts/codex-async.sh check <task_id>

# Wait for result (blocking)
~/.claude/scripts/codex-async.sh wait <task_id> [timeout_seconds]

# Get output
~/.claude/scripts/codex-async.sh output <task_id>

# List all tasks
~/.claude/scripts/codex-async.sh list

# Clean up
~/.claude/scripts/codex-async.sh clean
```

## Example Usage

### Via MCP (if available)
When MCP is connected, Codex tools will appear. Use them for:
- File editing
- Code generation
- Debugging

### Via Async Script (recommended for long tasks)
```bash
# Start Codex investigating a bug
~/.claude/scripts/codex-async.sh start bug-123 "Investigate why the MySQL connection pool is exhausting. Check src/sql/executor.ts and related files. The error is: Connection timeout after 30s" xhigh

# Meanwhile, do other work...

# Check status
~/.claude/scripts/codex-async.sh check bug-123

# Get result when done
~/.claude/scripts/codex-async.sh output bug-123
```

## Codex vs Opus

| Aspect | Codex 5.3 | Opus 4.5 |
|--------|-----------|----------|
| Best for | Robust infra code, hard bugs | Smooth UX, taste, creativity |
| Reasoning | xhigh = very thorough | Extended thinking |
| Verbosity | Less verbose | More verbose |
| Speed | Slower at xhigh | Faster |

## Tips

1. **Use xhigh for hard bugs** — worth the extra time
2. **Provide context** — include file paths and error messages
3. **Let it work** — Codex benefits from longer reasoning time
4. **Check periodically** — use async pattern for long tasks
