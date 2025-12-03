---
name: "gmail-assistant"
description: "Use when composing, sending, searching, or managing Warren's emails via gmail CLI. Covers drafting with styles, finding similar emails for context, managing groups, discovering contacts online, and email workflows. Always test to fuchengwarrenzhu@gmail.com before real sends."
---

# Gmail Assistant

Use this skill when working with email through the `gmail` CLI tool.

## Quick Commands

- `/gmail` - Quick reference for common gmail CLI commands
- `/gmail::setup` - Set up Gmail CLI authentication

## Core Principles

**ALWAYS before composing:**
1. Search past emails to recipient(s) → extract patterns (greeting, tone, sign-off)
2. Check available email styles → match context
3. Test to fuchengwarrenzhu@gmail.com FIRST
4. Review preview → then send to real recipient

**Progressive disclosure:**
- Start with summaries (`gmail list`, `gmail search`)
- Read full content only when needed (`--full`)
- Get thread context only if required (`gmail thread`)

---

## Essential Commands

### Search & Discovery
```bash
gmail search "to:person@example.com" --max 10        # Emails to someone
gmail search "from:person@example.com" --max 10      # Emails from someone
gmail search "subject:keyword after:2024/10/01"      # By subject + date
gmail search "has:attachment filename:pdf"           # With attachments
gmail list --folder INBOX --max 10                   # List inbox
gmail folders                                        # List all folders/labels
```

### Read & View
```bash
gmail read <message_id>                              # Summary view
gmail read <message_id> --full                       # Full content
gmail read <message_id> --full-thread                # Full content with thread context
gmail thread <message_id>                            # View entire thread
gmail thread <message_id> --strip-quotes             # View thread without quoted content
```

### Send & Reply
```bash
# Send from file (preferred for composed emails)
gmail send --to user@example.com --subject "X" --body "$(cat /tmp/email/draft.txt)"
gmail send --to user@example.com --subject "X" --body "$(cat /tmp/email/draft.txt)" --attachment file.pdf

# Send inline (for quick replies only)
gmail send --to user@example.com --subject "X" --body "Y"
gmail reply <message_id> --body "Reply text"
gmail reply <message_id> --body "Reply" --reply-all
```

### Email Styles
```bash
gmail styles list                                    # List all styles
gmail styles show professional-formal                # View specific style
gmail styles validate style-name                     # Validate format
```

**Common styles:** `professional-formal`, `professional-friendly`, `casual-friend`, `brief-reply`

### Email Groups
```bash
gmail groups list                                    # List all groups
gmail groups show team                               # Show group members
gmail groups add team person@example.com             # Add member
gmail send --to @team --subject "X" --body "Y"       # Use group
```

### Workflows
```bash
gmail workflows list                                 # List workflows
gmail workflows run clear                            # Run interactively
gmail workflows start clear                          # Start programmatic (JSON)
gmail workflows continue <token> archive             # Continue with action
```

---

## Important Workflow Guidelines

### Composing Emails
1. Search past emails to recipient → extract greeting/tone/sign-off patterns
2. Check relevant email styles (`gmail styles list`)
3. Draft combining past patterns + style + current context
4. **Write draft to `/tmp/email/{descriptive_name}.txt`**
5. Open file for user review/editing (use `open` command on macOS)
6. **Test to fuchengwarrenzhu@gmail.com first** using file: `gmail send --to fuchengwarrenzhu@gmail.com --subject "..." --body "$(cat /tmp/email/{name}.txt)" --yolo`
7. After user confirms, send to real recipient using same file

### Extracting Email Style from Past Emails
1. Search relevant past emails: `gmail search "to:@harvard.edu" --folder SENT --max 10`
2. Read full content: `gmail read <message_id> --full`
3. Note patterns:
   - **Greeting**: Formal (Dear Professor) vs. casual (Hi)
   - **Tone**: Professional, friendly, concise
   - **Structure**: Sections (Why/Preparation/Commitment), bullet points, paragraphs
   - **Sign-off**: Best regards, Thanks, etc.
   - **Signature**: Contact info format
4. Match these patterns in new draft for consistency

### Replying to Emails
1. Read original email (`gmail read <id> --full`)
2. Check thread if needed (`gmail thread <id>`)
3. Search past emails from sender to match their style
4. Draft appropriate reply → review preview → send

### Finding Contacts
1. Search inbox: `gmail search "from:[name]"`
2. Search sent: `gmail search "to:[name]"`
3. Check groups: `gmail groups list`
4. If not found → search web (LinkedIn, org directories)
5. Confirm with user before using new emails

---

## Extracting Email Context

### Getting Full Thread Conversation

**Recommended approach:**
```bash
# Use gmail thread to view entire conversation
gmail thread <message_id>                  # Show full thread
gmail thread <message_id> --strip-quotes   # Remove quoted content for clarity
gmail thread <message_id> --output-format json  # Get JSON format
```

**Alternative (manual assembly):**
```bash
# 1. Find thread
gmail list --folder ALL --query "keyword"

# 2. Get all message IDs in thread
# Note thread_id from results

# 3. Read each message with full body
gmail read <id> --full

# 4. Piece together conversation manually
```

### Finding CC'd Recipients

If `gmail read` output doesn't show CC/BCC recipients (current limitation), use Python workaround:

```python
from gmaillm.gmail_client import GmailClient

client = GmailClient()
msg = client.service.users().messages().get(
    userId='me',
    id='<message_id>',
    format='full'
).execute()

headers = msg['payload']['headers']

# Extract CC recipients
cc = [h['value'] for h in headers if h['name'].lower() == 'cc']
to = [h['value'] for h in headers if h['name'].lower() == 'to']
from_ = [h['value'] for h in headers if h['name'].lower() == 'from']

print(f"From: {from_}")
print(f"To: {to}")
print(f"CC: {cc}")
```

### Common Pattern: Draft Reply Based on Thread

**Complete workflow:**
1. Search for thread: `gmail list --folder ALL --query "subject:keywords"`
2. Note message IDs and thread_id from results
3. Read each message for context: `gmail read <id>` (or `--full` for body)
4. Extract who's involved:
   - If CC not visible, use Python workaround above
   - Note all participants from From/To/CC fields
5. Draft reply matching tone and context
6. Include appropriate recipients (reply vs reply-all)
7. Send with `--yolo` to skip confirmation

**Example:**
```bash
# Find thread
gmail list --folder ALL --query "MLD courses" --output-format json

# Read messages
gmail read 19a5a90f97be8df8

# Extract CC (if needed)
# Use Python script above

# Send reply with CC
gmail send --to "mksmith@hks.harvard.edu" --cc "Greg_Dorchak@hks.harvard.edu" --subject "Reply" --body "..." --yolo
```

---

## Gmail Search Operators

**People:** `from:`, `to:`, `cc:`, `bcc:`
**Date:** `after:YYYY/MM/DD`, `before:YYYY/MM/DD`, `newer_than:7d`, `older_than:30d`
**Status:** `is:unread`, `is:starred`, `is:important`, `is:read`
**Content:** `subject:keyword`, `has:attachment`, `has:drive`, `filename:pdf`
**Size:** `larger:10M`, `smaller:5M`
**Boolean:** `OR`, `-` (NOT), `()` (grouping)

**Examples:**
- All correspondence: `to:person@example.com OR from:person@example.com`
- Recent thread: `subject:project after:2024/10/01`
- Unread important: `is:unread is:important`
- With PDF: `has:attachment filename:pdf`

---

## Key Things to Know

**Email Styles:**
- Located in `~/.gmaillm/email-styles/`
- Common: `professional-formal`, `professional-friendly`, `casual-friend`, `brief-reply`
- View with `gmail styles show <name>`
- Use for guidance on tone, greetings, closings

**Configuration:**
- All settings in `~/.gmaillm/`
- First time: `gmail setup-auth`
- Verify: `gmail verify`

**Best Practices:**
- Search past emails before composing → extract patterns
- Use progressive disclosure → summaries first, full content only when needed
- Test to fuchengwarrenzhu@gmail.com before real sends
- Leverage email groups for recurring distributions
- Match recipient's formality level

**Common Mistakes to Avoid:**
- Sending without searching first
- Wrong formality level (too casual or too formal)
- Skipping test emails
- Not using groups for recurring sends
- Getting full email when summary sufficient

---

## References

For detailed information when needed:
- `references/email-styles.md` - Complete styles guide
- `references/gmail-search-syntax.md` - Full search syntax
- `references/api-reference.md` - Complete API docs