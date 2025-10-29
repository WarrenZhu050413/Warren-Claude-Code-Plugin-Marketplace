---
name: Mail Wrapper
description: LLM-friendly Python wrapper for Gmail operations using the Gmail API. Provides progressive disclosure, pagination, and structured output for reading, sending, searching, and managing emails. Use when working with email tasks including list, read, send, search, reply, label management, and batch operations.
---

# Mail Wrapper

## Email Sending Workflow

When composing emails for the user:

1. **Gather context**: Search sent emails to recipient to understand communication patterns
2. **Infer style**: Check `references/email-styles/learned/patterns.md` for recipient-specific patterns
3. **Apply guidelines**: Use base styles (STYLE.md, CLEAR.md) + learned patterns
4. **Draft email**: Compose email matching user's established style
5. **Show preview**: Display full email content to user for review
6. **Confirm**: Wait for user approval ("y/yes") or YOLO mode ("yolo")
7. **Send**: Only send after explicit confirmation

**YOLO Mode**: User can say "YOLO" or "yolo" to skip confirmation and send immediately. YOLO applies per-email only (doesn't persist).

**Signature**: Add "Sent from Claude Code" at the end of emails.

A Python library that wraps Gmail API access with an LLM-optimized interface featuring progressive disclosure, automatic pagination, and context-efficient output formatting.

## Purpose

Provide LLM-friendly email operations that minimize context usage while maximizing information utility. Unlike traditional email APIs that dump entire message contents, this wrapper offers:

- **Progressive Disclosure**: Start with summaries, request details only when needed
- **Automatic Pagination**: Default 10 results per page, max 50, with clear next-page tokens
- **Context Efficiency**: Structured markdown output, truncated bodies, human-readable IDs
- **Comprehensive Operations**: Read, send, search, reply, draft, label management, batch operations

## When to Use

Use this skill when the user requests email-related tasks:

- Listing emails from inbox or other folders
- Reading specific emails (summary or full content)
- Searching emails with Gmail query syntax
- Sending new emails or replying to existing ones
- Managing email labels (mark read/unread, star, move to folders)
- Performing batch operations on multiple emails
- Listing available folders/labels

## Core Design Principles

### 1. Progressive Disclosure

Always start with email summaries (ID, from, subject, date, snippet). Request full content only when the LLM determines it's necessary for the task.

```python
# Start with summary
email = client.read_email(message_id, format="summary")

# If needed, get full content
if needs_full_content:
    email = client.read_email(message_id, format="full")
```

### 2. Pagination by Default

Never fetch all results at once. Use pagination to respect context limits:

```python
# First page (default 10 results)
result = client.list_emails(folder='INBOX', max_results=10)

# Next page if needed
if result.next_page_token:
    next_result = client.list_emails(
        folder='INBOX',
        max_results=10,
        page_token=result.next_page_token
    )
```

### 3. Structured Output

All models include `.to_markdown()` methods that produce LLM-friendly formatted output. Use these for presenting results to the user or for LLM reasoning.

## Installation

The mail_wrapper library is located at:
```
/Users/wz/.claude/plugins/.../scripts/mail_wrapper/
```

**Install as package:**
```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/scripts/mail_wrapper
pip3 install --break-system-packages -e .
```

After installation, the `mail` command is available globally.

**Structure:**
```
scripts/mail_wrapper/
├── __init__.py
├── gmail_client.py      # Main client
├── models.py            # Pydantic models
├── utils.py             # Helper functions
├── cli.py               # Command-line interface
├── setup.py             # Package installer
├── tests/               # Test suite
└── references/
    └── email-styles/    # Style guide system
        ├── STYLE.md     # Precise writing
        ├── CLEAR.md     # Brief & direct
        └── learned/     # Grows over time
            └── patterns.md
```

## CLI Usage

The `gmail` command provides quick access to all email operations:

### Verify Setup
```bash
gmail verify
```
Checks authentication, folder access, and basic functionality.

### List Emails
```bash
gmail list                          # Default: INBOX, 10 results
gmail list --folder SENT --max 5   # List from SENT folder
```

### Read Email
```bash
gmail read <message_id>        # Summary (default)
gmail read <message_id> --full # Full body
```

### View Thread
```bash
gmail thread <message_id>
```
Shows entire conversation (all emails in thread).

### Search
```bash
gmail search "from:example@gmail.com has:attachment"
gmail search "is:unread" --max 20
```

### Reply
```bash
gmail reply <message_id> --body "Thanks for the update!"
gmail reply <message_id> --body "Thanks!" --reply-all
```
Always shows preview and asks for confirmation unless YOLO.

### Send
```bash
gmail send \
  --to user@example.com \
  --subject "Meeting Tomorrow" \
  --body "Looking forward to our meeting"

# With CC and attachments
gmail send \
  --to user1@example.com user2@example.com \
  --cc boss@example.com \
  --subject "Report" \
  --body "Attached is the report" \
  --attachments report.pdf data.xlsx

# YOLO mode (skip confirmation)
gmail send --to user@example.com --subject "Quick note" --body "Hi" --yolo
```

### List Folders
```bash
gmail folders
```

## Python Library Usage

### Initialize Client

```python
from mail_wrapper import GmailClient

# Uses existing OAuth2 credentials from Gmail MCP
client = GmailClient()
```

### List Emails

```python
# List recent emails from INBOX
result = client.list_emails(folder='INBOX', max_results=10)
print(result.to_markdown())

# List from specific folder
result = client.list_emails(folder='SENT', max_results=5)

# List with pagination
result = client.list_emails(folder='INBOX', max_results=10, page_token=token)
```

### Read Email

```python
# Get summary (default - minimal context usage)
email = client.read_email(message_id, format="summary")

# Get full email (when body content needed)
email = client.read_email(message_id, format="full")

# Display formatted output
print(email.to_markdown())
```

### Search Emails

```python
# Use Ggmail search syntax
result = client.search_emails(
    query="from:example@gmail.com has:attachment",
    folder='INBOX',
    max_results=10
)

# Common search queries:
# - "from:email@example.com"
# - "subject:invoice"
# - "has:attachment"
# - "is:unread"
# - "after:2024/10/01"
```

### Send Email

```python
from mail_wrapper import SendEmailRequest

# Create request
request = SendEmailRequest(
    to=["recipient@example.com"],
    subject="Hello",
    body="This is the email body",
    cc=["cc@example.com"],  # optional
    attachments=["/path/to/file.pdf"],  # optional
)

# Send
response = client.send_email(request)
print(response.to_markdown())
```

### Reply to Email

```python
# Reply to original sender
response = client.reply_email(
    message_id="abc123",
    body="Thank you for your email...",
    reply_all=False  # or True to reply to all recipients
)
```

### Manage Labels

```python
# Mark as read
client.modify_labels(message_id, remove_labels=['UNREAD'])

# Star an email
client.modify_labels(message_id, add_labels=['STARRED'])

# Move to folder (add/remove labels)
client.modify_labels(
    message_id,
    add_labels=['Label_5'],  # user label ID
    remove_labels=['INBOX']
)
```

### Batch Operations

```python
# Batch modify labels
result = client.batch_modify_labels(
    message_ids=['id1', 'id2', 'id3'],
    remove_labels=['UNREAD']
)
print(result.to_markdown())  # Shows success/failure counts

# Batch delete (move to trash)
result = client.batch_delete(
    message_ids=['id1', 'id2', 'id3'],
    permanent=False  # False = trash, True = permanent
)
```

### Get Folders

```python
# List all folders/labels
folders = client.get_folders()
for folder in folders:
    print(folder.to_markdown())
```

## Common Workflows

### Workflow 1: Find and Read Recent Emails

```python
# 1. List recent emails
result = client.list_emails(folder='INBOX', max_results=5)

# 2. Show summaries to user
for email in result.emails:
    print(email.to_markdown())

# 3. If user wants to read specific email, get full content
if user_requests_details:
    full_email = client.read_email(email.message_id, format="full")
    print(full_email.to_markdown())
```

### Workflow 2: Search and Bulk Archive

```python
# 1. Search for emails to archive
result = client.search_emails(
    query="from:newsletter@example.com",
    folder='INBOX',
    max_results=50
)

# 2. Confirm with user
print(f"Found {len(result.emails)} emails to archive")

# 3. Batch archive (remove INBOX label)
if user_confirms:
    message_ids = [e.message_id for e in result.emails]
    result = client.batch_modify_labels(
        message_ids,
        remove_labels=['INBOX']
    )
    print(f"Archived {len(result.successful)} emails")
```

### Workflow 3: Send and Track

```python
# 1. Send email
request = SendEmailRequest(
    to=["client@example.com"],
    subject="Project Update",
    body="Here's the latest update...",
)
response = client.send_email(request)

# 2. Get sent message ID
if response.success:
    sent_msg_id = response.message_id

    # 3. Add to custom label for tracking
    client.modify_labels(sent_msg_id, add_labels=['Label_ProjectX'])
```

## Style Guide System

The mail wrapper includes a growing style guide system at `references/email-styles/`:

### Base Styles

**STYLE.md** - Precise writing guidelines:
- Clear, personal voice
- Logical flow
- Avoid: deeply, profoundly, crucial, perfect
- Use "I think" freely in opinion pieces

**CLEAR.md** - Brevity guidelines:
- Direct answers, no preamble/postamble
- Concise over comprehensive
- Scannable structure

### Learned Patterns

**learned/patterns.md** - Grows over time:
- Recipient-specific patterns (professors vs friends)
- Common structures (apologies, follow-ups, updates)
- Observed greeting/sign-off styles

### Style Inference

When drafting emails, Claude:
1. Searches sent emails to recipient
2. Extracts patterns (greeting, tone, structure, sign-off)
3. Checks learned/patterns.md for existing rules
4. Applies STYLE.md + CLEAR.md + learned patterns
5. Shows draft for confirmation

### Growing the Guide

When consistent patterns emerge:
1. Claude notes pattern (e.g., "always uses 'Best,' with professors")
2. Suggests adding to learned/patterns.md
3. User approves or rejects
4. If approved, Claude updates patterns.md
5. Future emails automatically use pattern

**Example:**
```python
# 1. Search for style examples
sent = client.search_emails("in:sent to:professor@university.edu", max_results=3)

# 2. Observe patterns in results
# - Always "Dear Professor X,"
# - Always "Best,\nWarren"
# - Structured, formal tone

# 3. Apply patterns to new email
# 4. Add to learned/patterns.md after confirmation
```

## Authentication

The library automatically uses existing OAuth2 credentials from Gmail MCP:

- **Credentials**: `/Users/wz/.gmail-mcp/credentials.json`
- **OAuth Keys**: `/Users/wz/Desktop/OAuth2/gcp-oauth.keys.json`

If authentication fails, ensure:
1. Gmail MCP is properly set up
2. Credentials files exist at the above paths
3. OAuth tokens are not expired (auto-refresh is attempted)

## Error Handling

All operations include clear error messages:

```python
try:
    result = client.list_emails(folder='INBOX')
except RuntimeError as e:
    print(f"Error: {e}")
    # Error messages guide next steps
```

Common errors:
- **FileNotFoundError**: Credentials files missing
- **RuntimeError**: API errors (with Gmail API details)
- **ValueError**: Invalid parameters

## Output Formats

All models support `.to_markdown()` for LLM-friendly output:

- **EmailSummary**: Compact single-email view
- **EmailFull**: Full email with headers, body, attachments
- **SearchResult**: List of summaries with pagination info
- **Folder**: Label name, ID, message counts
- **SendEmailResponse**: Success confirmation or error details
- **BatchOperationResult**: Success/failure counts with failed IDs

## Testing

The library includes a comprehensive test suite:

```bash
python3 scripts/test_wrapper.py
```

Tests cover:
- Authentication
- Folder listing
- Egmail listing with pagination
- Reading (summary and full)
- Searching
- Sending
- Label modification
- Batch operations

## References

For detailed usage examples and patterns, see:

- `references/usage_examples.md` - Common patterns and workflows
- `references/gmail_search_syntax.md` - Ggmail search query guide

## Important Notes

1. **Context Efficiency**: Always use `format="summary"` unless body content is specifically needed
2. **Pagination**: Respect max_results limits (default 10, max 50)
3. **Batch Operations**: For bulk changes, use batch methods to avoid rate limits
4. **Label IDs**: System labels use names ('INBOX', 'SENT'), user labels use IDs ('Label_1', 'Label_2')
5. **Markdown Output**: Always use `.to_markdown()` for user-facing output

## Dependencies

Required packages (already installed):
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client
- pydantic>=2.0.0
- python-dateutil
