# GMAILLM Snippet Hook

## Overview

The GMAILLM snippet hook provides contextual guidance for using the gmaillm CLI tool whenever a user mentions "GMAILLM" in their prompt.

## Trigger

**Pattern:** `\b(GMAILLM)\b[.,;:!?]?`

**Matches:**
- "GMAILLM" - exact match
- "GMAILLM." - with period
- "GMAILLM!" - with exclamation
- "GMAILLM?" - with question mark
- "GMAILLM," - with comma
- etc.

**Examples:**
```
"I want to use GMAILLM to send email"
"Use GMAILLM."
"What is GMAILLM?"
"GMAILLM, please help"
```

## What It Provides

When triggered, the snippet injects comprehensive usage guidance including:

### 1. Quick Reference
- Core commands (verify, list, read, search, send, reply)
- Groups, styles, and workflows management
- Common command patterns

### 2. Programmatic Action Patterns

#### SEND Pattern
- Context gathering from previous emails
- Style determination and application
- Email drafting with learned patterns
- Preview and confirmation workflow
- Post-send suggestions (create group/style/workflow)

#### READ Pattern
- Progressive disclosure (summary → full content)
- Context-efficient email reading

#### WORKFLOW Pattern
- Workflow listing and execution
- Suggestions for creating new workflows

### 3. Post-Action Suggestions

The snippet instructs Claude to **proactively suggest** creating reusable resources:

**After SENDING:**
- Suggest **GROUP** if sending to multiple recipients or pattern emerges
- Suggest **STYLE** if specific tone/format instructions given
- Show exact command and wait for confirmation

**After WORKFLOW:**
- Suggest creating workflow for repeated multi-step tasks
- Provide clear preview of what will be automated

### 4. Key Patterns
- Always quote `#groupname` (shell interprets `#` as comment)
- Preview before send (no automatic sending)
- Suggest reusables proactively
- Use progressive disclosure for context efficiency

## Configuration

**Location:** `/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/scripts/config.local.json`

**Entry:**
```json
{
  "name": "gmaillm",
  "pattern": "\\b(GMAILLM)\\b[.,;:!?]?",
  "snippet": ["../snippets/gmaillm-usage.md"],
  "separator": "\n",
  "enabled": true
}
```

## Usage Example

**User prompt:**
```
"GMAILLM. I want to send an email to my team about the project update."
```

**What happens:**
1. Hook triggers and injects `gmaillm-usage.md` into context
2. Claude receives comprehensive usage guidance
3. Claude follows the SEND pattern:
   - Searches previous emails to team
   - Determines appropriate style
   - Drafts email
   - Shows preview
   - Waits for confirmation
   - After sending, suggests creating "team" group if not exists

## Testing

Test the pattern matching:
```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/scripts
python3 snippets_cli.py test gmaillm "Use GMAILLM to send email"
```

Expected output:
```
✓ Pattern matched
  name: gmaillm
  pattern: \b(GMAILLM)\b[.,;:!?]?
  matches: ['GMAILLM']
  matched: True
```

## Files

- **Snippet**: `snippets/gmaillm-usage.md`
- **Config**: `scripts/config.local.json`
- **Hook script**: `scripts/snippet_injector.py`

## Integration with Claude Code

The snippet hook integrates with Claude Code's UserPromptSubmit hook system. When a user submits a prompt:

1. `snippet_injector.py` checks all patterns in `config.local.json`
2. If pattern matches, corresponding snippet(s) are read
3. Snippet content is injected into the prompt context
4. Claude receives the prompt with injected guidance

## Benefits

1. **Contextual help**: Guidance appears automatically when mentioning gmaillm
2. **Programmatic patterns**: Clear workflows for send/read/workflow operations
3. **Proactive suggestions**: Claude suggests creating groups/styles/workflows
4. **Consistency**: Standardized approach to gmaillm operations
5. **Learning**: Claude learns to use gmaillm effectively without explicit instruction

## Related

- **MAIL snippet**: Triggers on `\b(MAIL|EMAIL)\b[.,;:!?]?` - loads full mail wrapper skill
- **GMAILLM snippet**: Triggers on `\b(GMAILLM)\b[.,;:!?]?` - loads CLI-specific usage guide

Both snippets provide complementary guidance for email operations.
