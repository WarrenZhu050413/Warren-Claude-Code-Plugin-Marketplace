---
name: GmailLM Usage
description: Context injection for gmaillm CLI usage patterns, programmatic actions, and workflow suggestions
pattern: \b(GMAILLM)\b[.,;:!?]?
---

# GmailLM CLI Usage Guide

**TRIGGERED BY**: User mentioned "gmaillm" - providing contextual usage guidance.

---

## Quick Reference

### Core Commands

```bash
# Verify setup
gmail verify

# List emails
gmail list --folder INBOX --max-results 10
gmail list --output-format json

# Read email
gmail read <message_id>                    # Summary
gmail read <message_id> --output-format full

# Search
gmail search "from:someone@example.com"
gmail search "is:unread" --max-results 20

# Send (always shows preview unless --dry-run or --force)
gmail send --to user@example.com --subject "Hi" --body "Message"
gmail send --to "#team" --subject "Update" --body "..." --dry-run

# Reply
gmail reply <message_id> --body "Thanks!"
```

### Groups, Styles, Workflows

```bash
# Groups
gmail groups list
gmail groups show team
gmail groups create project-team user1@ex.com user2@ex.com
gmail groups validate

# Styles
gmail styles list
gmail styles show professional-formal
gmail styles create my-style
gmail styles examples  # See LLM usage guide

# Workflows
gmail workflows list
gmail workflows run weekly-digest
```

---

## Programmatic Action Patterns

When the user requests email operations, follow these patterns:

### 📧 SEND Pattern

**Workflow:**
1. **Gather context** (if sending to known recipient):
   ```bash
   gmail search "in:sent to:recipient@example.com" --max-results 3 --output-format json
   ```
   - Analyze previous emails for tone, greeting, sign-off patterns
   - Check for existing style in `gmail styles list`

2. **Determine style**:
   - Check if user specified style (e.g., "formal", "casual")
   - If not specified, infer from context:
     - Client/professor → professional-formal
     - Team member → professional-friendly
     - Friend → casual-friendly
   - Use `gmail styles show <style-name>` to load guidelines

3. **Draft email**:
   - Apply style guidelines (greeting, body structure, closing, do/don't rules)
   - Follow learned patterns from step 1
   - Add signature: "Sent from Claude Code"

4. **Preview and confirm**:
   - Show full email content to user
   - **CRITICAL**: Wait for explicit confirmation ("yes"/"y") or force flag
   - If user says "YOLO", use `--force` to skip confirmation

5. **Send**:
   ```bash
   gmail send --to "recipient@example.com" --subject "..." --body "..." [--force if YOLO]
   ```

6. **Post-send suggestions** (see below)

**Example interaction:**
```
User: "Email John about the project update"

Claude:
1. Searches: gmail search "in:sent to:john@example.com" --max-results 3
2. Observes: Always uses "Hi John," and "Best,"
3. Drafts email matching pattern
4. Shows preview
5. Waits for confirmation
6. Sends with: gmail send --to "john@example.com" --subject "..." --body "..."
7. Suggests: "Would you like me to create a 'project-updates' group or workflow?"
```

### 📖 READ Pattern

**Workflow:**
1. **List context**:
   ```bash
   gmail list --folder INBOX --max-results 10
   ```
   - Show summaries to user
   - Let user identify which email to read

2. **Read summary first**:
   ```bash
   gmail read <message_id>
   ```
   - Default format is summary (efficient)

3. **Read full if needed**:
   ```bash
   gmail read <message_id> --output-format full
   ```
   - Only request full content if user needs body details

### 🔄 WORKFLOW Pattern

**Creating Workflows:**

To create a workflow for specific email patterns:

```bash
# Create workflow for specific recipient
gmail workflows create gmaillm-inbox \
  --query "to:wzhu+gmaillm@college.harvard.edu" \
  --name "GmailLM Messages" \
  --description "Process emails sent to +gmaillm alias"

# Create workflow for unread emails
gmail workflows create daily-clear \
  --query "is:unread in:inbox" \
  --auto-mark-read

# Create workflow with specific label
gmail workflows create proj-alpha \
  --query "label:Projects/Alpha is:unread"
```

**Running Workflows:**

```bash
# Interactive mode (shows each email, prompts for actions)
gmail workflows run gmaillm-inbox

# Programmatic mode (LLM-friendly with continuation tokens)
gmail workflows start gmaillm-inbox           # Returns token
gmail workflows continue <token> archive       # Archive current email
gmail workflows continue <token> skip          # Skip to next
gmail workflows continue <token> reply -b "Thanks!"  # Reply and archive
```

**Common Gmail Search Queries:**

- `to:user+tag@domain.com` - Emails sent to specific alias
- `from:sender@example.com` - Emails from specific sender
- `is:unread` - Unread emails only
- `is:important` - Important emails
- `has:attachment` - Emails with attachments
- `in:inbox` - Emails in inbox
- `label:Projects/Alpha` - Emails with specific label
- `after:2024/10/01` - Emails after date
- Combine with AND: `from:user@example.com is:unread`

**Workflow Management:**

```bash
# List all workflows
gmail workflows list

# Show workflow details
gmail workflows show gmaillm-inbox

# Delete workflow
gmail workflows delete gmaillm-inbox
```

**When to Suggest New Workflow:**

Suggest creating a workflow if user:
- Performs same search/action repeatedly
- Mentions processing specific email patterns
- Asks about automating email tasks

---

## Post-Action Suggestions

After completing email operations, **proactively suggest** creating reusable resources:

### After SENDING email:

**Suggest GROUP if:**
- User sent to multiple recipients together
- Same recipients mentioned in conversation context
- Pattern: "team", "project members", "clients"

**Example:**
```
✅ Email sent successfully!

💡 I noticed you sent to alice@ex.com, bob@ex.com, and carol@ex.com.
   Would you like me to create a group for these recipients?

   Suggested name: "project-alpha"

   To create: gmail groups create project-alpha alice@ex.com bob@ex.com carol@ex.com

   Create this group? (yes/no)
```

**Suggest STYLE if:**
- User gave specific tone/format instructions (e.g., "make it formal", "keep it brief")
- Consistent pattern for specific recipient type (e.g., always formal with professors)

**Example:**
```
✅ Email sent successfully!

💡 I used a formal, structured tone for this professor email.
   Would you like me to save this as a reusable style?

   Suggested name: "professor-formal"

   This would capture:
   - Greeting: "Dear Professor [Name],"
   - Tone: Formal, structured
   - Closing: "Best regards,\n[Your Name]"

   Create this style? (yes/no)
```

### After RUNNING workflow:

**Suggest WORKFLOW if:**
- User performs same multi-step email task repeatedly
- Pattern involves search + action (e.g., "archive all newsletters")

**Example:**
```
✅ Task completed!

💡 This workflow could be automated:
   - Search: "from:newsletter@example.com"
   - Action: Archive (remove INBOX label)

   Would you like me to create a workflow for this?

   Suggested name: "archive-newsletters"

   Create this workflow? (yes/no)
```

---

## Implementation Instructions

When suggesting resources:

1. **Always ask before creating** - Never create groups/styles/workflows without explicit user approval
2. **Provide clear preview** - Show exactly what will be created
3. **Suggest meaningful names** - Use context to propose good names (not "group1", "style1")
4. **Show command** - Display the exact command that will be run
5. **Execute only after "yes"** - Wait for confirmation before running create command

**Confirmation keywords:**
- YES: "yes", "y", "sure", "go ahead", "create it", "yep", "yeah"
- NO: "no", "n", "skip", "not now", "later", "nope"

---

## Special Flags

- `--dry-run`: Preview email without sending (useful for testing group expansion)
- `--force`: Skip confirmation prompts (use with YOLO mode)
- `--output-format json`: Get machine-readable output
- `--output-format rich`: Human-readable formatted output (default)

---

## Key Patterns

1. **Always use quotes around `#groupname`** - Shell interprets `#` as comment
   ```bash
   # ✅ Correct
   gmail send --to "#team" --subject "Update"

   # ❌ Wrong
   gmail send --to #team --subject "Update"
   ```

2. **Preview before send** - Always show email content to user before sending
3. **Suggest reusables** - Proactively identify opportunities for groups/styles/workflows
4. **Progressive disclosure** - Start with summaries, request full content only when needed
5. **Context efficiency** - Use `--max-results` to limit output (default: 10)

---

## Examples Command

**IMPORTANT:** Always use the `examples` command to learn about features. **Never read source code** to understand how to use gmaillm.

```bash
gmail groups examples      # Group usage patterns
gmail styles examples      # Style usage + LLM guide
gmail workflows examples   # Workflow creation and usage patterns
```

**Why use `examples` instead of reading code:**
- Examples show **how to use** the CLI, not how it's implemented
- Examples include real-world patterns and workflows
- Examples are designed for LLM consumption (structured, clear)
- Reading source code wastes context and provides wrong information

**The `styles examples` command includes a dedicated "🤖 LLM USE" section showing how to:**
1. Determine relevant style from user context
2. Retrieve style guidelines
3. Apply style rules when composing
4. Match style to context (client, team, casual)

---

**VERIFICATION_HASH:** `gmaillm-usage-v1-2025-10-28`
