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

## Phase 1: Parse & Understand Intent

Extract from `$ARGUMENTS`:
- **Snippet name**: The identifier (e.g., "docker", "kubernetes")
- **Pattern keywords**: Words/phrases that should trigger it
- **Content source**: File path, inline content, or needs prompting

### Natural Language Examples

```
"create docker snippet for docker and containers"
→ name: docker, pattern: docker|containers, needs: content

"add kubernetes snippet, use ~/k8s.md"
→ name: kubernetes, content: ~/k8s.md, needs: pattern

"create snippet"
→ needs: everything (fully interactive)
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

## Phase 3: Format Inputs

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

## Phase 4: Execute CLI

```bash
result=$(cd ${CLAUDE_PLUGIN_ROOT}/scripts && python3 snippets_cli.py create "$name" \
  --pattern "$formatted_pattern" \
  ${content:+--content "$content"} \
  ${file_path:+--file "$file_path"} 2>&1)
```

## Phase 5: Handle Result

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

## Phase 6: Create and Run Test Suite

After success, automatically create and run tests:

```bash
# Create test suite
mkdir -p ${CLAUDE_PLUGIN_ROOT}/tests/shared
cat > ${CLAUDE_PLUGIN_ROOT}/tests/shared/${name}_test.sh << 'EOF'
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
if cd ${CLAUDE_PLUGIN_ROOT}/scripts && python3 snippets_cli.py list | grep -q "$SNIPPET_NAME"; then
    echo "  ✅ PASS"
    ((TESTS_PASSED++))
else
    echo "  ❌ FAIL"
    ((TESTS_FAILED++))
fi

# Test 2: Pattern matching
echo "Test 2: Testing pattern matching..."
if cd ${CLAUDE_PLUGIN_ROOT}/scripts && python3 snippets_cli.py test "$SNIPPET_NAME" "Testing $TEST_KEYWORD" | grep -q "matched"; then
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

chmod +x ${CLAUDE_PLUGIN_ROOT}/tests/shared/${name}_test.sh

# Run tests
${CLAUDE_PLUGIN_ROOT}/tests/shared/${name}_test.sh
```

## Phase 7: Display Full Snippet

After tests, show complete snippet content for verification:

```bash
snippet_file=$(echo "$result" | python3 -c "import json, sys; ...")
echo ""
echo "📄 Full Snippet Content:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "${CLAUDE_PLUGIN_ROOT}/scripts/$snippet_file"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

## Important Notes

- **Be conversational**: Use natural language
- **Validate early**: Check before calling CLI
- **Format clearly**: Use emojis and structure
- **Handle errors gracefully**: Never show raw JSON
- **Always run tests**: Catch issues immediately
- **Always display snippet**: Users verify content
- **Use ${CLAUDE_PLUGIN_ROOT}**: For all plugin paths
