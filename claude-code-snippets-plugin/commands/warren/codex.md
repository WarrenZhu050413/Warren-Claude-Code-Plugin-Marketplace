================================
CODEX MCP QUICK REFERENCE
================================

## WHEN TO USE CODEX MCP

**VERIFICATION_HASH:** `b94f600a82d96a33`

- Heavy analytical tasks (plan reviews, architecture analysis, bug investigations)
- Web research (fetch latest docs, articles, best practices)
- Token-intensive work (offload to avoid cluttering main context)
- Deep code analysis across multiple files
- Playwright test debugging and analysis

## THE TWO TOOLS

1. mcp__codex__codex        → Start new session (returns conversationId)
2. mcp__codex__codex-reply  → Continue existing session (requires conversationId)

## STANDARD CONFIGURATION (ALWAYS USE THIS)

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

## CONTINUING CONVERSATIONS

mcp__codex__codex-reply(
    conversationId=conv_id,  # From previous response
    prompt="Follow-up question or next step"
)

## KEY RULES

✅ ALWAYS:
- Use "model": "gpt-5-codex"
- Use "sandbox_mode": "read-only" (analysis only, no writing)
- Use "approval_policy": "never" (can't respond to prompts in MCP)
- Use "model_reasoning_effort": "high"
- Use "model_reasoning_summary": "concise"
- Pass config as inline object (NOT file path)
- Extract conversationId from response for continuation

❌ NEVER:
- Use config="/path/to/file.toml" (causes hanging)
- Use profile="name" (may cause nested spawning)
- Use "workspace-write" or "danger-full-access" (Codex is for analysis)
- Use "model_verbosity" (doesn't work with gpt-5-codex)

## SESSION MANAGEMENT

- Sessions auto-saved to: ~/.codex/sessions/YYYY/MM/DD/*.jsonl
- conversationId is in the tool response - extract it
- Use same conversationId for multi-turn conversations

## TYPICAL USE CASES

1. Research: Enable web_search, ask for latest info/docs
2. Plan Review: Analyze docs, identify gaps, suggest improvements
3. Bug Investigation: Deep dive into code, cross-reference patterns
4. Architecture Analysis: Review structure, propose simplifications
5. Multi-turn Analysis: Extract conv_id, continue with follow-ups
6. Playwright Testing: Analyze test failures, suggest fixes, debug selectors

## EXAMPLE FLOW

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

## PLAYWRIGHT TESTING EXAMPLE

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

================================
END QUICK REFERENCE
================================
