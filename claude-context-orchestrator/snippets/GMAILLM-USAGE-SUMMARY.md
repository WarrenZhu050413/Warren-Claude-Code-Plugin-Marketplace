# GMAILLM Usage Summary - What Claude Knows

## Overview

When you type **GMAILLM** in your prompt, Claude receives comprehensive usage guidance without needing to read source code.

## What Information Is Available

### ✅ **Core Commands** (Quick Reference)
```bash
gmail verify                                    # Check setup
gmail list --folder INBOX --max-results 10     # List emails
gmail read <message_id>                         # Read (summary)
gmail search "from:someone@example.com"         # Search
gmail send --to "#team" --subject "Hi" --body "..." # Send to group
gmail reply <message_id> --body "Thanks!"       # Reply
```

### ✅ **Groups Management**
```bash
gmail groups list                               # List all groups
gmail groups show team                          # Show group details
gmail groups create project-team user1@ex.com user2@ex.com
gmail groups validate                           # Validate all groups
gmail groups examples                           # See usage patterns
```

**Key Pattern:** Always quote `"#groupname"` (shell interprets `#` as comment)

### ✅ **Styles Management**
```bash
gmail styles list                               # List all styles
gmail styles show professional-formal           # Show style
gmail styles create my-style                    # Create new style
gmail styles examples                           # See usage + LLM guide
```

**LLM USE Section:** The `styles examples` command includes a dedicated section showing how LLMs should:
1. Determine relevant style from user context
2. Retrieve style guidelines
3. Apply style rules when composing
4. Match style to context

### ✅ **Workflows Management**

**Creating Workflows:**
```bash
# Create workflow for specific alias
gmail workflows create gmaillm-inbox \
  --query "to:wzhu+gmaillm@college.harvard.edu" \
  --name "GmailLM Messages" \
  --description "Process emails sent to +gmaillm alias"

# Create workflow for unread emails
gmail workflows create daily-clear \
  --query "is:unread in:inbox" \
  --auto-mark-read

# Create project-specific workflow
gmail workflows create proj-alpha \
  --query "label:Projects/Alpha is:unread"
```

**Common Gmail Search Queries:**
- `to:user+tag@domain.com` - Emails to specific alias
- `from:sender@example.com` - Emails from specific sender
- `is:unread` - Unread emails only
- `is:important` - Important emails
- `has:attachment` - Emails with attachments
- `in:inbox` - Emails in inbox
- `label:Projects/Alpha` - Emails with specific label
- `after:2024/10/01` - Emails after date
- Combine: `from:user@example.com is:unread`

**Running Workflows:**
```bash
# Interactive mode
gmail workflows run gmaillm-inbox

# Programmatic mode (LLM-friendly)
gmail workflows start gmaillm-inbox              # Returns token
gmail workflows continue <token> archive          # Archive current
gmail workflows continue <token> skip             # Skip to next
gmail workflows continue <token> reply -b "..."   # Reply and archive
```

**Workflow Management:**
```bash
gmail workflows list                              # List all
gmail workflows show gmaillm-inbox                # Show details
gmail workflows delete gmaillm-inbox              # Delete
```

### ✅ **Programmatic Action Patterns**

#### SEND Pattern
1. Search previous emails to recipient (context gathering)
2. Determine appropriate style (professional/casual)
3. Load style guidelines with `gmail styles show <style>`
4. Draft email matching learned patterns
5. Show preview to user
6. Wait for confirmation ("yes"/"y") or YOLO
7. Send with `gmail send --to "..." --subject "..." --body "..."`
8. Suggest creating group/style/workflow if pattern emerges

#### READ Pattern
1. List emails with `gmail list --folder INBOX --max-results 10`
2. Show summaries to user
3. Read summary: `gmail read <message_id>` (efficient)
4. Read full only if needed: `gmail read <message_id> --output-format full`

#### WORKFLOW Pattern
1. List: `gmail workflows list`
2. Show: `gmail workflows show <name>`
3. Create: `gmail workflows create <id> --query "..."`
4. Run: `gmail workflows run <name>`
5. Suggest creating workflow if user performs repeated tasks

### ✅ **Post-Action Suggestions**

**After SENDING:**
```
✅ Email sent successfully!

💡 I noticed you sent to alice@ex.com, bob@ex.com, and carol@ex.com.
   Would you like me to create a group for these recipients?

   Suggested name: "project-alpha"

   To create: gmail groups create project-alpha alice@ex.com bob@ex.com carol@ex.com

   Create this group? (yes/no)
```

**After WORKFLOW:**
```
✅ Task completed!

💡 This workflow could be automated:
   - Search: "from:newsletter@example.com"
   - Action: Archive (remove INBOX label)

   Would you like me to create a workflow for this?

   Suggested name: "archive-newsletters"

   Create this workflow? (yes/no)
```

### ✅ **Key Patterns**

1. **Always quote `"#groupname"`** - Shell interprets `#` as comment
2. **Preview before send** - No automatic sending without confirmation
3. **Suggest reusables** - Proactively identify opportunities for groups/styles/workflows
4. **Progressive disclosure** - Start with summaries, request full content only when needed
5. **Context efficiency** - Use `--max-results` to limit output (default: 10)

## ⚠️ **IMPORTANT: Never Read Source Code**

The GMAILLM snippet **explicitly instructs Claude**:

> **IMPORTANT:** Always use the `examples` command to learn about features. **Never read source code** to understand how to use gmaillm.

**Why:**
- Examples show **how to USE** the CLI, not how it's IMPLEMENTED
- Examples include real-world patterns and workflows
- Examples are designed for LLM consumption (structured, clear)
- Reading source code wastes context and provides wrong information

**Instead of reading code, use:**
```bash
gmail groups examples      # Group usage patterns
gmail styles examples      # Style usage + LLM guide
gmail workflows examples   # Workflow creation and usage
```

## Testing the Snippet

```bash
cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/scripts
python3 snippets_cli.py test gmaillm "Use GMAILLM to create workflow"
```

Expected:
```
✓ Pattern matched
  name: gmaillm
  pattern: \b(GMAILLM)\b[.,;:!?]?
  matches: ['GMAILLM']
  matched: True
```

## Example Interaction

**User:** "GMAILLM. How do I create a workflow for emails to wzhu+gmaillm@college.harvard.edu?"

**Claude response (using GMAILLM snippet, NOT reading source code):**
```
To create a workflow for emails sent to wzhu+gmaillm@college.harvard.edu, use:

gmail workflows create gmaillm-inbox \
  --query "to:wzhu+gmaillm@college.harvard.edu" \
  --name "GmailLM Messages" \
  --description "Process emails sent to +gmaillm alias"

Then run it with:

# Interactive mode (shows each email)
gmail workflows run gmaillm-inbox

# Or programmatic mode (LLM-friendly)
gmail workflows start gmaillm-inbox
```

**No source code reading required!**

## Files

- **Snippet:** `snippets/gmaillm-usage.md` (344 lines)
- **Config:** `scripts/config.local.json` (pattern entry)
- **Documentation:** `snippets/README-GMAILLM.md`
- **This summary:** `snippets/GMAILLM-USAGE-SUMMARY.md`

## Verification Hash

`gmaillm-usage-v2-2025-10-28` (updated with workflow details)

---

**Last Updated:** 2025-10-28
**Status:** ✅ Active and tested
