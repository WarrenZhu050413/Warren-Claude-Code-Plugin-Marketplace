---
description: Update an existing snippet's pattern or content
---

# Update Snippet (LLM-Enabled with Mandatory Preview)

You are an intelligent wrapper around `snippets_cli.py update`. Your job is to:
1. **Understand what needs updating** (pattern, content, status, name)
2. **Show current state** before making changes
3. **Generate complete preview** of all proposed changes
4. **Get explicit user approval** before executing
5. **Execute & test** changes after approval
6. **Display updated snippet** for verification

## Phase 1: Parse Intent

Extract from `$ARGUMENTS`:
- **Snippet name**: Which snippet to update
- **What to change**: Pattern, content, enabled status, or rename
- **New values**: Specific updates to make

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
```

## Phase 2: Get Current State

Always show current state first:

```bash
current=$(cd ${CLAUDE_PLUGIN_ROOT}/scripts && python3 snippets_cli.py list "$name" 2>&1)
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

## Phase 3: Build Complete Change Preview (**MANDATORY**)

**CRITICAL**: Before ANY confirmation prompt, construct COMPLETE preview of all changes.

### Generate Comprehensive Preview

Display ALL changes in a single preview:

```
═══════════════════════════════════════════════════════════
📋 PREVIEW: Proposed Changes to '{name}' Snippet
═══════════════════════════════════════════════════════════

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

### Request Approval (**MANDATORY GATE**)

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
- **Y/yes**: Proceed to Phase 4 (Execute)
- **N/no**: Abort, display cancellation message
- **D/details**: Show detailed diff, then re-ask
- **M/modify**: Return to Phase 3 with refinements

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

## Phase 4: Execute Update (**ONLY AFTER APPROVAL**)

**PREREQUISITE**: Phase 3 must have received explicit approval.

```bash
result=$(cd ${CLAUDE_PLUGIN_ROOT}/scripts && python3 snippets_cli.py update "$name" \
  ${pattern:+--pattern "$pattern"} \
  ${content:+--content "$content"} \
  ${file:+--file "$file"} \
  ${enabled:+--enabled "$enabled"} \
  ${rename:+--rename "$rename"} \
  2>&1)
```

**If execution fails**:
```
❌ Update failed: {error_message}

No changes were applied. Current state preserved.

Troubleshooting:
- Check snippet name is correct
- Verify file paths are accessible
- Ensure no duplicate patterns/names
```

## Phase 5: Format Result

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

💡 Changes take effect immediately.
```

## Phase 6: Verification Testing

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

## Phase 7: Display Updated Snippet

After verification, show complete updated snippet:

```bash
snippet_file=$(echo "$result" | python3 -c "import json, sys; ...")
echo ""
echo "📄 Updated Snippet Content:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "${CLAUDE_PLUGIN_ROOT}/scripts/$snippet_file"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

## Important Notes

- **ALWAYS show current state** before building preview
- **ALWAYS generate complete preview** before asking approval
- **NEVER execute without explicit approval** - hard requirement
- **Preview must be comprehensive** - show ALL changes
- **Handle cancellation gracefully** - no changes if user says no
- **Support detailed view** - allow users to see more before approving
- **Validate before preview** - catch errors early
- **Always test after update** - verify snippet still works
- **Always display updated snippet** - users verify final content
