# Debugging Claude Code

Comprehensive guide for testing and debugging Claude Code modifications including hooks, plugins, snippets, and configurations.

---

## Overview

This guide helps you test modifications to Claude Code itself using the `claude` CLI with debug mode. Use this when:
- Testing hook configurations
- Debugging snippet injection
- Verifying plugin functionality
- Validating configuration changes

---

## Key Testing Commands

### 1. One-Shot Testing with Debug Mode

Test modifications without entering interactive mode.

**Basic debug test:**
```bash
claude --debug -p "your test prompt here"
```

**Structured JSON output for parsing:**
```bash
claude --debug --verbose --output-format "stream-json" -p "test prompt" | jq .
```

**Test with specific working directory:**
```bash
cd /path/to/test/directory
claude --debug -p "test prompt"
```

**Test hook triggers:**
```bash
claude --debug -p "keyword that triggers hook"
```

### Why `--debug`?

The `--debug` flag provides:
- **Debug logs** written to `~/.claude/debug/{session_id}/`
- **System initialization** details (tools, MCP servers, slash commands)
- **Session ID** revelation for conversation continuation
- **Hook execution** traces (pattern matching, script paths)
- **Complete execution trace** for post-mortem analysis

### Debug Output Structure

```json
{
  "type": "system",
  "subtype": "init",
  "cwd": "/working/directory",
  "session_id": "f4abda12-6884-44f2-ae60-228eeb924482",
  "tools": ["Task", "Bash", "Read", "Write", ...],
  "mcp_servers": [{"name": "exa", "status": "connected"}],
  "model": "claude-sonnet-4-5-20250929",
  "slash_commands": ["exp-create", "exp-list", ...]
}
```

### Debug Logs Location

**Path:** `~/.claude/debug/{session_id}/`

**Contents:**
- Complete conversation transcript
- Hook execution details
- Tool calls and responses
- Error traces and warnings

---

## 2. Continue Conversation After One-Shot

You can continue conversations from one-shot commands using the session_id.

**Capture session_id:**
```bash
# Method 1: From debug output
claude --debug --verbose --output-format "stream-json" -p "test my hook" | jq . > /tmp/debug.json
SESSION_ID=$(jq -r '.session_id' /tmp/debug.json | head -1)

# Method 2: From stderr
SESSION_ID=$(claude --debug -p "hi" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
```

**Continue conversation with session_id:**
```bash
# Continue with specific session
claude --debug -p "did the hook work?" -c "$SESSION_ID"

# Continue most recent conversation
claude -c

# Another one-shot using same session
claude --debug --verbose --output-format "stream-json" -p "test another aspect" -c "$SESSION_ID" | jq .
```

**Use cases:**
- Initial automated test, then manual exploration
- Scripted test sequences with conversation memory
- Iterative debugging workflows across multiple commands
- Verify hook effects persist across conversation turns

---

## 3. Debug Logs Deep Dive

Debug logs contain complete execution traces for detailed post-mortem analysis.

**List all debug sessions:**
```bash
ls -lth ~/.claude/debug/ | head -20
```

**Find most recent session:**
```bash
LATEST=$(ls -t ~/.claude/debug/ | head -1)
echo "Latest session: $LATEST"
```

**View complete logs:**
```bash
cat ~/.claude/debug/$LATEST/*
```

**Search for specific patterns:**
```bash
grep -r "UserPromptSubmit" ~/.claude/debug/$LATEST/
grep -r "SNIPPET_NAME" ~/.claude/debug/$LATEST/
grep -r "hook.*matched" ~/.claude/debug/$LATEST/
```

**Monitor logs in real-time:**
```bash
tail -f ~/.claude/debug/$LATEST/*
```

**Extract key information:**
```bash
cat ~/.claude/debug/$LATEST/* | grep -E "(session_id|tools|mcp_servers|slash_commands)"
```

### What's in Debug Logs

- **System initialization** - Session ID, working directory, available tools
- **MCP server status** - Which servers connected/failed
- **Tool calls** - Every tool invoked with parameters and responses
- **Hook execution** - Pattern matching, script paths, output
- **Error traces** - Complete stack traces for debugging
- **Conversation turns** - Full request/response cycle

### Debug Log Analysis Example

```bash
# Scenario: Testing if a snippet injection worked

# 1. Run test and capture session_id
OUTPUT=$(claude --debug --verbose --output-format "stream-json" -p "docker help" | jq .)
SESSION_ID=$(echo "$OUTPUT" | jq -r 'select(.session_id != null) | .session_id' | head -1)

# 2. Check if UserPromptSubmit hook fired
cat ~/.claude/debug/$SESSION_ID/* | grep "UserPromptSubmit"

# 3. Verify snippet content was injected
cat ~/.claude/debug/$SESSION_ID/* | grep -A 50 "user-prompt-submit-hook"

# 4. Check for snippet announcement in response
cat ~/.claude/debug/$SESSION_ID/* | grep "Active Context"

# 5. Verify verification hash was present
cat ~/.claude/debug/$SESSION_ID/* | grep "VERIFICATION_HASH"
```

### Debugging Failed Hooks

```bash
# Check if hook pattern matched
grep -r "hook.*matched" ~/.claude/debug/$SESSION_ID/

# Check for script execution errors
grep -r "error\|Error\|ERROR" ~/.claude/debug/$SESSION_ID/

# Verify script path was correct
grep -r "command.*python3.*scripts" ~/.claude/debug/$SESSION_ID/

# Check hook output
grep -r "hook.*output" ~/.claude/debug/$SESSION_ID/
```

---

## Testing Hook Configurations

### Workflow

1. **Modify hook configuration** (e.g., `hooks/hooks.json` or `plugin.json`)

2. **Verify configuration** with `/hooks` command:
   ```bash
   claude -p "/hooks"
   ```

3. **Test hook trigger with debug mode:**
   ```bash
   claude --debug -p "prompt containing trigger keyword"
   ```

4. **Check debug output and logs** for:
   - Matching hook patterns
   - Script execution paths
   - Command output/errors
   - Success/failure status
   - Full execution trace in `~/.claude/debug/{session_id}/`

5. **Review debug logs:**
   ```bash
   # Find your session_id from the debug output, then:
   cat ~/.claude/debug/{session_id}/*

   # Or tail for real-time monitoring:
   tail -f ~/.claude/debug/{session_id}/*
   ```

6. **Iterate:** Adjust configuration based on debug output and logs

### Hook Testing Checklist

- [ ] JSON syntax is valid (use `jq` or JSON validator)
- [ ] Hook patterns match correctly (test regex separately)
- [ ] Script paths are absolute (use `${CLAUDE_PLUGIN_ROOT}`)
- [ ] Scripts have execution permissions (`chmod +x`)
- [ ] Environment variables are accessible
- [ ] Commands work when run manually
- [ ] Tool names match exactly (case-sensitive)

### Example: Testing a UserPromptSubmit Hook

```bash
# 1. Check hook is registered
claude -p "/hooks"

# 2. Test with trigger keyword (debug mode with JSON output)
claude --debug --verbose --output-format "stream-json" -p "docker containers" | jq . | tee /tmp/test.json

# 3. Extract session_id for continuation
SESSION_ID=$(jq -r 'select(.session_id != null) | .session_id' /tmp/test.json | head -1)
echo "Session ID: $SESSION_ID"

# 4. Verify snippet injection in debug logs
cat ~/.claude/debug/$SESSION_ID/* | grep -A 10 "UserPromptSubmit"

# 5. Continue conversation to verify context persists
claude --debug -p "what snippet was active?" -c "$SESSION_ID"

# 6. Review complete debug logs
ls -lh ~/.claude/debug/$SESSION_ID/
cat ~/.claude/debug/$SESSION_ID/*
```

---

## Testing Snippet Configurations

### Pattern Matching Tests

```bash
# Test if snippet triggers correctly (CLI tool)
cd /path/to/plugin/scripts
python3 snippets_cli.py test snippet-name "test prompt with keywords" --snippets-dir ../commands/local

# Test via live interaction with debug mode
claude --debug --verbose --output-format "stream-json" -p "prompt with snippet keywords" | jq .

# Extract session_id and check debug logs for snippet injection
SESSION_ID=$(claude --debug -p "test keyword" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
cat ~/.claude/debug/$SESSION_ID/* | grep "SNIPPET_NAME"
```

### Verification Hash Testing

Add a unique verification hash to your snippet:

```markdown
**VERIFICATION_HASH:** `8d3a7f1b9c4e2056`
```

Then test if it's injected:

```bash
claude -p "what is the verification hash for testing?"
# Should return: 8d3a7f1b9c4e2056
```

### Snippet Testing Workflow

1. **Create/modify snippet**
2. **Test pattern matching** (CLI tool)
3. **Test live injection** (`claude --debug`)
4. **Verify hash** (one-shot question)
5. **Test announcement** (check for Active Context message)
6. **Continue conversation** (verify context persists)

---

## Testing Plugin Changes

### Full Plugin Test Workflow

```bash
# 1. Modify plugin (hooks, commands, snippets)

# 2. Restart Claude Code (required for changes to take effect)
# Exit any running sessions, then start fresh

# 3. Verify plugin loaded
claude -p "/plugin list"

# 4. Test commands
claude -p "/your-command test-input"

# 5. Test hooks with debug mode
claude --debug -p "trigger your hook"

# 6. Test snippets
claude --debug -p "keywords that trigger snippet"

# 7. Continue conversation to verify state
claude -c -p "confirm the context is still active"
```

---

## Common Pitfalls

### 1. Forgetting to Restart

**Issue:** Plugin/hook changes don't take effect

**Solution:** Exit Claude Code and restart after configuration changes

### 2. Relative Paths in Hooks

**Issue:** Scripts can't be found

**Solution:** Use absolute paths or `${CLAUDE_PLUGIN_ROOT}`

```json
// ❌ Wrong
"command": "./scripts/hook.py"

// ✅ Right
"command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/hook.py"
```

### 3. Not Using Debug Mode

**Issue:** Can't see what's happening during execution, no logs saved

**Solution:** Always use `--debug` when testing

```bash
# ❌ Limited visibility, no logs
claude -p "test"

# ✅ Full debugging output with logs
claude --debug -p "test"

# ✅ Structured JSON output for parsing
claude --debug --verbose --output-format "stream-json" -p "test" | jq .

# ✅ Check debug logs afterward
ls ~/.claude/debug/  # List all session directories
cat ~/.claude/debug/{session_id}/*  # View specific session logs
```

### 4. Testing in Wrong Directory

**Issue:** Hooks/snippets don't trigger as expected

**Solution:** Test in appropriate working directory

```bash
# Be explicit about where you test
cd /path/to/test/project
claude --verbose -p "test"
```

---

## Best Practices

1. **Always use `--debug`** when testing modifications - saves logs to `~/.claude/debug/{session_id}/`
2. **Capture session_id** for conversation continuation and log review
3. **Test incrementally** - One change at a time
4. **Create verification hashes** - Unique identifiers to confirm injection
5. **Review debug logs** - Check `~/.claude/debug/{session_id}/` for complete execution trace
6. **Automate tests** - Create bash scripts for repeatable testing with session tracking
7. **Test conversation continuity** - Use `-c {session_id}` to verify state persists
8. **Manual script testing** - Run scripts directly before testing in Claude
9. **Check permissions** - Ensure scripts are executable
10. **Use absolute paths** - Avoid relative path issues with `${CLAUDE_PLUGIN_ROOT}`
11. **Restart after changes** - Plugin/hook changes require restart
12. **Document test cases** - Keep track of what should happen and expected session IDs

---

## Advanced Testing Patterns

### Automated Test Suites

Create bash test scripts:

```bash
#!/bin/bash
# test_my_plugin.sh

echo "🧪 Testing Plugin: my-plugin"

# Test 1: Snippet exists
echo "Test 1: Snippet registration..."
claude -p "/plugin list" | grep -q "my-plugin" && echo "✅ PASS" || echo "❌ FAIL"

# Test 2: Pattern matching
echo "Test 2: Pattern matching..."
output=$(claude -p "test keyword" 2>&1)
echo "$output" | grep -q "expected content" && echo "✅ PASS" || echo "❌ FAIL"

# Test 3: Verification hash
echo "Test 3: Verification hash..."
output=$(claude -p "what is the verification hash?" 2>&1)
echo "$output" | grep -q "8d3a7f1b9c4e2056" && echo "✅ PASS" || echo "❌ FAIL"

# Test 4: Conversation continuity
echo "Test 4: Conversation continuity..."
claude -p "start test" > /dev/null
output=$(claude -c -p "continue test" 2>&1)
echo "$output" | grep -q "expected response" && echo "✅ PASS" || echo "❌ FAIL"
```

### JSON Output for Programmatic Testing

```bash
# Get JSON output for parsing
claude --debug --verbose -p "test" --output-format json > test-output.json

# Parse with jq
cat test-output.json | jq '.responses[].text'
```

### Limiting Turns for Testing

```bash
# Limit agentic turns for faster testing
claude --max-turns 3 -p "test prompt"
```

---

## Debugging Tips

### 1. Check Hook Execution

```bash
# Use debug mode to see full execution details
claude --debug -p "trigger keyword"

# With JSON output for programmatic analysis
claude --debug --verbose --output-format "stream-json" -p "trigger keyword" | jq .

# Review debug logs for complete execution trace
SESSION_ID=$(claude --debug -p "test" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
cat ~/.claude/debug/$SESSION_ID/* | less
```

### 2. Test Scripts Manually

```bash
# Run hook script directly to verify it works
/absolute/path/to/script.py "test input"
```

### 3. Validate JSON Configurations

```bash
# Check JSON syntax
jq . hooks/hooks.json

# Validate plugin manifest
jq . .claude-plugin/plugin.json
```

### 4. Check File Permissions

```bash
# Scripts must be executable
ls -la /path/to/script.py
chmod +x /path/to/script.py
```

### 5. Use Verification Hashes

Add unique hashes to track content injection:

```markdown
**VERIFICATION_HASH:** `unique-hash-12345`
```

Test with:
```bash
claude -p "what is the verification hash?"
```

---

## Quick Reference

```bash
# Test hook execution with debug mode
claude --debug -p "trigger keyword"

# Get structured JSON output
claude --debug --verbose --output-format "stream-json" -p "test" | jq .

# Capture session_id for continuation
SESSION_ID=$(claude --debug -p "test" 2>&1 | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)

# Continue conversation with session_id
claude --debug -p "follow-up test" -c "$SESSION_ID"

# Review debug logs
ls ~/.claude/debug/  # List all sessions
cat ~/.claude/debug/$SESSION_ID/*  # View specific session
tail -f ~/.claude/debug/$SESSION_ID/*  # Monitor in real-time

# Test snippet pattern matching (CLI)
python3 snippets_cli.py test snippet-name "test prompt" --snippets-dir ../commands/local

# Verify plugin loaded
claude -p "/plugin list"

# Check hook configuration
claude -p "/hooks"

# Automated test script with session tracking
#!/bin/bash
OUT=$(claude --debug --verbose --output-format "stream-json" -p "test 1" | jq .)
SESSION_ID=$(echo "$OUT" | jq -r 'select(.session_id != null) | .session_id' | head -1)
echo "Session: $SESSION_ID"

# Check debug logs
cat ~/.claude/debug/$SESSION_ID/* | grep "expected" && echo "✅" || echo "❌"

# Continue and test
claude --debug -p "test 2" -c "$SESSION_ID" | grep "expected" && echo "✅" || echo "❌"
```

---

## Resources

- [CLI Reference](https://docs.claude.com/en/docs/claude-code/cli-reference.md)
- [Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks.md)
- [Interactive Mode](https://docs.claude.com/en/docs/claude-code/interactive-mode.md)
- [Troubleshooting Guide](https://docs.claude.com/en/docs/claude-code/troubleshooting.md)
