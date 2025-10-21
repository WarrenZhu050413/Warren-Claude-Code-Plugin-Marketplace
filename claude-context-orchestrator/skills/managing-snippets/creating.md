---
description: Create a new snippet with regex pattern matching
---

# Create Snippet (LLM-Enabled)

You are an intelligent wrapper around the `snippets_cli.py` tool. Your job is to:
1. **Check CLI help** to understand available options (MANDATORY)
2. **Understand user intent** from natural language input
3. **Guide interactively** if information is missing
4. **Format inputs** intelligently (especially regex patterns)
5. **Execute the CLI** with proper arguments
6. **Format output** beautifully
7. **Display full snippet content** for verification
8. **Create and run test suite** to verify snippet injection

## Phase 0: CLI Help Check (**MANDATORY FIRST STEP**)

**CRITICAL**: Before ANY other operation, ALWAYS check the CLI help to understand current available options and avoid using non-existent arguments.

```bash
# Get main help
main_help=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py --help 2>&1)

# Get create subcommand help
create_help=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py create --help 2>&1)
```

**Parse the help output to extract:**
- Available options (e.g., `--pattern`, `--description`, `--content`, `--file`, `--files`, `--separator`, `--enabled`, `--force`)
- Required vs optional arguments (note: `--description` is now REQUIRED)
- Option formats and constraints
- Global options (e.g., `--config`, `--snippets-dir`, `--use-base-config`, `--format`)

**Why This Matters:**
- Prevents errors from using non-existent options
- Ensures correct argument syntax
- Adapts to CLI changes automatically
- Identifies which options support snippets-dir override

**Store parsed options for validation in Phase 1.**

## Phase 1: Parse & Validate

Extract from `$ARGUMENTS`:
- **Snippet name**: The identifier (e.g., "docker", "kubernetes")
- **Description**: When/why to use this snippet (REQUIRED for Agent Skills format)
- **Pattern keywords**: Words/phrases that should trigger it
- **Content source**: File path, inline content, or needs prompting
- **Config target**: Whether to use base config (--use-base-config flag) - defaults to local config

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

**If description missing:**
```
"Please describe when this snippet should be used.

💡 Example: 'Use this when working with Docker containers and containerization'

Your description:"
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

Transform user input → proper regex following **STANDARD FORMAT REQUIREMENTS**:

#### **STANDARD PATTERN FORMAT (ENFORCED BY CLI)**

**Format**: `\b(PATTERN)[.,;:]?\b`

**All patterns MUST follow this format:**
1. **Word boundaries**: `\b` at start and end
2. **Parentheses**: Pattern wrapped in `()`
3. **ALL CAPS**: Pattern content must be uppercase (A-Z, 0-9)
4. **Multi-word separators**: Use `_`, `-`, or no separator
5. **Optional punctuation**: `[.,;:]?` at the end
6. **Alternation**: Use `|` for multiple patterns

**CLI Validation Rules:**
- ✅ Pattern must match: `\b(PATTERN)[.,;:]?\b`
- ✅ Pattern content must be ALL CAPS
- ✅ No spaces allowed (use `_`, `-`, or nothing)
- ✅ Cannot mix `_` and `-` in same pattern
- ❌ Lowercase letters will be rejected
- ❌ Missing parentheses will be rejected
- ❌ Missing `[.,;:]?` will be rejected

**Valid Examples:**
```
\b(DOCKER)[.,;:]?\b                    # Single word
\b(DOCKER|CONTAINER)[.,;:]?\b          # Alternation
\b(BUILD_ARTIFACT)[.,;:]?\b            # Underscore separator
\b(BUILD-ARTIFACT)[.,;:]?\b            # Hyphen separator
\b(BUILDARTIFACT)[.,;:]?\b             # No separator
\b(NVIM|NEOVIM)[.,;:]?\b               # Multiple alternatives
```

**Invalid Examples (will be rejected):**
```
\bdocker\b                             # ❌ Missing parentheses
\b(docker)[.,;:]?\b                    # ❌ Lowercase
\b(DOCKER)                             # ❌ Missing [.,;:]?\b
(DOCKER)[.,;:]?                        # ❌ Missing \b boundaries
\b(BUILD_ARTIFACT-TEST)[.,;:]?\b       # ❌ Mixed separators
\b(DOCKER CONTAINER)[.,;:]?\b          # ❌ Contains space
```

#### **Pattern Transformation Process**

**User Input → Standard Format Conversion:**

1. **Convert to ALL CAPS:**
   - "docker" → "DOCKER"
   - "build artifact" → "BUILD_ARTIFACT"

2. **Handle multi-word patterns (choose separator):**
   - "docker container" → `BUILD_ARTIFACT` (underscore, preferred)
   - OR → `BUILD-ARTIFACT` (hyphen)
   - OR → `BUILDARTIFACT` (no separator)

3. **Handle alternation:**
   - "docker, container, dockerfile" → `(DOCKER|CONTAINER|DOCKERFILE)`

4. **Apply standard format:**
   - Add `\b` at start
   - Add parentheses around pattern
   - Add `[.,;:]?` for optional punctuation
   - Add `\b` at end

**Transformation Examples:**
```
Input: "docker or container"
Output: \b(DOCKER|CONTAINER)[.,;:]?\b

Input: "kubernetes, k8s, kubectl"
Output: \b(KUBERNETES|K8S|KUBECTL)[.,;:]?\b

Input: "build mcp"
Output: \b(BUILD_MCP)[.,;:]?\b

Input: "deep search"
Output: \b(DEEP_SEARCH)[.,;:]?\b
```

#### **Complex Patterns (Exceptions)**

Patterns with advanced regex (`.*, .+, [^...]`) are allowed as exceptions but should be rare.

**Standard Rules (deprecated):**
- ⚠️ Old lowercase patterns are no longer supported
- ⚠️ Patterns without parentheses will be rejected
- ⚠️ Use the new standard format for all new snippets

### Path Resolution

- Expand `~` → full home directory path
- Convert relative → absolute paths
- Validate file exists before calling CLI

## Phase 2b: Prepend Agent Skills YAML Frontmatter (**MANDATORY**)

**CRITICAL**: ALL new snippets MUST use the Agent Skills format with YAML frontmatter.

### Agent Skills Format

Every snippet you create must begin with this YAML frontmatter:

```markdown
---
name: {name}
description: {description}
---

[Snippet content follows...]
```

### Implementation Rules

1. **Always prepend**: Add YAML frontmatter BEFORE any user-provided content
2. **Use actual values**:
   - `name`: The snippet identifier (e.g., `docker`, `kubernetes`)
   - `description`: When/why to use this snippet (e.g., "Use when working with Docker containers")
3. **Preserve content**: Don't modify user's original content
4. **No verification hash**: The new format doesn't include verification hashes
5. **Standard Agent Skills**: Follows the same format as Claude Code Agent Skills

### Example Transformation

**User provides:**
```
# Docker Cheat Sheet

Commands for Docker...
```

**You create (with YAML frontmatter prepended):**
```
---
name: docker
description: Use when working with Docker containers, images, and containerization
---

# Docker Cheat Sheet

Commands for Docker...
```

### Why This Matters

- **Standard format**: Matches Claude Code Agent Skills convention
- **Simpler structure**: Cleaner than old announcement template
- **Better discovery**: Description helps Claude understand when to use the snippet
- **Git versioning**: No hashes means cleaner git diffs

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

📍 LOCATION: /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/commands/local/{name}.md

📝 CONFIG: ${use_base_config ? 'config.json (global)' : 'config.local.json (personal)'}

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
result=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py ${use_base_config:+--use-base-config} create "$name" \
  --pattern "$formatted_pattern" \
  --description "$description" \
  ${content:+--content "$content"} \
  ${file_path:+--file "$file_path"} 2>&1)
```

**Note about --use-base-config:**
- **Without flag** (default): Saves to `config.local.json` (personal snippets)
- **With flag**: Saves to `config.json` (global/shared snippets)
- Most users want personal snippets, so default is correct
- Only use `--use-base-config` for snippets you want to share across all users

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
# Description: {description}

SNIPPET_NAME="{name}"
TEST_KEYWORD="{test_keyword}"
TESTS_PASSED=0
TESTS_FAILED=0

echo "🧪 Testing Snippet: $SNIPPET_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test 1: Snippet exists
echo "Test 1: Checking snippet exists..."
if cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py list --snippets-dir ../commands/local | grep -q "$SNIPPET_NAME"; then
    echo "  ✅ PASS"
    ((TESTS_PASSED++))
else
    echo "  ❌ FAIL"
    ((TESTS_FAILED++))
fi

# Test 2: Pattern matching
echo "Test 2: Testing pattern matching..."
if cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py test "$SNIPPET_NAME" "Testing $TEST_KEYWORD" --snippets-dir ../commands/local | grep -q "matched"; then
    echo "  ✅ PASS"
    ((TESTS_PASSED++))
else
    echo "  ❌ FAIL"
    ((TESTS_FAILED++))
fi

# Test 3: E2E injection test (check for YAML frontmatter)
echo "Test 3: E2E injection test..."
snippet_file="/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/commands/local/${SNIPPET_NAME}.md"
if grep -q "^name: $SNIPPET_NAME$" "$snippet_file" && grep -q "^description:" "$snippet_file"; then
    echo "  ✅ PASS: YAML frontmatter found"
    ((TESTS_PASSED++))
else
    echo "  ❌ FAIL: YAML frontmatter not found"
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
cat "/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/commands/local/${snippet_name}.md"
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
