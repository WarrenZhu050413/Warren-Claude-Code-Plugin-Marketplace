---
name: "Minimal GitHub Issue Template"
description: "Warren's preferred minimal format for GitHub issues. Use by default unless user asks for more detail."
triggers: ["github issue", "gh issue create", "report bug"]
---

# Minimal GitHub Issue Template

## Default Format (Use Unless User Asks for More)

```markdown
[Problem statement in 1-2 sentences. What breaks and when.]

### Reproduce

```bash
# Step 1: Minimal setup
# Step 2: Trigger action
# Step 3: Observe problem
```

### Environment
- Tool X.Y.Z
- OS version
```

## Rules

**Include:**
- Problem statement (1-2 sentences max)
- Minimal reproduce steps (3-5 bash commands that trigger the bug)
- Environment (one line per item)

**Don't include (unless user explicitly requests):**
- ❌ Code analysis sections ("The Issue")
- ❌ Suggested fixes or "Expected Behavior"
- ❌ Line numbers or code snippets from source
- ❌ Verification steps (only trigger steps)
- ❌ Technical explanations of why it fails

**Always:**
- Show preview before creating
- Get user approval
- Keep it brief - respect maintainer time

## When to Expand

Add detail only if user says:
- "add more detail"
- "explain the technical issue"
- "suggest a fix"

## Example

**Good (Minimal):**
```markdown
Orchestra's MCP configuration deletes existing MCP servers in `.mcp.json` when configuring a local session. Merging instead of overwriting would help preserve existing MCP configs.

### Reproduce

```bash
# 1. Create project with existing .mcp.json
cd ~/my-project
cat > .mcp.json << 'EOF'
{"mcpServers": {"my-server": {"command": "python"}}}
EOF

# 2. Start Orchestra
echo '{"use_docker": false}' > ~/.orchestra/config/settings.json
orchestra

# 3. Check .mcp.json
cat .mcp.json
# Problem: my-server is gone
```

### Environment
- Orchestra 1.0.57
- macOS 14.6.0
```

**Bad (Too Verbose):**
- Adding "The Issue" section with code snippets
- Including line numbers and technical analysis
- Suggesting specific code fixes
- Adding verification/debugging steps
