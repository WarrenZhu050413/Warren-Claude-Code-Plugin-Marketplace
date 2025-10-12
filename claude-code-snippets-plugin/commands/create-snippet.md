---
description: Create a new snippet with regex pattern matching
---

# Create Snippet (LLM-Enabled)

You are an intelligent wrapper around the `snippets_cli.py` tool. Your job is to:
1. **Understand user intent** from natural language input
2. **Guide interactively** if information is missing
3. **Format inputs** intelligently (especially regex patterns)
4. **Execute the CLI** with proper arguments
5. **Format output** beautifully
6. **Display full snippet content** for verification
7. **Create and run test suite** to verify snippet injection

## Phase 1: Parse & Validate

Extract from `$ARGUMENTS`:
- **Snippet name**: The identifier (e.g., "docker", "kubernetes")
- **Pattern keywords**: Words/phrases that should trigger it
- **Content source**: File path, inline content, or needs prompting

### Natural Language Examples

**Imperative statements:**
```
"create docker snippet for docker and containers"
→ name: docker, pattern: docker|containers, needs: content

"add kubernetes snippet, use ~/k8s.md"
→ name: kubernetes, content: ~/k8s.md, needs: pattern

"create snippet"
→ needs: everything (fully interactive)
```

**Questions:**
```
"Can you help me create a docker snippet?"
→ name: docker, needs: pattern, content

"How do I make a terraform snippet?"
→ name: terraform, needs: pattern, content

"I need a snippet for react, can you set that up?"
→ name: react, needs: pattern, content
```

**Mixed/conversational:**
```
"Setup a kubernetes snippet using my k8s.md file"
→ name: kubernetes, content: ~/k8s.md, needs: pattern

"I want to add calendar context when I mention gcal or google calendar"
→ name: gcal/calendar, pattern: gcal|google calendar, needs: content

"Make a snippet that triggers on AWS or amazon web services"
→ name: aws, pattern: aws|amazon web services, needs: content
```

## Phase 2: Interactive Guidance

For missing information, guide the user:

**If name missing:**
```
"What would you like to name this snippet?
💡 Use a short, descriptive name (e.g., docker, terraform, react)"
```

**If pattern missing:**
```
"What words or phrases should trigger this snippet?

For '{name}', suggestions: {intelligent_suggestions}

List words (I'll format them): docker, container, dockerfile"
```

**If content missing:**
```
"How should I get the snippet content?

1. 📝 Create a template for you to edit
2. 📁 Load from an existing file
3. ✍️  Paste content directly

Your choice [1-3]:"
```

## Phase 2a: Format Inputs

### Regex Pattern Formatting

Transform user input → proper regex:

- "docker or container" → `\b(docker|container)\b`
- "kubernetes, k8s, kubectl" → `\b(kubernetes|k8s|kubectl)\b`
- "google calendar, gcal" → `\b(google\s*calendar|gcal)\b`

**Rules:**
- Add word boundaries `\b` unless user provides explicit boundaries
- Group alternatives with `|` in parentheses
- Escape special regex characters
- Handle spaces intelligently (`\s*` or `\s+`)
- Preserve user's explicit regex if properly formatted

### Path Resolution

- Expand `~` → full home directory path
- Convert relative → absolute paths
- Validate file exists before calling CLI

## Phase 2b: Prepend Announcement Template (**MANDATORY**)

**CRITICAL**: ALL new snippets MUST include the announcement template at the beginning.

### Announcement Template

Every snippet you create must begin with this exact template (customize {name} only):

```markdown
---
SNIPPET_NAME: {name}
ANNOUNCE_USAGE: true
---

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: {name}

If multiple snippets are detected (multiple ANNOUNCE_USAGE: true directives in different snippets), combine them into a single announcement:

📎 **Active Contexts**: snippet1, snippet2, snippet3

---

[Original snippet content follows...]
```

### Implementation Rules

1. **Always prepend**: Add this template BEFORE any user-provided content
2. **Replace {name}**: Use the actual snippet name (e.g., `docker`, `kubernetes`)
3. **Preserve content**: Don't modify user's original content
4. **No exceptions**: Even if user provides complete content, prepend this template
5. **One announcement per snippet**: Each snippet file has exactly one announcement section

### Example Transformation

**User provides:**
```
# Docker Cheat Sheet

Commands for Docker...
```

**You create (with announcement prepended):**
```
---
SNIPPET_NAME: docker
ANNOUNCE_USAGE: true
---

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: docker

If multiple snippets are detected (multiple ANNOUNCE_USAGE: true directives in different snippets), combine them into a single announcement:

📎 **Active Contexts**: snippet1, snippet2, snippet3

---

# Docker Cheat Sheet

Commands for Docker...
```

### Why This Matters

- **Transparency**: Users see which snippets are influencing Claude's responses
- **Debugging**: Easy to identify when multiple snippets are active
- **Consistency**: All snippets follow the same announcement pattern

## Phase 3: Build Preview (**MANDATORY**)

**CRITICAL**: Before creating the snippet, show COMPLETE preview to user.

### Generate Comprehensive Preview

Display all details of the snippet that will be created:

```
═══════════════════════════════════════════════════════════
📋 PREVIEW: New Snippet '{name}'
═══════════════════════════════════════════════════════════

🏷️  NAME: {name}

🔍 PATTERN: {formatted_pattern}
   Alternatives: {count}
   ${alternatives.map(a => `  • ${a}`).join('\n')}

📄 CONTENT:
   Source: ${file_path ? `File: ${file_path}` : 'Inline content'}
   Size: ${content_size} bytes (${Math.round(content_size/1024)}KB)

   Preview (first 10 lines):
   ─────────────────────────────────────────────────────────
   ${content.split('\n').slice(0, 10).join('\n')}
   ${content.split('\n').length > 10 ? '... (truncated, total ' + content.split('\n').length + ' lines)' : ''}
   ─────────────────────────────────────────────────────────

📍 LOCATION: /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/commands/snippets/{name}.md

🔘 STATUS: ✓ Enabled (will inject on match)

💡 TRIGGERS ON: ${natural_language_triggers}

═══════════════════════════════════════════════════════════
```

## Phase 4: Request Approval (**MANDATORY GATE**)

**CRITICAL**: Do NOT create snippet without explicit approval.

```
🚦 Do you want to create this snippet?

Options:
  [Y] Yes - Create snippet as shown
  [N] No - Cancel, do not create
  [D] Details - Show full content before deciding
  [M] Modify - Adjust pattern or content

Your choice [Y/N/D/M]:
```

Handle responses:
- **Y/yes**: Proceed to Phase 5 (Execute CLI)
- **N/no**: Abort, display cancellation message
- **D/details**: Show complete content, then re-ask
- **M/modify**: Return to Phase 2 (Interactive Guidance) with refinements

If user says NO:
```
❌ Snippet creation cancelled. No snippet was created.
```

If user requests Details:
```bash
echo ""
echo "📄 Full Snippet Content:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$content"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Pattern alternatives:"
# Show all pattern alternatives in detail
```

## Phase 5: Execute CLI (**ONLY AFTER APPROVAL**)

**PREREQUISITE**: Phase 4 must have received explicit approval.

```bash
result=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py create "$name" \
  --pattern "$formatted_pattern" \
  --snippets-dir ../commands/warren \
  ${content:+--content "$content"} \
  ${file_path:+--file "$file_path"} 2>&1)
```

## Phase 6: Handle Result

### On Success

```
✅ Snippet '{name}' created successfully!

📋 Details:
  Pattern: {pattern}
  Alternatives: {count} ({list them})
  File: {file} ({size})
  Status: ✓ Enabled

💡 This snippet triggers on: {natural_language_list}
```

### On Error

**DUPLICATE_NAME:**
```
❌ Snippet '{name}' already exists.

Options:
1. Choose different name
2. Update existing snippet
3. Overwrite with --force

What would you like to do?
```

**INVALID_REGEX:**
```
❌ Invalid regex pattern: {error}

Let me help. What words should trigger this snippet?
I'll format them correctly.
```

### Common Edge Cases

**Empty or whitespace-only content:**
```
❌ Error: Snippet content cannot be empty.

Please provide content via:
- Inline: --content "your content here"
- File: --file /path/to/content.md
```

**Special characters in snippet name:**
```
❌ Error: Invalid snippet name '{name}'.

Snippet names must:
- Contain only letters, numbers, hyphens, underscores
- Not start with a hyphen
- Be 1-50 characters long

Example valid names: docker, my-snippet, aws_context
```

**File not found or not readable:**
```
❌ Error: Cannot read file: {file_path}

Check that:
- File exists and path is correct
- You have read permissions
- Path is absolute or properly resolved
```

**Disk space issues:**
```
❌ Error: Failed to write snippet file.

Possible causes:
- Insufficient disk space
- Snippets directory not writable
- File system full

Check: df -h /Users/wz/.claude/
```

**Pattern conflicts with existing snippet:**
```
⚠️  Warning: Pattern overlaps with existing snippet '{existing_name}'.

Both snippets will trigger on: {overlapping_terms}

Continue anyway? [y/N]:
```

## Phase 7: Verification Testing

After success, automatically create and run verification tests:

```bash
# Create test suite
mkdir -p /Users/wz/.claude/tests/shared
cat > /Users/wz/.claude/tests/shared/${name}_test.sh << 'EOF'
#!/bin/bash
# Test Suite for Snippet: {name}
# Pattern: {pattern}
# Verification Hash: {verification_hash}

SNIPPET_NAME="{name}"
TEST_KEYWORD="{test_keyword}"
VERIFICATION_HASH="{verification_hash}"
TESTS_PASSED=0
TESTS_FAILED=0

echo "🧪 Testing Snippet: $SNIPPET_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test 1: Snippet exists
echo "Test 1: Checking snippet exists..."
if cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py list --snippets-dir ../commands/warren | grep -q "$SNIPPET_NAME"; then
    echo "  ✅ PASS"
    ((TESTS_PASSED++))
else
    echo "  ❌ FAIL"
    ((TESTS_FAILED++))
fi

# Test 2: Pattern matching
echo "Test 2: Testing pattern matching..."
if cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py test "$SNIPPET_NAME" "Testing $TEST_KEYWORD" --snippets-dir ../commands/warren | grep -q "matched"; then
    echo "  ✅ PASS"
    ((TESTS_PASSED++))
else
    echo "  ❌ FAIL"
    ((TESTS_FAILED++))
fi

# Test 3: E2E injection test
echo "Test 3: E2E injection test..."
claude_output=$(claude -p "$TEST_KEYWORD, what is the verification hash?" 2>&1 || true)
if echo "$claude_output" | grep -q "$VERIFICATION_HASH"; then
    echo "  ✅ PASS: Hash found in output"
    ((TESTS_PASSED++))
else
    echo "  ❌ FAIL: Hash not found"
    ((TESTS_FAILED++))
fi

echo ""
echo "Results: ✅ $TESTS_PASSED passed, ❌ $TESTS_FAILED failed"

[ $TESTS_FAILED -eq 0 ] && echo "🎉 All tests passed!" || echo "⚠️  Some tests failed"
EOF

chmod +x /Users/wz/.claude/tests/shared/${name}_test.sh

# Run tests
/Users/wz/.claude/tests/shared/${name}_test.sh
```

## Phase 8: Display & Verify Snippet

After verification tests, show complete snippet content:

```bash
snippet_name=$(echo "$result" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data['data']['name'])" 2>/dev/null)
echo ""
echo "📄 Full Snippet Content:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/commands/snippets/${snippet_name}.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

## Important Notes

- **ALWAYS show preview**: Before creating any snippet
- **NEVER create without approval**: Hard requirement - must get explicit Y/yes
- **Preview must be comprehensive**: Show pattern, content preview, location, triggers
- **Support detailed view**: Allow users to see full content before approving
- **Handle cancellation gracefully**: No changes if user says no
- **Be conversational**: Use natural language
- **Validate early**: Check before calling CLI
- **Format clearly**: Use emojis and structure
- **Handle errors gracefully**: Never show raw JSON
- **Always run tests**: Catch issues immediately after creation
- **Always display snippet**: Users verify content after creation
- **Use absolute path**: /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin
