---
name: using-codex
description: Using Codex CLI (`codex exec`) for testing and automation. Focus on gpt-5-codex with different reasoning efforts, web search, streaming, and multi-turn conversations.
---

# Using Codex for Testing & Automation

**Always use `gpt-5-codex` with different reasoning efforts.** Never use o3 or 4o.

**⚠️ IMPORTANT: Git Repository Requirement**
- Codex requires a Git repository by default to prevent destructive changes
- **If NOT in a git repo**: Add `--skip-git-repo-check` to every command
- **If IN a git repo**: Git check passes automatically

```bash
# In git repo - works fine
codex exec --model gpt-5-codex "task"

# NOT in git repo - need flag
codex exec --model gpt-5-codex --skip-git-repo-check "task"
```

## Official Documentation

- **Main Repo**: https://github.com/openai/codex
- **Non-interactive Mode**: https://github.com/openai/codex/blob/main/docs/exec.md
- **Config Guide**: https://github.com/openai/codex/blob/main/docs/config.md
- **Sandbox & Approvals**: https://github.com/openai/codex/blob/main/docs/sandbox.md

## Core Patterns

**Note**: All examples assume you're in a git repo. If not, add `--skip-git-repo-check` to every command.

### 1. Basic Execution (Read-Only)

```bash
# In git repo
codex exec --model gpt-5-codex "analyze test failures"

# Not in git repo
codex exec --model gpt-5-codex --skip-git-repo-check "analyze test failures"
```

### 2. With File Edits (Workspace-Write)

```bash
# In git repo
codex exec --model gpt-5-codex --full-auto "fix failing tests"

# Not in git repo
codex exec --model gpt-5-codex --skip-git-repo-check --full-auto "fix failing tests"
```

### 3. With Web Search (Critical for Up-to-Date Info)

```bash
# In git repo
codex exec \
  --model gpt-5-codex \
  --config tools.web_search=true \
  "research best practices for async Rust and apply to this codebase"

# Not in git repo
codex exec \
  --model gpt-5-codex \
  --skip-git-repo-check \
  --config tools.web_search=true \
  "research best practices for async Rust and apply to this codebase"
```

### 4. Streaming Output (JSON Lines)

```bash
# Stream events as they happen
codex exec --model gpt-5-codex --json "run all tests" > output.jsonl

# Watch in real-time
codex exec --model gpt-5-codex --json "analyze errors" | jq -r '.type'
```

Event types you'll see:
- `thread.started` - session begins (contains `thread_id`)
- `turn.started` - agent starts processing
- `item.completed` - reasoning, commands, file changes
- `turn.completed` - includes token usage

### 5. Multi-Turn Conversations (Save Conversation ID)

```bash
# First turn - save JSON output
codex exec --model gpt-5-codex --json "run tests" 2>&1 > output.jsonl

# Extract thread_id
cat output.jsonl | jq -r 'select(.type=="thread.started") | .thread_id' > thread_id.txt

# Resume with the same conversation (note: --model not needed for resume)
THREAD_ID=$(cat thread_id.txt)
echo "fix those failures" | codex exec resume $THREAD_ID
echo "verify all tests pass now" | codex exec resume $THREAD_ID

# Or just resume last session (no thread_id needed)
echo "now check code coverage" | codex exec resume --last
```

## Reasoning Effort Configuration

**Always use `gpt-5-codex`** - adjust reasoning effort based on task complexity:

### Quick Tasks (Low Reasoning)

```bash
codex exec \
  --model gpt-5-codex \
  --config model_reasoning_effort=low \
  "run pytest and report failures"
```

### Standard Tasks (Medium Reasoning - Default)

```bash
codex exec \
  --model gpt-5-codex \
  --config model_reasoning_effort=medium \
  "analyze test failures and suggest fixes"
```

### Complex Tasks (High Reasoning)

```bash
codex exec \
  --model gpt-5-codex \
  --config model_reasoning_effort=high \
  "debug race condition in concurrent tests"
```

### Deep Analysis (Detailed Reasoning Summary)

```bash
codex exec \
  --model gpt-5-codex \
  --config model_reasoning_effort=high \
  --config model_reasoning_summary=detailed \
  "analyze architecture for security vulnerabilities"
```

## Sandbox Modes

### read-only (Default - Safest)

```bash
codex exec --model gpt-5-codex "analyze code coverage"
```

### workspace-write (Allow File Edits)

```bash
codex exec --model gpt-5-codex --full-auto "fix type errors"
# Or explicitly:
codex exec --model gpt-5-codex --sandbox workspace-write "fix errors"
```

### danger-full-access (Full Disk + Network)

```bash
codex exec \
  --model gpt-5-codex \
  --sandbox danger-full-access \
  "run integration tests against staging"
```

## Command-Line Configuration (Flexible)

**Use `--config key=value` for maximum flexibility.** Don't use profiles.

### Multiple Configs in One Command

```bash
codex exec \
  --model gpt-5-codex \
  --config model_reasoning_effort=high \
  --config model_reasoning_summary=detailed \
  --config tools.web_search=true \
  --config approval_policy=never \
  --config hide_agent_reasoning=true \
  "research and implement caching strategy"
```

### Common Config Combinations

```bash
# CI/CD: fast, no prompts, hide reasoning
codex exec \
  --model gpt-5-codex \
  --config model_reasoning_effort=low \
  --config approval_policy=never \
  --config hide_agent_reasoning=true \
  "run test suite"

# Deep analysis: high reasoning, web search, detailed summary
codex exec \
  --model gpt-5-codex \
  --config model_reasoning_effort=high \
  --config model_reasoning_summary=detailed \
  --config tools.web_search=true \
  "analyze security of authentication flow"

# File editing: workspace-write, medium reasoning
codex exec \
  --model gpt-5-codex \
  --full-auto \
  --config model_reasoning_effort=medium \
  "refactor database module for better testability"
```

## Structured Output (JSON Schema)

Get structured data back:

```bash
# Define schema
cat > schema.json << 'EOF'
{
  "type": "object",
  "properties": {
    "test_failures": {
      "type": "array",
      "items": {"type": "string"}
    },
    "coverage_percent": {"type": "number"},
    "needs_attention": {
      "type": "array",
      "items": {"type": "string"}
    }
  },
  "required": ["test_failures", "coverage_percent"],
  "additionalProperties": false
}
EOF

# Get structured output
codex exec \
  --model gpt-5-codex \
  --output-schema schema.json \
  "analyze test suite" -o results.json

# Parse results
cat results.json | jq '.test_failures'
```

## Web Search (Important!)

**Enable web search for up-to-date information:**

```bash
# Research latest best practices
codex exec \
  --model gpt-5-codex \
  --config tools.web_search=true \
  --config model_reasoning_effort=medium \
  "research 2025 best practices for React testing and apply here"

# Find current library versions
codex exec \
  --model gpt-5-codex \
  --config tools.web_search=true \
  "check if we're using latest stable versions of dependencies"

# Debug with latest docs
codex exec \
  --model gpt-5-codex \
  --full-auto \
  --config tools.web_search=true \
  --config model_reasoning_effort=high \
  "research this error message and fix it"
```

## Streaming + Multi-Turn Pattern

**Powerful pattern for complex workflows:**

```bash
#!/bin/bash
# Complex multi-turn workflow with streaming

# Turn 1: Initial analysis
echo "=== Turn 1: Analyzing Tests ==="
codex exec \
  --model gpt-5-codex \
  --json \
  --config model_reasoning_effort=medium \
  "run all tests and analyze failures" 2>&1 > turn1.jsonl

# Extract thread_id
THREAD_ID=$(cat turn1.jsonl | jq -r 'select(.type=="thread.started") | .thread_id')
echo "Thread ID: $THREAD_ID"

# Turn 2: Fix failures
echo -e "\n=== Turn 2: Fixing Failures ==="
echo "fix all test failures" | codex exec \
  --json \
  --full-auto \
  --config model_reasoning_effort=high \
  resume $THREAD_ID 2>&1 > turn2.jsonl

# Turn 3: Verify fixes
echo -e "\n=== Turn 3: Verifying Fixes ==="
echo "run tests again and confirm all pass" | codex exec \
  --json \
  resume $THREAD_ID 2>&1 > turn3.jsonl

# Extract final result
echo -e "\n=== Final Result ==="
cat turn3.jsonl | jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text' | tail -1
```

## Practical Examples

### Example 1: CI/CD Test Runner

```bash
# Fast, no prompts, structured output
codex exec \
  --model gpt-5-codex \
  --config model_reasoning_effort=low \
  --config approval_policy=never \
  --config hide_agent_reasoning=true \
  --output-schema test-schema.json \
  "run pytest and extract results" -o ci-results.json
```

### Example 2: Deep Debugging Session

```bash
# High reasoning, web search, multi-turn
codex exec \
  --model gpt-5-codex \
  --json \
  --config model_reasoning_effort=high \
  --config model_reasoning_summary=detailed \
  --config tools.web_search=true \
  "analyze this segfault and research solutions" 2>&1 > debug.jsonl

# Extract thread_id
THREAD_ID=$(cat debug.jsonl | jq -r 'select(.type=="thread.started") | .thread_id')

# Continue debugging
echo "apply the fix" | codex exec --full-auto resume $THREAD_ID
echo "verify it's resolved" | codex exec resume $THREAD_ID
```

### Example 3: Research + Implementation

```bash
# Enable web search for research
codex exec \
  --model gpt-5-codex \
  --full-auto \
  --config model_reasoning_effort=high \
  --config tools.web_search=true \
  "research current best practices for rate limiting APIs and implement for our endpoints"
```

### Example 4: Streaming Progress Monitor

```bash
# Monitor progress in real-time
codex exec \
  --model gpt-5-codex \
  --json \
  --full-auto \
  --config model_reasoning_effort=medium \
  "refactor authentication module" 2>&1 \
  | jq -r 'select(.type=="item.completed") |
    "\(.item.type): \(if .item.type == "agent_message" then .item.text elif .item.type == "command_execution" then .item.command else .item.type end)"'
```

## Key Configuration Options

```bash
# Model (always this)
--model gpt-5-codex

# Git repo requirement
--skip-git-repo-check                     # bypass git repo requirement

# Reasoning effort (adjust per task)
--config model_reasoning_effort=low       # quick tasks
--config model_reasoning_effort=medium    # default
--config model_reasoning_effort=high      # complex tasks

# Reasoning summary (more detail)
--config model_reasoning_summary=concise  # default
--config model_reasoning_summary=detailed # verbose explanations

# Web search (important!)
--config tools.web_search=true            # enable web access

# Approval policy
--config approval_policy=never            # fully autonomous (CI/CD)
--config approval_policy=on-request       # model decides (default)

# Hide reasoning in logs
--config hide_agent_reasoning=true        # cleaner output

# Sandbox
--sandbox read-only                       # default (safe)
--sandbox workspace-write                 # or --full-auto
--sandbox danger-full-access              # full access
```

## Environment Variables

```bash
# Override API key
CODEX_API_KEY=sk-... codex exec --model gpt-5-codex "task"

# Custom home directory
CODEX_HOME=~/.codex-ci codex exec --model gpt-5-codex "task"
```

## Output Modes

```bash
# Default: activity to stderr, final message to stdout
codex exec --model gpt-5-codex "task"

# JSON streaming
codex exec --model gpt-5-codex --json "task" > output.jsonl

# Structured output
codex exec --model gpt-5-codex --output-schema schema.json "task" -o out.json

# Save to file
codex exec --model gpt-5-codex "task" -o result.txt
```

## Quick Reference

**⚠️ Add `--skip-git-repo-check` if NOT in a git repository**

```bash
# Basic (read-only)
codex exec --model gpt-5-codex "analyze code"

# With edits
codex exec --model gpt-5-codex --full-auto "fix errors"

# With web search (important!)
codex exec --model gpt-5-codex --config tools.web_search=true "research and implement feature"

# High reasoning
codex exec --model gpt-5-codex --config model_reasoning_effort=high "debug complex issue"

# Streaming
codex exec --model gpt-5-codex --json "task" > output.jsonl

# Multi-turn
codex exec --model gpt-5-codex --json "step 1" 2>&1 > out.jsonl
THREAD_ID=$(cat out.jsonl | jq -r 'select(.type=="thread.started") | .thread_id')
echo "step 2" | codex exec resume $THREAD_ID

# Outside git repo - add this flag to all commands
codex exec --model gpt-5-codex --skip-git-repo-check "task"
```

## Learning from GitHub Issues

Use `gh` CLI to find real-world examples:

```bash
# Search for exec examples
gh issue list -R openai/codex -S "codex exec" -L 20

# Find web search examples
gh issue list -R openai/codex -S "web_search" -L 10

# Streaming issues
gh issue list -R openai/codex -S "--json" -L 10

# Multi-turn conversation examples
gh issue list -R openai/codex -S "resume" -L 10

# View specific issue
gh issue view ISSUE_NUMBER -R openai/codex

# Search for working configs
gh search code -R openai/codex "codex exec" --extension yml
gh search code -R openai/codex "config.toml" --extension toml

# Find hot topics (most discussed)
gh api 'repos/openai/codex/issues?sort=comments&direction=desc&per_page=10' \
  | jq -r '.[] | "#\(.number) (\(.comments) comments): \(.title)"'

# Get comments from an issue
gh api repos/openai/codex/issues/ISSUE_NUMBER/comments \
  | jq -r '.[] | "\(.user.login): \(.body)\n---"'

# Latest releases
gh release list -R openai/codex --limit 10
gh release view -R openai/codex

# Recent activity
gh issue list -R openai/codex --state open --limit 20
gh issue list -R openai/codex --state closed --limit 20
```

## Additional Resources

- **TypeScript SDK**: https://github.com/openai/codex/tree/main/sdk/typescript
- **GitHub Action**: https://github.com/openai/codex-action
- **FAQ**: https://github.com/openai/codex/blob/main/docs/faq.md
