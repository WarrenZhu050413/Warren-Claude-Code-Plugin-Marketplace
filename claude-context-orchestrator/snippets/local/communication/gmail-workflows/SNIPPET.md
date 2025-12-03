---
description: "Gmail CLI patterns for composing, searching, and managing emails"
SNIPPET_NAME: gmail-workflows
ANNOUNCE_USAGE: true
---

# Gmail Workflows Context

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: gmail-workflows

If multiple snippets are detected, combine them:

📎 **Active Contexts**: gmail-workflows, snippet2, snippet3

---

**VERIFICATION_HASH:** `gmail_v1_20251107`

## Trigger Keywords

This snippet should be active when:
- User mentions: "gmail", "email", "send email", "draft email", "compose", "reply"
- User uses email addresses in task description
- User asks about past emails or conversations
- User says "GMAIL" (all caps) to explicitly trigger

## Auto-Invoke Skill

When gmail triggers detected, **ALWAYS invoke the gmail-assistant skill first**:

```
Use the Skill tool with skill="gmail-assistant"
```

This loads complete gmail workflow documentation and best practices.

## Quick Reference (When Skill Not Needed)

For simple gmail queries or when skill already loaded:

### Before Composing
1. Search past emails to recipient(s) to extract patterns
2. Check available email styles with `gmail styles list`
3. Draft combining past patterns + style + current context
4. **ALWAYS test to fuchengwarrenzhu@gmail.com first**
5. Review preview then send to real recipient

### Essential Commands

**Search & Discovery:**
```bash
gmail list --folder ALL --query "keyword"              # Search all folders
gmail list --folder SENT --query "to:person@example"   # Find past emails to someone
gmail list --folder ALL --query "from:person@example"  # Find emails from someone
```

**Read & Context:**
```bash
gmail read <message_id>                                # Summary view (snippet only)
gmail read <message_id> --full                         # Full email body
gmail thread <thread_id>                               # View entire conversation
```

**Send & Reply:**
```bash
gmail send --to user@example.com --subject "X" --body "Y" --yolo
gmail reply <message_id> --body "Reply text" --yolo
```

### Current Limitations & Workarounds

#### Getting Full Email Body
- `gmail read <id>` returns truncated snippets (~100 chars)
- **Workaround:** Use `--full` flag (if implemented) or read raw API

#### Finding CC'd Recipients
- `gmail read` output doesn't show CC/BCC recipients
- **Workaround:** Use Python to extract headers:

```python
from gmaillm.gmail_client import GmailClient
client = GmailClient()
msg = client.service.users().messages().get(
    userId='me', id='<message_id>', format='full'
).execute()
headers = msg['payload']['headers']
cc = [h['value'] for h in headers if h['name'].lower() == 'cc']
print(f"CC: {cc}")
```

#### Thread Context
- No single command to view full thread
- **Workaround:**
  1. Find thread: `gmail list --folder ALL --query "subject:keyword"`
  2. Note thread_id from results
  3. Read each message individually with `--full`

### Common Patterns

**Pattern 1: Draft reply based on email thread**
1. Search: `gmail list --folder ALL --query "subject keywords"`
2. Read messages: `gmail read <id>` for each
3. Extract context: who's involved, what's been discussed
4. Use Python workaround if CC extraction needed
5. Draft reply matching tone
6. Send with appropriate recipients

**Pattern 2: Find contact information**
1. Search inbox: `gmail list --query "from:[name]"`
2. Search sent: `gmail list --folder SENT --query "to:[name]"`
3. Extract email from results
4. If not found, search web (LinkedIn, org directory)

**Pattern 3: Compose with style**
1. Check past emails to recipient for patterns
2. List styles: `gmail styles list`
3. View specific style: `gmail styles show professional-formal`
4. Draft combining recipient's expected style + situation
5. Test send first

## Notes

- Default search folder should be ALL (not just INBOX)
- Always use `--yolo` flag to skip confirmation prompts
- Test emails go to fuchengwarrenzhu@gmail.com
- Real recipient emails: wzhu@college.harvard.edu (work), fuchengwarrenzhu@gmail.com (personal)
