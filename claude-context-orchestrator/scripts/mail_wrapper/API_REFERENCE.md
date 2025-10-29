# Mail Wrapper API Reference

Complete reference for mail_wrapper Python library and CLI.

## Table of Contents
- [Python Library API](#python-library-api)
- [CLI Commands](#cli-commands)
- [Models & Types](#models--types)
- [Gmail Search Syntax](#gmail-search-syntax)

---

## Python Library API

### GmailClient

```python
from mail_wrapper import GmailClient

client = GmailClient(
    credentials_file="/Users/wz/.gmail-mcp/credentials.json",  # optional
    oauth_keys_file="/Users/wz/Desktop/OAuth2/gcp-oauth.keys.json"  # optional
)
```

### Core Operations

#### verify_setup()
Verify authentication and basic functionality.

```python
result = client.verify_setup()
# Returns: {
#     'auth': bool,
#     'folders': int,
#     'inbox_accessible': bool,
#     'errors': List[str]
# }
```

#### list_emails()
List emails with pagination.

```python
result = client.list_emails(
    folder='INBOX',        # Gmail label/folder
    max_results=10,        # 1-50, default 10
    page_token=None,       # For pagination
    query=None             # Gmail search query
)
# Returns: SearchResult
```

**Example:**
```python
# First page
result = client.list_emails(folder='INBOX', max_results=10)
for email in result.emails:
    print(email.to_markdown())

# Next page
if result.next_page_token:
    next_result = client.list_emails(
        folder='INBOX',
        max_results=10,
        page_token=result.next_page_token
    )
```

#### read_email()
Read a specific email.

```python
email = client.read_email(
    message_id,           # Required: message ID
    format="summary"      # "summary" | "full"
)
# Returns: EmailSummary | EmailFull
```

**Formats:**
- `"summary"` (default): ID, from, to, subject, date, snippet, labels
- `"full"`: Everything + body (plain text & HTML), attachments

**Example:**
```python
# Get summary first (minimal context)
summary = client.read_email(msg_id, format="summary")
print(summary.to_markdown())

# Get full if body needed
full = client.read_email(msg_id, format="full")
print(full.body_plain)
```

#### search_emails()
Search emails using Gmail query syntax.

```python
result = client.search_emails(
    query,                # Gmail search query
    folder='INBOX',       # Optional: limit to folder
    max_results=10        # 1-50, default 10
)
# Returns: SearchResult
```

**Example:**
```python
result = client.search_emails(
    query="from:professor@university.edu has:attachment after:2024/10/01",
    max_results=20
)
```

#### get_thread()
Get all emails in a conversation thread.

```python
messages = client.get_thread(message_id)
# Returns: List[EmailSummary] (chronologically sorted)
```

**Example:**
```python
thread = client.get_thread(msg_id)
print(f"Thread has {len(thread)} messages")
for i, msg in enumerate(thread, 1):
    print(f"[{i}] {msg.from_.email} → {msg.to[0].email if msg.to else 'unknown'}")
    print(f"    {msg.subject}")
```

#### send_email()
Send a new email.

```python
from mail_wrapper import SendEmailRequest

request = SendEmailRequest(
    to=["user@example.com"],           # Required: list of recipients
    subject="Subject",                  # Required: string
    body="Email body",                  # Required: string
    cc=["cc@example.com"],             # Optional: list
    attachments=["/path/to/file.pdf"]  # Optional: list of file paths
)

response = client.send_email(request)
# Returns: SendEmailResponse
```

**Example:**
```python
request = SendEmailRequest(
    to=["friend@gmail.com"],
    subject="Quick Question",
    body="Hey, are you free tomorrow?\n\nBest,\nWarren"
)
response = client.send_email(request)
if response.success:
    print(f"Sent! Message ID: {response.message_id}")
```

#### reply_email()
Reply to an existing email.

```python
response = client.reply_email(
    message_id,           # Required: original message ID
    body,                 # Required: reply body text
    reply_all=False       # Optional: reply to all recipients
)
# Returns: SendEmailResponse
```

**Example:**
```python
response = client.reply_email(
    message_id="19abc123",
    body="Thanks for the update!",
    reply_all=False
)
```

#### get_folders()
List all Gmail labels/folders.

```python
folders = client.get_folders()
# Returns: List[Folder]
```

**Example:**
```python
folders = client.get_folders()
for folder in folders:
    print(f"{folder.name}: {folder.unread_count} unread")
```

#### modify_labels()
Add or remove labels from an email.

```python
client.modify_labels(
    message_id,                    # Required: message ID
    add_labels=['STARRED'],        # Optional: labels to add
    remove_labels=['UNREAD']       # Optional: labels to remove
)
```

**Common operations:**
```python
# Mark as read
client.modify_labels(msg_id, remove_labels=['UNREAD'])

# Star email
client.modify_labels(msg_id, add_labels=['STARRED'])

# Archive (remove from inbox)
client.modify_labels(msg_id, remove_labels=['INBOX'])

# Move to trash
client.modify_labels(msg_id, add_labels=['TRASH'])
```

#### batch_modify_labels()
Modify labels on multiple emails at once.

```python
result = client.batch_modify_labels(
    message_ids=['id1', 'id2', 'id3'],  # Required: list of message IDs
    add_labels=['Label_5'],              # Optional: labels to add
    remove_labels=['UNREAD']             # Optional: labels to remove
)
# Returns: BatchOperationResult
```

**Example:**
```python
# Mark all as read
message_ids = [email.message_id for email in search_result.emails]
result = client.batch_modify_labels(
    message_ids,
    remove_labels=['UNREAD']
)
print(f"Marked {len(result.successful)} emails as read")
```

#### delete_email()
Delete a single email.

```python
success = client.delete_email(
    message_id,           # Required: message ID
    permanent=False       # Optional: True = permanent, False = trash
)
# Returns: bool
```

#### batch_delete()
Delete multiple emails at once.

```python
result = client.batch_delete(
    message_ids=['id1', 'id2', 'id3'],  # Required: list
    permanent=False                      # Optional: True = permanent
)
# Returns: BatchOperationResult
```

---

## CLI Commands

All commands use the `mail` entry point. For now, use:
```bash
python3 -m mail_wrapper.cli <command>
```

Or create an alias:
```bash
alias gmail='python3 -m mail_wrapper.cli'
```

### gmail verify
Check authentication and setup.

```bash
gmail verify
```

### gmail list
List emails from a folder.

```bash
gmail list                          # Default: INBOX, 10 results
gmail list --folder SENT            # List from SENT folder
gmail list --max 20                 # Get 20 results
gmail list --query "is:unread"     # With search query
```

**Options:**
- `--folder FOLDER` - Folder/label to list from (default: INBOX)
- `--max N` - Maximum results (1-50, default: 10)
- `--query QUERY` - Gmail search query

### gmail read
Read a specific email.

```bash
gmail read <message_id>        # Summary (default)
gmail read <message_id> --full # Full body
```

**Options:**
- `--full` - Show full email body (instead of summary)

### gmail thread
Show entire email conversation.

```bash
gmail thread <message_id>
```

### gmail search
Search emails.

```bash
gmail search "from:example@gmail.com"
gmail search "has:attachment" --max 20
gmail search "is:unread after:2024/10/01" --folder INBOX
```

**Options:**
- `--folder FOLDER` - Limit search to folder (default: INBOX)
- `--max N` - Maximum results (1-50, default: 10)

### gmail reply
Reply to an email.

```bash
gmail reply <message_id> --body "Thanks!"
gmail reply <message_id> --body "Sounds good" --reply-all
```

**Options:**
- `--body TEXT` - Required: reply body text
- `--reply-all` - Reply to all recipients (default: reply to sender only)

**Confirmation:** Always shows preview and asks "Send? (y/n/yolo)"

### gmail send
Send a new email.

```bash
gmail send \
  --to user@example.com \
  --subject "Subject" \
  --body "Body text"

# With multiple recipients
gmail send \
  --to user1@example.com user2@example.com \
  --cc boss@example.com \
  --subject "Report" \
  --body "See attached" \
  --attachments report.pdf data.xlsx

# Skip confirmation with YOLO mode
gmail send --to user@example.com --subject "Test" --body "Hi" --yolo
```

**Options:**
- `--to EMAIL [EMAIL...]` - Required: recipient email(s)
- `--subject TEXT` - Required: email subject
- `--body TEXT` - Required: email body
- `--cc EMAIL [EMAIL...]` - Optional: CC recipient(s)
- `--attachments FILE [FILE...]` - Optional: file path(s) to attach
- `--yolo` - Skip confirmation, send immediately

### gmail folders
List all available folders/labels.

```bash
gmail folders
```

---

## Models & Types

### EmailSummary
Brief email overview (minimal context).

**Fields:**
- `message_id: str` - Unique message ID
- `thread_id: str` - Thread/conversation ID
- `from_: EmailAddress` - Sender
- `to: List[EmailAddress]` - Recipients
- `subject: str` - Email subject
- `date: datetime` - Sent date/time
- `snippet: str` - Short preview (~100 chars)
- `labels: List[str]` - Gmail labels
- `has_attachments: bool` - Has files attached
- `is_unread: bool` - Unread status

**Methods:**
- `to_markdown() -> str` - Formatted output

### EmailFull
Complete email with body (use sparingly).

**Fields:** (All EmailSummary fields plus:)
- `body_plain: str` - Plain text body
- `body_html: str` - HTML body (if exists)
- `attachments: List[Attachment]` - Attached files
- `headers: Dict[str, str]` - All email headers

### EmailAddress
Email address with optional name.

**Fields:**
- `email: str` - Email address
- `name: Optional[str]` - Display name

### SearchResult
Paginated search results.

**Fields:**
- `emails: List[EmailSummary]` - Email summaries
- `total_count: int` - Total matching emails
- `query: str` - Search query used
- `next_page_token: Optional[str]` - Token for next page

**Methods:**
- `to_markdown() -> str` - Formatted output

### Folder
Gmail label/folder info.

**Fields:**
- `id: str` - Label ID
- `name: str` - Label name
- `type: str` - 'system' or 'user'
- `message_count: Optional[int]` - Total messages
- `unread_count: Optional[int]` - Unread messages

### SendEmailRequest
Email sending parameters.

**Fields:**
- `to: List[str]` - Required: recipient emails
- `subject: str` - Required: subject line
- `body: str` - Required: email body
- `cc: Optional[List[str]]` - CC recipients
- `attachments: Optional[List[str]]` - File paths

### SendEmailResponse
Email send result.

**Fields:**
- `success: bool` - Send succeeded
- `message_id: str` - Sent message ID
- `thread_id: str` - Thread ID
- `error: Optional[str]` - Error message if failed

### BatchOperationResult
Batch operation results.

**Fields:**
- `successful: List[str]` - Successful message IDs
- `failed: List[str]` - Failed message IDs
- `errors: Dict[str, str]` - Error messages by ID

---

## Gmail Search Syntax

### Basic Operators

**From/To:**
```
from:user@example.com       # Emails from user
to:user@example.com         # Emails to user
cc:user@example.com         # CC'd to user
bcc:user@example.com        # BCC'd to user
```

**Subject:**
```
subject:invoice             # Subject contains "invoice"
subject:(invoice payment)   # Subject contains both words
```

**Dates:**
```
after:2024/10/01           # After date
before:2024/10/31          # Before date
older_than:7d              # Older than 7 days
newer_than:2d              # Newer than 2 days
```

**Status:**
```
is:unread                  # Unread emails
is:read                    # Read emails
is:starred                 # Starred emails
is:important               # Marked important
```

**Content:**
```
has:attachment             # Has attachments
has:drive                  # Has Google Drive attachment
has:document               # Has document attachment
has:spreadsheet            # Has spreadsheet
has:presentation           # Has presentation
```

**Size:**
```
size:1000000              # Larger than 1MB
larger:10M                # Larger than 10MB
smaller:5M                # Smaller than 5MB
```

**Labels:**
```
label:inbox               # In INBOX
label:sent                # In SENT
-label:inbox              # NOT in inbox (archived)
```

### Boolean Operators

```
AND     # Both conditions (implicit, can be omitted)
OR      # Either condition
-       # NOT (exclude)
()      # Grouping
```

**Examples:**
```
from:professor@edu AND has:attachment
from:alice OR from:bob
subject:report -from:manager
(from:alice OR from:bob) has:attachment
```

### Advanced Examples

**Unread emails from specific person with attachments:**
```
from:john@example.com is:unread has:attachment
```

**Recent emails about project:**
```
subject:project after:2024/10/01 -label:trash
```

**Important emails not yet read:**
```
is:important is:unread -from:noreply
```

**Large emails with PDFs:**
```
has:attachment filename:pdf larger:5M
```

**Emails in thread:**
```
in:thread_id
```

---

## Quick Reference Card

### Python Library Cheat Sheet
```python
from mail_wrapper import GmailClient, SendEmailRequest

client = GmailClient()

# List
result = client.list_emails(folder='INBOX', max_results=10)

# Read
email = client.read_email(msg_id, format="summary")
email = client.read_email(msg_id, format="full")

# Search
result = client.search_emails("from:user@example.com has:attachment")

# Thread
thread = client.get_thread(msg_id)

# Send
request = SendEmailRequest(to=["user@example.com"], subject="Hi", body="Hello")
response = client.send_email(request)

# Reply
response = client.reply_email(msg_id, body="Thanks!", reply_all=False)

# Labels
client.modify_labels(msg_id, add_labels=['STARRED'], remove_labels=['UNREAD'])

# Batch
client.batch_modify_labels(ids, remove_labels=['UNREAD'])
```

### CLI Cheat Sheet
```bash
gmail verify                                    # Check setup
gmail list --folder INBOX --max 10             # List emails
gmail read <id> --full                         # Read email
gmail thread <id>                              # View conversation
gmail search "is:unread" --max 20              # Search
gmail reply <id> --body "Thanks!"              # Reply
gmail send --to user@example.com \            # Send
  --subject "Test" --body "Hi"
gmail folders                                  # List folders
```

---

## Authentication

Uses existing Gmail MCP OAuth2 credentials:
- **Credentials:** `/Users/wz/.gmail-mcp/credentials.json`
- **OAuth Keys:** `/Users/wz/Desktop/OAuth2/gcp-oauth.keys.json`

Tokens auto-refresh. If authentication fails:
1. Check credential files exist
2. Verify OAuth tokens not expired
3. Run `gmail verify` to diagnose

---

## Common Patterns

### Progressive Disclosure
```python
# Always start with summary
summaries = client.list_emails(max_results=10)

# Only get full content when needed
for summary in summaries.emails:
    if "important keyword" in summary.subject.lower():
        full = client.read_email(summary.message_id, format="full")
        # Process full email
```

### Pagination
```python
all_emails = []
page_token = None

while True:
    result = client.list_emails(max_results=50, page_token=page_token)
    all_emails.extend(result.emails)

    if not result.next_page_token:
        break
    page_token = result.next_page_token
```

### Error Handling
```python
try:
    response = client.send_email(request)
    if response.success:
        print(f"Sent: {response.message_id}")
    else:
        print(f"Failed: {response.error}")
except RuntimeError as e:
    print(f"Error: {e}")
```

---

## Style Guide System

Located at `references/email-styles/`:
- **STYLE.md** - Precise writing guidelines
- **CLEAR.md** - Brevity guidelines
- **learned/patterns.md** - User-specific patterns (grows over time)

When drafting emails, Claude:
1. Searches sent emails to recipient
2. Extracts patterns (greeting, tone, sign-off)
3. Applies STYLE + CLEAR + learned patterns
4. Shows preview for confirmation

---

## Additional Resources

- **SKILL.md** - Complete usage guide with workflows
- **README.md** - Quick start and installation
- **references/usage_examples.md** - 16 detailed examples
- **references/gmail_search_syntax.md** - Complete search reference
