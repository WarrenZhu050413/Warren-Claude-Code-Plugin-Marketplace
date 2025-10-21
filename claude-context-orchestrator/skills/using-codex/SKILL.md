---
name: using-codex
description: Using Codex MCP for deep analysis, multi-step research, and complex analytical tasks. Use when heavy analytical work, plan reviews, architecture analysis, bug investigations, autonomous multi-step research, or web research is needed. Keywords - codex, analysis, research, investigation, playwright, testing, debug
---

# Using Codex

## Purpose

This skill provides guidance for using Codex MCP to offload heavy analytical and research tasks. Codex is a powerful tool for deep code analysis, multi-step research, and token-intensive work that should not clutter the main conversation context.

## When to Use Codex MCP

Use Codex MCP for:

- **Heavy analytical tasks** - Plan reviews, architecture analysis, bug investigations
- **Web research** - Fetch latest docs, articles, best practices
- **Token-intensive work** - Offload to avoid cluttering main context
- **Deep code analysis** - Cross-reference patterns across multiple files
- **Playwright test debugging** - Analyze test failures, suggest fixes, debug selectors
- **Multi-step autonomous research** - Let Codex explore and report back

## The Two Tools

1. **mcp__codex__codex** - Start new session (returns conversationId)
2. **mcp__codex__codex-reply** - Continue existing session (requires conversationId)

## Standard Configuration

ALWAYS use this configuration pattern:

```python
result = mcp__codex__codex(
    prompt="Your analytical task here",
    config={
        "tools": {"web_search": true},           # Add for research tasks
        "model": "gpt-5-codex",                  # ALWAYS gpt-5-codex
        "approval_policy": "never",              # REQUIRED for MCP
        "sandbox_mode": "read-only",             # ALWAYS read-only
        "model_reasoning_effort": "high",        # ALWAYS high
        "model_reasoning_summary": "concise"     # ALWAYS concise
    }
)

# Extract conversationId (returned by the tool)
conv_id = result["conversationId"]
```

## Continuing Conversations

```python
mcp__codex__codex-reply(
    conversationId=conv_id,  # From previous response
    prompt="Follow-up question or next step"
)
```

## Key Rules

**ALWAYS:**
- Use `"model": "gpt-5-codex"`
- Use `"sandbox_mode": "read-only"` (analysis only, no writing)
- Use `"approval_policy": "never"` (can't respond to prompts in MCP)
- Use `"model_reasoning_effort": "high"`
- Use `"model_reasoning_summary": "concise"`
- Pass config as inline object (NOT file path)
- Extract conversationId from response for continuation

**NEVER:**
- Use `config="/path/to/file.toml"` (causes hanging)
- Use `profile="name"` (may cause nested spawning)
- Use `"workspace-write"` or `"danger-full-access"` (Codex is for analysis)
- Use `"model_verbosity"` (doesn't work with gpt-5-codex)

## Session Management

- Sessions auto-saved to: `~/.codex/sessions/YYYY/MM/DD/*.jsonl`
- conversationId is in the tool response - extract it
- Use same conversationId for multi-turn conversations

## Typical Use Cases

### 1. Research
Enable web_search, ask for latest info/docs

```python
result = mcp__codex__codex(
    prompt="Research latest best practices for X and summarize key findings",
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

### 2. Plan Review
Analyze docs, identify gaps, suggest improvements

```python
result = mcp__codex__codex(
    prompt="Review the project plan in docs/ and identify gaps or inconsistencies",
    config={
        "tools": {"web_search": false},
        "model": "gpt-5-codex",
        "approval_policy": "never",
        "sandbox_mode": "read-only",
        "model_reasoning_effort": "high",
        "model_reasoning_summary": "concise"
    }
)
```

### 3. Bug Investigation
Deep dive into code, cross-reference patterns

```python
result = mcp__codex__codex(
    prompt="Investigate why feature X is failing. Check src/ for related patterns",
    config={
        "tools": {"web_search": false},
        "model": "gpt-5-codex",
        "approval_policy": "never",
        "sandbox_mode": "read-only",
        "model_reasoning_effort": "high",
        "model_reasoning_summary": "concise"
    }
)
```

### 4. Architecture Analysis
Review structure, propose simplifications

```python
result = mcp__codex__codex(
    prompt="Analyze the codebase architecture and suggest simplifications",
    config={
        "tools": {"web_search": false},
        "model": "gpt-5-codex",
        "approval_policy": "never",
        "sandbox_mode": "read-only",
        "model_reasoning_effort": "high",
        "model_reasoning_summary": "concise"
    }
)
```

### 5. Multi-turn Analysis
Extract conv_id, continue with follow-ups

```python
# Start analysis
result = mcp__codex__codex(
    prompt="Analyze X and identify issues",
    config={
        "tools": {"web_search": true},
        "model": "gpt-5-codex",
        "approval_policy": "never",
        "sandbox_mode": "read-only",
        "model_reasoning_effort": "high",
        "model_reasoning_summary": "concise"
    }
)

# Continue with follow-up
conv_id = result["conversationId"]
mcp__codex__codex-reply(
    conversationId=conv_id,
    prompt="Now propose solutions for issue #2"
)
```

### 6. Playwright Testing
Analyze test failures, suggest fixes, debug selectors

```python
# Analyze test failure
result = mcp__codex__codex(
    prompt="Analyze this Playwright test failure: [paste error/trace]. Review tests/hypertext-demo.spec.mjs and suggest fixes.",
    config={
        "tools": {"web_search": false},
        "model": "gpt-5-codex",
        "approval_policy": "never",
        "sandbox_mode": "read-only",
        "model_reasoning_effort": "high",
        "model_reasoning_summary": "concise"
    }
)

# Ask for specific selector improvements
conv_id = result["conversationId"]
mcp__codex__codex-reply(
    conversationId=conv_id,
    prompt="Suggest more robust selectors for the tooltip element"
)
```

## Best Practices

1. **Use web_search selectively** - Only enable when you need external research
2. **Extract conversationId immediately** - Store it for follow-up queries
3. **Keep prompts focused** - Codex works best with clear, specific tasks
4. **Use multi-turn for complex analysis** - Break down big tasks into steps
5. **Stay in read-only mode** - Codex is for analysis, not implementation
6. **Let Codex explore autonomously** - Trust it to navigate codebases and docs
7. **Use for token-heavy work** - Offload big analysis to keep main context clean
