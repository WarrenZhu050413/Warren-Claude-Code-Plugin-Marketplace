---
description: Update an existing snippet's pattern or content
---

# Update Snippet (LLM-Enabled with Mandatory Preview)

You are an intelligent wrapper around `snippets_cli.py update`. Your job is to:
1. **Analyze conversation context** if update instructions not provided (NEW)
2. **Check CLI help** to understand available options (MANDATORY)
3. **Understand what needs updating** (pattern, content, status, name)
4. **Show current state** before making changes
5. **Generate complete preview** of all proposed changes
6. **Get explicit user approval** before executing
7. **Execute & test** changes after approval
8. **Display updated snippet** for verification

## Phase 0: Analyze Context and Infer Changes (if needed)

**CRITICAL**: Before checking CLI help, determine if update instructions are provided.

1. **Parse $ARGUMENTS to extract**:
   - Snippet name/identifier (required)
   - Update instructions (optional - pattern changes, content updates, etc.)

2. **If update instructions are NOT provided**:
   - **Analyze recent conversation** for context:
     - Look for snippets that were just used or mentioned
     - Identify issues with snippet injection or matching
     - Note any pattern mismatches discovered (e.g., "POST didn't match")
     - Identify content that should be added to snippets
     - Look for user corrections or manual workarounds
   - **Infer necessary changes**:
     - Should pattern be expanded to catch more keywords?
     - Is content outdated or missing information?
     - Were alternative terms mentioned that should be added?
     - Did pattern fail to match when it should have?
   - **Propose specific modifications** based on conversation analysis
   - Present to user: "Based on our recent session where [summary], I propose updating [snippet] to: [specific changes]"

3. **If update instructions ARE provided**:
   - Skip conversation analysis
   - Proceed directly to Phase 0.5 with provided instructions

**Example scenarios**:
- User says: "update-snippet POST" (no instructions)
  → Analyze: We used POST command, noticed filtering issues, discussed recipient logic
  → Propose: "Update POST snippet pattern to include variations, add recipient filtering examples"

- User says: "update-snippet POST add the word 'email'" (has instructions)
  → Skip analysis, use provided instructions directly to add 'email' to pattern

## Phase 0.5: CLI Help Check (**MANDATORY STEP**)

**CRITICAL**: Before ANY other operation, ALWAYS check the CLI help to understand current available options and avoid using non-existent arguments.

```bash
# Get main help
main_help=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py --help 2>&1)

# Get update subcommand help
update_help=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py update --help 2>&1)
```

**Parse the help output to extract:**
- Available options (e.g., `--pattern`, `--content`, `--file`, `--enabled`, `--rename`)
- Global options (e.g., `--config`, `--snippets-dir`, `--use-base-config`, `--format`)
- Required vs optional arguments
- Option formats (e.g., `--enabled ENABLED` expects a value)
- Any constraints or special requirements

**Why This Matters:**
- Prevents errors from using non-existent options (like `--force` which doesn't exist for update)
- Ensures correct argument syntax
- Adapts to CLI changes automatically
- Avoids wasting user time with failed commands

**Store parsed options for validation in Phase 1.**

## Phase 1: Parse & Validate

Extract from `$ARGUMENTS` (or from Phase 0 analysis):
- **Snippet name**: Which snippet to update
- **What to change**: Pattern, content, enabled status, or rename (from args or conversation analysis)
- **New values**: Specific updates to make (from args or conversation analysis)
- **Config target**: Whether to use base config (--use-base-config flag) - defaults to local config

### Intent Examples

```
"/update-snippet docker add compose"
→ name: docker, action: modify pattern, add: compose

"/update-snippet mail --disable"
→ name: mail, action: disable

"/update-snippet kubernetes use ~/new-k8s.md"
→ name: kubernetes, action: update content, file: ~/new-k8s.md

"/update-snippet gcal rename to google-calendar"
→ name: gcal, action: rename, new name: google-calendar

"/update-snippet POST" (no instructions)
→ name: POST, action: analyze conversation for updates
```

## Phase 2: Show Current State

Always show current state before making changes:

```bash
current=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py list "$name" --snippets-dir ../commands/local 2>&1)
```

Display:

```
📄 Current snippet: {name}

Pattern: {current_pattern}
  Alternatives: {count}
  • {list alternatives}

Content: {file} ({size})
Status: {enabled ? '✓ Enabled' : '✗ Disabled'}

Analyzing requested changes...
```

## Phase 2a: Format Pattern Updates (if applicable)

If the update involves pattern changes, **ALWAYS consult the Regex Protocol Guide below** before proceeding.

### Quick Regex Rules Summary

**CRITICAL SPACING RULES:**
1. **NO SPACES in patterns**: Never use `\s`, `\s*`, or `\s+` between words
2. **Only allow**: `-` (hyphen), `_` (underscore), or nothing between words
3. **Use `[-_]?`** to allow optional hyphen or underscore: `word1[-_]?word2`
4. **Standard punctuation**: Add `[.,;:]?\b` at the end for optional trailing punctuation
5. **Word boundaries**: Always use `\b` at start and end

**Pattern Structure Template:**
```
\b(WORD1|WORD2|word1[-_]?word2)[.,;:]?\b
```

**When updating patterns:**
- Apply Protocol Guide rules (see below) to any new pattern
- Check existing pattern follows protocol (warn if not)
- Suggest corrections if user provides non-compliant pattern
- **See full Regex Protocol Guide below for comprehensive rules**

---

## Regex Protocol Guide (Comprehensive Standards)

**This section documents the complete regex standards for all snippets. ALWAYS reference these rules when creating or updating snippet patterns.**

### 1. Core Pattern Structure

**Standard Format:**
```regex
\b(ALTERNATIVE1|ALTERNATIVE2|...)[.,;:]?\b
```

**Components:**
- `\b` - Word boundary at start (REQUIRED)
- `(...)` - Grouping for alternatives (REQUIRED if multiple alternatives)
- `|` - OR operator between alternatives
- `[.,;:]?` - Optional trailing punctuation (REQUIRED STANDARD)
- `\b` - Word boundary at end (REQUIRED)

### 2. Case Conventions

**✅ PREFER: Uppercase for triggers**
- Use uppercase for snippet names that should be explicit triggers
- Examples: `LUA`, `HTML`, `TDD`, `STYLE`, `ISSUE`, `NOTIFY`
- **Rationale**: Reduces false positives, requires intentional invocation

**⚠️ ALLOW: Lowercase for common terms**
- Use lowercase for frequently occurring technical terms
- Examples: `nvim`, `docker`, `kubernetes`, `playwright`
- **Rationale**: These appear naturally in conversation

**❌ AVOID: Mixed case patterns**
- Don't use: `\b(Docker|DOCKER|docker)\b`
- Instead choose one: `\b(DOCKER)\b` or `\b(docker)\b`
- **Exception**: When capturing common misspellings or variations

**Decision Matrix:**
```
Intent: Explicit command-style    → Use UPPERCASE (e.g., LUA, HTML)
Intent: Natural context trigger   → Use lowercase (e.g., search, nvim)
Intent: Broad coverage            → Use lowercase with alternatives
```

### 3. Punctuation Standard

**REQUIRED: Always end with `[.,;:]?\b`**

All patterns MUST follow this standard unless there's a specific reason:

```regex
✅ CORRECT:   \bLUA[.,;:]?\b
✅ CORRECT:   \b(docker|container)[.,;:]?\b
❌ WRONG:     \bLUA\.?\b          (missing comma, semicolon, colon)
❌ WRONG:     \bLUA\b             (no punctuation support)
```

**Why this matters:**
- Matches: "Let's use LUA." (period)
- Matches: "LUA, what is the pattern?" (comma)
- Matches: "LUA; also check HTML" (semicolon)
- Matches: "LUA: verify this works" (colon)

**Special Cases (Command-style patterns):**
- `TXT[/:.]\\s*` - Commands like `TXT: content here`
- `CLEAR[/:.]?\\s*` - Commands like `CLEAR/all`
- These use `/` and `:` as command operators, not natural punctuation

### 4. Multi-Word Phrase Handling

**CRITICAL: NEVER use `\s`, `\s*`, or `\s+` between words**

**✅ CORRECT approach - Use `[-_]?`:**
```regex
google[-_]?calendar         # Matches: google-calendar, google_calendar, googlecalendar
claude[-_]?debug            # Matches: claude-debug, claude_debug, claudedebug
amazon[-_]?web[-_]?services # Matches: amazon-web-services, amazon_web_services, etc.
```

**❌ WRONG approach - Using spaces:**
```regex
google\s*calendar           # FORBIDDEN - space-based matching
claude[\s-]debug            # FORBIDDEN - includes \s
web\s+services              # FORBIDDEN - space-based matching
```

**Pattern for compound terms:**
```regex
\b(word1[-_]?word2|word2[-_]?word1)[.,;:]?\b
```

**Examples:**
```regex
\b(google[-_]?calendar|calendar[-_]?google|gcal)[.,;:]?\b
\b(claude[-_]?debug|debug[-_]?claude)[.,;:]?\b
\b(linear[-_]?app|linear[-_]?api|linearapp|linearapi|linear)[.,;:]?\b
```

### 5. Word Boundary Best Practices

**REQUIRED: Both start and end boundaries**

```regex
✅ CORRECT:   \bLUA[.,;:]?\b
❌ WRONG:     LUA[.,;:]?\b           (missing start boundary)
❌ WRONG:     \bLUA[.,;:]?           (missing end boundary)
```

**Why boundaries matter:**
```regex
Without boundaries:
Pattern: LUA
Matches: "LUA" ✓  but also "VALUATION" ✗ (substring match)

With boundaries:
Pattern: \bLUA\b
Matches: "LUA" ✓  and NOT "VALUATION" ✓ (word match only)
```

**Boundary interaction with punctuation:**
```regex
\bLUA[.,;:]?\b

✓ Matches:  "LUA."       (boundary before L, after A, period optional)
✓ Matches:  "LUA,"       (boundary before L, after A, comma optional)
✓ Matches:  "LUA"        (boundary before L, after A, no punctuation)
✗ No match: "LUATEST"    (no boundary after A)
```

### 6. Avoiding Unintentional Triggers

**Problem: Overly broad patterns**

```regex
❌ DANGEROUS: \b(post|POST)\b
   Issue: Matches "post" in "post-processing", "postmodern", "posting"

✅ BETTER: \bPOST[.,;:]?\b
   Solution: Uppercase requires intentional trigger

✅ ALSO GOOD: \b(shit)?(POST|post)[.,;:]?\b
   Solution: Context-aware pattern (actual example from your snippets)
```

**Common false positive sources:**

| Pattern | False Positive | Fix |
|---------|---------------|-----|
| `\b(test)\b` | "latest", "greatest", "testament" | Use `\bTEST\b` (uppercase) |
| `\b(search)\b` | "research", "searching" (if unwanted) | Use `\bSEARCH\b` or be explicit about intent |
| `\b(cal)\b` | "calendar", "calculate", "calorie" | Use full word: `\b(calendar|gcal)\b` |
| `\b(mail)\b` | "email", "mailing" (if unwanted) | Use `\bMAIL\b` or include explicit alternatives |

**Testing for false positives:**
```bash
# Test your pattern against common English words
echo "The latest research on testing post-processing..." | grep -E '\btest\b'
# If this matches and you don't want it to, use uppercase: \bTEST\b
```

### 7. Alternative Management

**Good practices for alternatives:**

```regex
✅ LOGICAL GROUPING:
\b(linear|linearapp|linearapi|linear[-_]?app|linear[-_]?api)[.,;:]?\b
   • Start with shortest/most common (linear)
   • Add compound forms (linearapp)
   • Add hyphenated variants (linear-app)

✅ INCLUDE COMMON ABBREVIATIONS:
\b(google[-_]?calendar|calendar[-_]?google|gcal)[.,;:]?\b
   • Full term
   • Alternative order
   • Common abbreviation

❌ TOO MANY ALTERNATIVES (hard to maintain):
\b(kubernetes|k8s|kube|k-8-s|k_8_s|...50 more...)\b
   Instead: \b(kubernetes|k8s|kube)\b
```

**Alternative count guidelines:**
- **1-3 alternatives**: Ideal, easy to understand
- **4-7 alternatives**: Acceptable, document the reasoning
- **8+ alternatives**: Consider if pattern is too broad, may need splitting

### 8. Protocol Validation Checklist

**Before finalizing any pattern, verify:**

- [ ] ✅ Starts with `\b`
- [ ] ✅ Ends with `[.,;:]?\b`
- [ ] ✅ No `\s`, `\s*`, or `\s+` between words
- [ ] ✅ Multi-word terms use `[-_]?` format
- [ ] ✅ Case convention is intentional (uppercase or lowercase)
- [ ] ✅ Tested against false positive scenarios
- [ ] ✅ Alternative count is reasonable (< 8 preferred)
- [ ] ✅ All alternatives are necessary and documented

### 9. Pattern Examples by Use Case

**Command-style (uppercase, explicit):**
```regex
\bLUA[.,;:]?\b                          # Lua programming context
\bHTML[.,;:]?\b                         # HTML output style
\bTDD[.,;:]?\b                          # Test-driven development
\bISSUE[.,;:]?\b                        # Create GitHub issue
\bNOTIFY[.,;:]?\b                       # Send notification
\bSTYLE[.,;:]?\b                        # Style guide
```

**Context-aware (lowercase, natural):**
```regex
\b(nvim|neovim)[.,;:]?\b                # Neovim context
\b(docker|container)[.,;:]?\b          # Docker context
\b(playwright)[.,;:]?\b                 # Playwright testing
\b(codex)[.,;:]?\b                      # Codex search
```

**Compound terms (hyphen/underscore support):**
```regex
\b(claude[-_]?debug|debug[-_]?claude|claude[-_]?test|test[-_]?claude)[.,;:]?\b
\b(google[-_]?calendar|calendar[-_]?google|gcal)[.,;:]?\b
\b(linear[-_]?app|linear[-_]?api|linearapp|linearapi|linear)[.,;:]?\b
```

**Broad coverage (multiple alternatives):**
```regex
\b(search|searching|websearch|web[-_]?search|find[-_]?information|look[-_]?up|research|researching|comprehensive[-_]?search)[.,;:]?\b
\b(email|mail|e-mail|message|inbox|send\s+(to|message))[.,;:]?\b
\b(gcal|g-cal|google\s*calendar|calendar|event|schedule|appointment)[.,;:]?\b
```

### 10. Common Pattern Anti-Patterns

**❌ Anti-Pattern 1: Space-based matching**
```regex
BAD:  \b(google\s+calendar)\b
GOOD: \b(google[-_]?calendar)\b
```

**❌ Anti-Pattern 2: Missing punctuation standard**
```regex
BAD:  \bLUA\.?\b                        # Only supports period
GOOD: \bLUA[.,;:]?\b                    # Supports all punctuation
```

**❌ Anti-Pattern 3: No word boundaries**
```regex
BAD:  (docker|container)                # Matches substrings
GOOD: \b(docker|container)[.,;:]?\b     # Matches whole words
```

**❌ Anti-Pattern 4: Inconsistent case**
```regex
BAD:  \b(Docker|DOCKER|docker)\b        # Mixed case, confusing
GOOD: \b(docker)\b  OR  \b(DOCKER)\b    # Choose one intent
```

**❌ Anti-Pattern 5: Redundant alternatives**
```regex
BAD:  \b(kubernetes|kubernetes-|kubernetes_)\b    # Redundant with [-_]?
GOOD: \b(kubernetes|k8s)\b[.,;:]?\b              # Concise, clear
```

### 11. When to Deviate from Protocol

**Acceptable exceptions:**

1. **Command-style patterns with different operators:**
   ```regex
   TXT[/:.]\\s*              # Commands: TXT: text or TXT/ text
   CLEAR[/:.]?\\s*           # Commands: CLEAR: or CLEAR/
   ```
   *Reason*: These are command invocations, not natural text triggers

2. **Case-insensitive matching (rare):**
   ```regex
   (?i)\b(playwright[-_]?mcp|mcp[-_]?playwright)[.,;:]?\b
   ```
   *Reason*: Accommodate user typing variations when case doesn't matter

3. **Special whitespace handling (very rare):**
   ```regex
   \b(send\s+(to|message))\b              # Allows "send to" or "send message"
   ```
   *Reason*: Natural language phrases where space IS the separator

**Always document exceptions** in snippet metadata or comments.

## Phase 3: Build Preview (**MANDATORY**)

**CRITICAL**: Before ANY confirmation prompt, construct COMPLETE preview of all changes.

### Step 3.1: Validate Pattern Against Protocol (if pattern changed)

**If pattern is being updated, validate against Regex Protocol Guide:**

```bash
# Check pattern compliance
pattern_warnings=()

# Check 1: Word boundaries
if [[ ! "$new_pattern" =~ ^\\\b.*\\\b$ ]]; then
    pattern_warnings+=("⚠️  Missing word boundaries (\\b at start and end)")
fi

# Check 2: Punctuation standard
if [[ ! "$new_pattern" =~ \[.,;:\]\?\\b$ ]]; then
    pattern_warnings+=("⚠️  Missing standard punctuation [.,;:]?\\b at end")
fi

# Check 3: Space-based matching (forbidden)
if [[ "$new_pattern" =~ \\s ]]; then
    pattern_warnings+=("🚫 CRITICAL: Contains \\s (space matching) - FORBIDDEN by protocol")
fi

# Check 4: Alternative count
alt_count=$(echo "$new_pattern" | grep -o '|' | wc -l)
alt_count=$((alt_count + 1))
if [ "$alt_count" -gt 7 ]; then
    pattern_warnings+=("⚠️  High alternative count ($alt_count) - consider simplifying")
fi

# Display warnings if any
if [ ${#pattern_warnings[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  PATTERN PROTOCOL WARNINGS:"
    for warning in "${pattern_warnings[@]}"; do
        echo "  $warning"
    done
    echo ""
    echo "See Regex Protocol Guide (Phase 2a) for standards."
    echo ""
fi
```

### Step 3.2: Generate Comprehensive Preview

Display ALL changes in a single preview:

```
═══════════════════════════════════════════════════════════
📋 PREVIEW: Proposed Changes to '{name}' Snippet
═══════════════════════════════════════════════════════════

📝 CONFIG: ${use_base_config ? 'config.json (global)' : 'config.local.json (personal)'}

${from_conversation ? `
🔍 SOURCE: Inferred from recent conversation analysis
  Context: ${conversation_summary}
` : '📝 SOURCE: Based on provided instructions'}

${pattern_changes ? `
🔧 PATTERN CHANGES:
  Current:  ${current_pattern} (${current_count} alternatives)
  New:      ${new_pattern} (${new_count} alternatives)

  ${added_terms.length > 0 ? `✚ Adding: ${added_terms.join(', ')}` : ''}
  ${removed_terms.length > 0 ? `✖ Removing: ${removed_terms.join(', ')}` : ''}
` : ''}

${content_changes ? `
📝 CONTENT CHANGES:
  Current:  ${current_size} bytes (${Math.round(current_size/1024)}KB)
  New:      ${new_size} bytes (${Math.round(new_size/1024)}KB)
  Change:   ${size_change > 0 ? '+' : ''}${size_change} bytes

  Preview (first 5 lines of new content):
  ─────────────────────────────────────────────────────────
  ${new_content.split('\n').slice(0, 5).join('\n')}
  ${new_content.split('\n').length > 5 ? '... (truncated)' : ''}
  ─────────────────────────────────────────────────────────
` : ''}

${status_changes ? `
🔘 STATUS CHANGE:
  Current:  ${current_status}
  New:      ${new_status}

  ${new_status === '✗ Disabled' ? `
  ⚠️  Note: When disabled, this snippet will NOT inject.
  ` : `
  ✅ Note: When enabled, this snippet will inject on match.
  `}
` : ''}

${rename_changes ? `
📛 RENAME:
  Current:  ${current_name}
  New:      ${new_name}
  File:     ${current_name}.md → ${new_name}.md
` : ''}

═══════════════════════════════════════════════════════════
```

## Phase 4: Request Approval (**MANDATORY GATE**)

**CRITICAL**: Do NOT proceed without explicit approval.

```
🚦 Do you want to apply these changes?

Options:
  [Y] Yes - Apply all changes as shown
  [N] No - Cancel, make no changes
  [D] Details - Show more detailed diff/preview
  [M] Modify - Adjust the proposed changes

Your choice [Y/N/D/M]:
```

Handle responses:
- **Y/yes**: Proceed to Phase 5 (Execute CLI)
- **N/no**: Abort, display cancellation message
- **D/details**: Show detailed diff, then re-ask
- **M/modify**: Return to Phase 3 (Build Preview) with refinements

If user says NO:
```
❌ Update cancelled. No changes made to '{name}' snippet.
```

If user requests Details:
```bash
# For content, show diff
if [ -n "$content_changes" ]; then
    diff -u <(cat current_file) <(cat new_file) | head -50
fi

# For pattern, show alternatives breakdown
if [ -n "$pattern_changes" ]; then
    echo "Current alternatives: ${current_alternatives}"
    echo "New alternatives: ${new_alternatives}"
fi
```

## Phase 5: Execute CLI (**ONLY AFTER APPROVAL**)

**PREREQUISITE**: Phase 4 must have received explicit approval.

**IMPORTANT**: Only use options that were confirmed to exist in Phase 0.5 help check.

```bash
result=$(cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts && python3 snippets_cli.py ${use_base_config:+--use-base-config} update "$name" \
  ${pattern:+--pattern "$pattern"} \
  ${content:+--content "$content"} \
  ${file:+--file "$file"} \
  ${enabled:+--enabled "$enabled"} \
  ${rename:+--rename "$rename"} \
  2>&1)
```

**Note about --use-base-config:**
- **Without flag** (default): Updates snippet in `config.local.json` (personal snippets)
- **With flag**: Updates snippet in `config.json` (global/shared snippets)
- Most users want personal snippets, so default is correct
- Only use `--use-base-config` for snippets you want to share across all users

**Note**: `--snippets-dir` is NOT supported for the update command. It reads from the configured snippets directory automatically.

**If execution fails**:
```
❌ Update failed: {error_message}

No changes were applied. Current state preserved.

Troubleshooting:
- Check snippet name is correct
- Verify file paths are accessible
- Ensure no duplicate patterns/names
- Confirm boolean values are lowercase (true/false)
- Make sure snippet exists before updating
```

### Common Edge Cases

**Rename conflict:**
```
❌ Error: Cannot rename to '{new_name}' - snippet already exists.

Choose a different name or delete existing snippet first.
```

**Invalid enabled value:**
```
❌ Error: --enabled must be 'true' or 'false' (lowercase).

You provided: {value}
Correct usage: --enabled true  or  --enabled false
```

**Content and file both provided:**
```
❌ Error: Cannot use both --content and --file together.

Use one or the other:
- Update from file: --file /path/to/file.md
- Update inline: --content "new content here"
```

**Concurrent modification:**
```
❌ Error: Snippet was modified by another process.

The snippet has changed since you loaded it. Retry the update.
```

**Empty pattern update:**
```
❌ Error: Pattern cannot be empty.

Provide a valid regex pattern with at least one alternative.
Example: --pattern "\b(docker|container)\b"
```

## Phase 6: Handle Result

### On Success

```
✅ Snippet '{name}' updated successfully!

📊 Changes applied:

${pattern_changed ? `Pattern:
  Before: ${old_pattern} (${old_count} alternatives)
  After:  ${new_pattern} (${new_count} alternatives)
` : ''}

${content_changed ? `Content:
  Before: ${old_size} bytes
  After:  ${new_size} bytes
  Change: ${diff_size > 0 ? '+' : ''}${diff_size} bytes
` : ''}

${enabled_changed ? `Status:
  Before: ${old_status}
  After:  ${new_status}
` : ''}

${from_conversation ? `
🔍 Note: These changes were inferred from conversation analysis.
` : ''}

💡 Changes take effect immediately.
```

## Phase 7: Verification Testing

After successful update, test that snippet still works:

```bash
# Extract hash if content/pattern changed
verification_hash=$(echo "$result" | python3 -c "import json, sys; print(json.load(sys.stdin).get('data', {}).get('verification_hash', ''))" 2>/dev/null || echo "")

if [ -n "$verification_hash" ]; then
    # Extract test word from pattern
    test_word=$(echo "$new_pattern" | grep -oE '\w+' | head -1)

    # Test with Claude
    test_result=$(claude -p "Test with $test_word keyword" 2>&1 | grep -i "$verification_hash" || echo "")

    if [ -n "$test_result" ]; then
        verification_status="✅ Verified - updated snippet is working"
    else
        verification_status="⚠️  Could not verify injection"
    fi

    echo ""
    echo "🔍 Verification:"
    echo "  Status: $verification_status"
    echo "  Hash: $verification_hash"
fi
```

## Phase 8: Display & Verify Snippet

After verification, show complete updated snippet:

```bash
snippet_file=$(echo "$result" | python3 -c "import json, sys; ...")
echo ""
echo "📄 Updated Snippet Content:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/$snippet_file"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

## Important Notes

- **NEW: Analyze conversation context** if no update instructions provided
- **ALWAYS check CLI help first** (Phase 0.5) before any operations
- **ALWAYS show current state** before building preview
- **ALWAYS generate complete preview** before asking approval
- **NEVER execute without explicit approval** - hard requirement
- **Preview must be comprehensive** - show ALL changes
- **Handle cancellation gracefully** - no changes if user says no
- **Support detailed view** - allow users to see more before approving
- **Validate before preview** - catch errors early
- **Always test after update** - verify snippet still works
- **Always display updated snippet** - users verify final content
- **Be transparent about source** - clearly indicate if changes were inferred from conversation
