---
name: using-codex
description: Using Codex MCP for deep analysis, multi-step research, and complex analytical tasks. Use when heavy analytical work, plan reviews, architecture analysis, bug investigations, autonomous multi-step research, or web research is needed. Keywords - codex, analysis, research, investigation, playwright, testing, debug
---

# Using Codex

Codex MCP offloads heavy analytical and research tasks to keep main conversation context clean.

## When to Use

- Heavy analysis (plan reviews, architecture, bugs)
- Web research (latest docs, best practices)
- Deep code analysis across multiple files
- Playwright test debugging
- Multi-step autonomous research

## Tools

**mcp__codex__codex** - Start session (returns conversationId)
**mcp__codex__codex-reply** - Continue session (needs conversationId)

## Standard Config

```python
result = mcp__codex__codex(
    prompt="Your task",
    config={
        "tools": {"web_search": true},           # Optional
        "model": "gpt-5-codex",                  # Required
        "approval_policy": "never",              # Required
        "sandbox_mode": "read-only",             # Required
        "model_reasoning_effort": "high",        # Required
        "model_reasoning_summary": "concise"     # Required
    }
)
conv_id = result["conversationId"]
```

## Key Rules

**Always:**
- `"model": "gpt-5-codex"`
- `"sandbox_mode": "read-only"`
- `"approval_policy": "never"`
- `"model_reasoning_effort": "high"`
- `"model_reasoning_summary": "concise"`
- Inline config object

**Never:**
- `config="/path/to/file.toml"` (hangs)
- `profile="name"` (causes nesting)
- `"workspace-write"` (analysis only)

## Use Cases

### Research
```python
result = mcp__codex__codex(
    prompt="Research X best practices",
    config={
        "tools": {"web_search": true},
        "model": "gpt-5-codex",
        "approval_policy": "never",
        "sandbox_mode": "read-only",
        "model_reasoning_effort": "high",
        "model_reasoning_summary": "concise"
    }
)
```

### Plan Review
```python
result = mcp__codex__codex(
    prompt="Review docs/ for gaps",
    config={
        "model": "gpt-5-codex",
        "approval_policy": "never",
        "sandbox_mode": "read-only",
        "model_reasoning_effort": "high",
        "model_reasoning_summary": "concise"
    }
)
```

### Multi-turn
```python
# Start
result = mcp__codex__codex(
    prompt="Analyze X",
    config={...}
)

# Continue
conv_id = result["conversationId"]
mcp__codex__codex-reply(
    conversationId=conv_id,
    prompt="Now do Y"
)
```

## Sessions

Auto-saved: `~/.codex/sessions/YYYY/MM/DD/*.jsonl`
