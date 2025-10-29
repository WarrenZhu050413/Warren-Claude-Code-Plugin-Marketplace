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

**Typical LLM Workflow:**

When user asks to "process emails" or "handle my inbox":

1. **Create or use workflow**:
   ```bash
   gmail workflows start gmaillm-inbox --output-format json
   ```

2. **Loop through emails autonomously**:
   ```bash
   # For each email in JSON response:
   # - Read email summary
   # - Determine action (archive, skip, reply, read)
   # - Execute: gmail workflows continue <token> <action> --output-format json
   # - Repeat until has_more: false
   ```

3. **Summary**:
   - Show user what was done (e.g., "Archived 5 newsletters, replied to 2 emails")

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

**For LLMs (Programmatic/Non-Interactive Mode):**

This is the preferred mode for Claude to process workflows autonomously:

```bash
# 1. Start workflow - gmaillm generates a token and returns first email
gmail workflows start gmaillm-inbox

# Returns JSON automatically:
# {
#   "success": true,
#   "token": "abc123...",  # AUTO-GENERATED by gmaillm (expires in 1 hour)
#   "email": { "id": "...", "from": "...", "subject": "...", "snippet": "..." },
#   "progress": { "total": 10, "processed": 0, "remaining": 10, "current": 1 }
# }

# 2. Process current email - Claude decides action based on content
gmail workflows continue <token> archive           # Archive and move to next
gmail workflows continue <token> skip              # Skip and move to next
gmail workflows continue <token> reply -b "..."    # Reply, archive, and move to next
gmail workflows continue <token> read              # Get full email content

# 3. Repeat step 2 for each email until progress.remaining == 0
```

**How Token-Based Workflow Works:**

1. **Token Generation** (`gmail workflows start`):
   - gmaillm creates a unique token (e.g., "abc123...")
   - Token represents a workflow session
   - Stores: email list, current position, actions taken
   - Expires after 1 hour

2. **Token Usage** (`gmail workflows continue <token> <action>`):
   - Token is passed to identify which workflow session
   - gmaillm looks up stored state
   - Processes current email with specified action
   - Updates state (position, actions log)
   - Returns new token (same session, updated state)
   - Returns next email

3. **State Tracking**:
   ```json
   {
     "token": "abc123...",
     "progress": {
       "total": 10,      // Total emails in workflow
       "processed": 3,    // How many processed so far
       "remaining": 7,    // How many left
       "current": 4       // Current email position
     },
     "completed": false   // true when remaining == 0
   }
   ```

4. **Workflow Lifecycle**:
   - **Start**: `gmail workflows start <name>` → creates token
   - **Continue**: `gmail workflows continue <token> <action>` → processes, returns updated token
   - **Complete**: When `progress.remaining == 0` or `completed: true`
   - **Expire**: Token expires after 1 hour (workflow must be restarted)

5. **Actions and State Changes**:
   - `view` - Return full email body (no state change, stays on same email)
   - `archive` - Archive email, advance to next
   - `skip` - Skip email (mark read if configured), advance to next
   - `reply -b "..."` - Send reply, archive, advance to next
   - `quit` - End workflow session immediately

**Key Properties:**
- **Stateful**: Token remembers position and history
- **Resumable**: Same token continues from where you left off
- **Single-session**: Each `start` creates a new token
- **Auto-cleanup**: Expired tokens are cleaned up automatically

**Token Storage and Persistence:**

- **Location**: `~/.gmaillm/workflow-states/`
- **Format**: Each token stored as a file (e.g., `abc123.json`)
- **Contains**: Email list, current position, actions taken, timestamp
- **Persisted to disk**: YES - survives computer restarts
- **Expiration**: Files older than 1 hour are considered expired
- **Cleanup**: Run `gmail workflows cleanup` to remove expired state files

**What Happens on Computer Restart:**

✅ **Token survives**: State file is on disk, not in memory
✅ **Can resume**: If within 1 hour, `gmail workflows continue <token>` works
❌ **Expires after 1 hour**: Even if computer stays on, token expires
⚠️ **Cleanup needed**: Old state files accumulate until manually cleaned

**Example:**
```bash
# Start workflow
gmail workflows start gmaillm-inbox
# Returns: token="abc123"

# Computer restarts (within 1 hour)

# Resume workflow - WORKS because state is on disk
gmail workflows continue abc123 archive

# After 1 hour - token expires
gmail workflows continue abc123 archive
# Error: Token expired (older than 1 hour)

# Clean up old state files
gmail workflows cleanup
```

**Programmatic Workflow Pattern (for Claude):**

1. **Start workflow**: `gmail workflows start <name> --output-format json`
2. **For each email**:
   - Read the email summary from JSON response
   - Determine action based on content:
     - `archive` - Archive and continue
     - `skip` - Skip and continue
     - `reply -b "message"` - Reply and continue
     - `read` - Get full content (then decide)
     - `stop` - Stop processing workflow
3. **Continue until** `has_more: false`

**Example LLM workflow execution:**

```python
# User: "Process my gmaillm inbox and archive newsletters"

# 1. Start workflow
response = run("gmail workflows start gmaillm-inbox --output-format json")
token = response["token"]

# 2. Process each email
while response["has_more"]:
    email = response["email"]

    # Decide action based on email content
    if "newsletter" in email["from"].lower():
        action = "archive"
    elif needs_full_content(email):
        # Get full email to decide
        full = run(f"gmail workflows continue {token} read --output-format json")
        action = determine_action(full["email"]["body"])
    else:
        action = "skip"

    # Execute action
    response = run(f"gmail workflows continue {token} {action} --output-format json")

# 3. Done when has_more: false
```

**For Humans (Interactive Mode):**

```bash
# Run interactively - shows each email and prompts for action
gmail workflows run gmaillm-inbox

# At each email, user types: archive, skip, reply, read, stop
```

**Key Difference:**
- **Interactive (`run`)**: Human types actions one by one
- **Programmatic (`start`/`continue`)**: LLM decides actions autonomously in a loop

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
