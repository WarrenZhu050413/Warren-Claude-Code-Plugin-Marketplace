# Headless Use Patterns

Comprehensive guide for using Claude Code in non-interactive, automated, and CI/CD environments.

## Overview

Headless mode refers to running Claude Code without interactive user input - perfect for:
- **CI/CD pipelines** - Automated code review, testing, deployment
- **Batch processing** - Process multiple files or tasks sequentially
- **Scripted automation** - Integrate Claude into existing workflows
- **Background tasks** - Long-running operations without user interaction
- **API-like usage** - Use Claude as a service in your applications

## Core Headless Patterns

### 1. One-Shot Commands

Execute a single task and exit - the most common headless pattern.

**Basic usage:**
```bash
claude -p "your prompt here"
```

**With options:**
```bash
# Bypass permissions for automation
claude --permission-mode bypassPermissions -p "update all config files"

# Limit turns for predictable execution
claude --max-turns 5 -p "analyze this codebase"

# Specify working directory
cd /path/to/project && claude -p "run tests"

# Set specific model
claude --model sonnet -p "review code quality"
```

### 2. Structured Output Formats

Get machine-readable output for parsing in scripts.

**Stream JSON** - One JSON object per line, real-time streaming:
```bash
claude --output-format "stream-json" -p "create a function" | jq .
```

**Compact JSON** - Complete response as single JSON:
```bash
claude --output-format "compact-json" -p "what is 2+2?" | jq '.messages[-1].content[0].text'
```

**Compact Text** - Plain text output, no markdown:
```bash
claude --output-format "compact-text" -p "summarize this file" > summary.txt
```

### 3. Session Management

Create, continue, and resume conversations programmatically.

**Capture Session ID:**
```bash
# Method 1: From debug output
OUTPUT=$(claude --debug --output-format "stream-json" -p "first task" 2>&1)
SESSION_ID=$(echo "$OUTPUT" | grep -o '"session_id":"[^"]*"' | head -1 | cut -d'"' -f4)

# Method 2: From debug logs directory
LATEST_SESSION=$(ls -t ~/.claude/debug/ | head -1)
```

**Continue Session:**
```bash
# Continue with explicit session ID
claude -c "$SESSION_ID" -p "follow-up question"

# Continue most recent session
claude -c -p "what did we just discuss?"
```

**Fork Session** (create branch from existing):
```bash
claude --fork-session --resume "$SESSION_ID" -p "try alternative approach"
```

### 4. Permission Modes for Automation

Control tool execution without user prompts.

**`bypassPermissions`** - Auto-approve everything (use with caution):
```bash
claude --permission-mode bypassPermissions -p "update all files"
```

**`acceptEdits`** - Auto-approve file edits only:
```bash
claude --permission-mode acceptEdits -p "refactor this module"
```

**`plan`** - Planning mode, no execution:
```bash
claude --permission-mode plan -p "how would you implement feature X?"
```

**`default`** - Standard permissions (requires interaction):
```bash
claude --permission-mode default -p "make changes"  # Not headless-friendly
```

### 5. Tool Restrictions

Limit which tools Claude can use for safety and predictability.

**Allow specific tools:**
```bash
claude --allowed-tools "Read,Grep,Glob" -p "analyze codebase structure"
```

**Disallow specific tools:**
```bash
claude --disallowed-tools "Bash,Write,Edit" -p "explain this code"
```

**Read-only mode:**
```bash
claude --allowed-tools "Read,Grep,Glob,WebFetch,WebSearch" -p "research topic"
```

## Advanced Headless Patterns

### 6. Batch Processing

Process multiple items sequentially or in parallel.

**Sequential processing:**
```bash
#!/bin/bash
# Process each file one by one

for file in src/**/*.js; do
    echo "Processing: $file"
    claude --permission-mode bypassPermissions \
           --max-turns 3 \
           -p "Review and fix issues in $file" \
           --output-format compact-text > "${file}.review.txt"
done
```

**Parallel processing:**
```bash
#!/bin/bash
# Process files in parallel (use with caution)

find src -name "*.ts" | xargs -P 4 -I {} bash -c '
    claude --permission-mode bypassPermissions \
           --max-turns 2 \
           -p "Type-check and fix {}" \
           --output-format compact-text > {}.log
'
```

### 7. CI/CD Integration

Use Claude in continuous integration pipelines.

**GitHub Actions example:**
```yaml
name: Claude Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Review PR
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Install Claude Code
          curl -fsSL https://claude.ai/install.sh | sh

          # Run review
          claude --permission-mode bypassPermissions \
                 --allowed-tools "Read,Grep,Glob" \
                 --max-turns 5 \
                 --output-format compact-text \
                 -p "Review this PR for code quality and security issues" \
                 > review.md

      - name: Post review
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: review
            });
```

### 8. Error Handling and Retries

Handle failures gracefully in automation.

**With timeout:**
```bash
timeout 300 claude --max-turns 10 -p "complex task" || echo "Task timed out"
```

**With retries:**
```bash
#!/bin/bash
MAX_RETRIES=3
ATTEMPT=1

while [ $ATTEMPT -le $MAX_RETRIES ]; do
    echo "Attempt $ATTEMPT of $MAX_RETRIES"

    if claude --permission-mode bypassPermissions \
              --max-turns 5 \
              -p "potentially failing task"; then
        echo "Success!"
        exit 0
    fi

    ATTEMPT=$((ATTEMPT + 1))
    sleep 5
done

echo "Failed after $MAX_RETRIES attempts"
exit 1
```

### 9. Output Parsing and Validation

Extract specific information from Claude's responses.

**Parse JSON output:**
```bash
# Extract specific fields
RESULT=$(claude --output-format "stream-json" -p "analyze data" 2>/dev/null | \
         jq -r 'select(.type == "result") | .result')

# Count tokens used
TOKENS=$(claude --output-format "stream-json" -p "task" 2>/dev/null | \
         jq -r 'select(.type == "result") | .usage.input_tokens')

# Extract cost
COST=$(claude --output-format "stream-json" -p "task" 2>/dev/null | \
       jq -r 'select(.type == "result") | .total_cost_usd')
```

**Validate output:**
```bash
# Check if task succeeded
claude --output-format "compact-text" -p "run tests" > output.txt
if grep -q "FAILED" output.txt; then
    echo "Tests failed!"
    exit 1
fi
```

### 10. Programmatic Input Streaming

Stream input to Claude dynamically (requires SDK - see Agent SDK Patterns).

## Headless Best Practices

### Safety

1. **Always use `--max-turns`** - Prevent runaway execution
2. **Set timeouts** - Use `timeout` command to limit runtime
3. **Restrict tools** - Use `--allowed-tools` to limit capabilities
4. **Test in sandbox** - Try commands in isolated environment first
5. **Monitor costs** - Parse JSON output to track token usage

### Reliability

1. **Handle errors** - Check exit codes and output for failures
2. **Implement retries** - Transient failures may succeed on retry
3. **Log everything** - Save output for debugging
4. **Use debug mode** - `--debug` saves full traces to `~/.claude/debug/`
5. **Validate output** - Don't assume success, verify results

### Performance

1. **Use compact outputs** - `compact-json` or `compact-text` reduce overhead
2. **Limit turns** - `--max-turns` reduces API calls
3. **Bypass permissions** - Avoid interactive prompts with `--permission-mode bypassPermissions`
4. **Disable unnecessary tools** - Reduce context and overhead
5. **Batch related tasks** - Combine multiple operations in one prompt

## Common Use Cases

### Code Review Automation

```bash
#!/bin/bash
# Automated code review script

PR_FILES=$(git diff --name-only main...HEAD)

claude --permission-mode bypassPermissions \
       --allowed-tools "Read,Grep,Glob" \
       --max-turns 3 \
       --output-format compact-text \
       -p "Review these files for issues: $PR_FILES.
           Focus on: security, performance, best practices." \
       > code_review.md
```

### Test Generation

```bash
# Generate tests for all untested files
claude --permission-mode acceptEdits \
       --max-turns 5 \
       -p "Find files without tests and create comprehensive test suites"
```

### Documentation Generation

```bash
# Auto-generate documentation
claude --permission-mode acceptEdits \
       --allowed-tools "Read,Write,Grep,Glob" \
       --max-turns 10 \
       -p "Generate API documentation for all public functions in src/"
```

### Dependency Updates

```bash
# Update and test dependencies
claude --permission-mode bypassPermissions \
       --max-turns 15 \
       -p "Update package.json dependencies to latest stable versions,
           run tests, and fix any breaking changes"
```

### Security Scanning

```bash
# Scan for security issues
claude --allowed-tools "Read,Grep,Glob,WebSearch" \
       --max-turns 5 \
       --output-format compact-json \
       -p "Scan codebase for security vulnerabilities.
           Check for: SQL injection, XSS, hardcoded secrets, etc." | \
       jq -r '.messages[-1].content[0].text' > security_report.md
```

## Debugging Headless Runs

### Enable Debug Mode

```bash
# Full debug output
claude --debug --verbose -p "task"

# Debug logs saved to ~/.claude/debug/{session_id}/
ls -lth ~/.claude/debug/
```

### Analyze Debug Logs

```bash
# Find latest session
LATEST=$(ls -t ~/.claude/debug/ | head -1)

# View full logs
cat ~/.claude/debug/$LATEST/*

# Search for errors
grep -i "error" ~/.claude/debug/$LATEST/*

# Check tool usage
grep -A5 "tool_name" ~/.claude/debug/$LATEST/*

# Verify permissions
grep "permission" ~/.claude/debug/$LATEST/*
```

### Common Issues

**Problem: Command hangs**
- Solution: Add `--max-turns` to limit execution
- Solution: Use `timeout` command: `timeout 300 claude -p "..."`

**Problem: Unexpected output**
- Solution: Use `--output-format "stream-json"` and parse with `jq`
- Solution: Enable `--debug` to see full execution trace

**Problem: Permission prompts**
- Solution: Use `--permission-mode bypassPermissions` or `acceptEdits`
- Solution: Restrict tools with `--allowed-tools`

**Problem: High costs**
- Solution: Use `--max-turns` to limit iterations
- Solution: Parse JSON output to monitor `total_cost_usd` field

## Environment Variables

Set defaults for headless use:

```bash
# Set API key
export ANTHROPIC_API_KEY="your-api-key"

# Use Bedrock
export CLAUDE_CODE_USE_BEDROCK=1

# Use Vertex AI
export CLAUDE_CODE_USE_VERTEX=1

# Set default model
export CLAUDE_MODEL="claude-sonnet-4-5"

# Set default permission mode
export CLAUDE_PERMISSION_MODE="acceptEdits"
```

## Quick Reference

```bash
# One-shot with JSON output
claude --output-format "stream-json" -p "task" | jq .

# Headless automation
claude --permission-mode bypassPermissions --max-turns 5 -p "task"

# Capture session for continuation
SESSION=$(claude --debug -p "task" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
claude -c "$SESSION" -p "continue"

# Read-only analysis
claude --allowed-tools "Read,Grep,Glob" --max-turns 3 -p "analyze"

# CI/CD code review
claude --permission-mode bypassPermissions \
       --allowed-tools "Read,Grep,Glob" \
       --max-turns 5 \
       --output-format compact-text \
       -p "review code" > review.md

# Monitor costs
claude --output-format "stream-json" -p "task" | \
  jq -r 'select(.type == "result") | .total_cost_usd'
```
