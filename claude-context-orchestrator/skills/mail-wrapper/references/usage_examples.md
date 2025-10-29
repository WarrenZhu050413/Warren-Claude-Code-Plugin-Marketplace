# Mail Wrapper Usage Examples

Comprehensive examples for common email operations.

## Table of Contents

1. [Basic Operations](#basic-operations)
2. [Advanced Searching](#advanced-searching)
3. [Email Management](#email-management)
4. [Batch Operations](#batch-operations)
5. [Complex Workflows](#complex-workflows)

## Basic Operations

### Example 1: Check Unread Emails

```python
from mail_wrapper import GmailClient

client = GmailClient()

# Search for unread emails
result = client.search_emails(
    query="is:unread",
    folder='INBOX',
    max_results=20
)

print(f"You have {len(result.emails)} unread emails:\n")
for email in result.emails:
    print(f"- {email.subject}")
    print(f"  From: {email.from_}")
    print(f"  Date: {email.date.strftime('%Y-%m-%d %H:%M')}\n")
```

### Example 2: Read Email with Attachments

```python
# Get email summary first
email = client.read_email(message_id, format="summary")

if email.has_attachments:
    # Get full details to see attachment list
    full_email = client.read_email(message_id, format="full")

    print(f"Email: {full_email.subject}")
    print(f"\nAttachments ({len(full_email.attachments)}):")
    for att in full_email.attachments:
        print(f"  - {att.filename} ({att.size_human})")
```

### Example 3: Send Email with CC and Attachments

```python
from mail_wrapper import SendEmailRequest

request = SendEmailRequest(
    to=["john@example.com", "jane@example.com"],
    cc=["manager@example.com"],
    subject="Q4 Report",
    body="Please find attached the Q4 financial report.",
    attachments=["/Users/wz/Documents/Q4_Report.pdf"],
)

response = client.send_email(request)

if response.success:
    print(f"✅ Email sent! Message ID: {response.message_id}")
else:
    print(f"❌ Failed: {response.error}")
```

## Advanced Searching

### Example 4: Find Emails from Date Range

```python
# Find emails from last week
result = client.search_emails(
    query="after:2024/10/19 before:2024/10/26",
    folder='INBOX',
    max_results=30
)

print(f"Found {result.total_count} emails from last week")
```

### Example 5: Search with Multiple Criteria

```python
# Find unread emails with attachments from specific sender
result = client.search_emails(
    query="from:client@example.com has:attachment is:unread",
    folder='INBOX'
)

for email in result.emails:
    print(email.to_markdown())
```

### Example 6: Search Across All Folders

```python
# Search without folder restriction
result = client.list_emails(
    folder='',  # empty = search all mail
    query="subject:invoice",
    max_results=50
)
```

## Email Management

### Example 7: Archive Old Emails

```python
# Find old emails in inbox
old_emails = client.search_emails(
    query="before:2024/01/01",
    folder='INBOX',
    max_results=100
)

# Archive by removing INBOX label
message_ids = [e.message_id for e in old_emails.emails]
result = client.batch_modify_labels(
    message_ids,
    remove_labels=['INBOX']
)

print(f"Archived {len(result.successful)} emails")
```

### Example 8: Mark All as Read

```python
# Get unread emails
unread = client.search_emails(
    query="is:unread",
    folder='INBOX',
    max_results=50
)

# Mark all as read
if unread.emails:
    message_ids = [e.message_id for e in unread.emails]
    result = client.batch_modify_labels(
        message_ids,
        remove_labels=['UNREAD']
    )
    print(f"Marked {len(result.successful)} emails as read")
```

### Example 9: Star Important Emails

```python
# Find emails from VIP sender
vip_emails = client.search_emails(
    query="from:boss@company.com is:unread",
    folder='INBOX'
)

# Star them
for email in vip_emails.emails:
    client.modify_labels(email.message_id, add_labels=['STARRED'])
    print(f"⭐ Starred: {email.subject}")
```

## Batch Operations

### Example 10: Clean Up Newsletter Subscriptions

```python
# Find all emails from newsletter
newsletters = client.search_emails(
    query="from:newsletter@example.com",
    folder='INBOX',
    max_results=100
)

print(f"Found {len(newsletters.emails)} newsletter emails")

# Option 1: Archive them
message_ids = [e.message_id for e in newsletters.emails]
archive_result = client.batch_modify_labels(
    message_ids,
    remove_labels=['INBOX']
)

# Option 2: Or delete them (move to trash)
# delete_result = client.batch_delete(message_ids, permanent=False)

print(f"Processed {len(archive_result.successful)} emails")
if archive_result.failed:
    print(f"Failed to process {len(archive_result.failed)} emails")
```

### Example 11: Organize by Label

```python
# Get all folders first
folders = client.get_folders()

# Find the "Projects" label
projects_label = next(
    (f for f in folders if f.name == 'Projects'),
    None
)

if projects_label:
    # Find project-related emails
    project_emails = client.search_emails(
        query="subject:project OR subject:milestone",
        folder='INBOX'
    )

    # Move to Projects folder
    message_ids = [e.message_id for e in project_emails.emails]
    client.batch_modify_labels(
        message_ids,
        add_labels=[projects_label.id],
        remove_labels=['INBOX']
    )
```

## Complex Workflows

### Example 12: Email Digest Creation

```python
# Get today's emails
from datetime import datetime

today = datetime.now().strftime("%Y/%m/%d")
result = client.search_emails(
    query=f"after:{today}",
    folder='INBOX',
    max_results=50
)

# Create digest
digest = f"# Daily Email Digest ({today})\n\n"
digest += f"Total: {result.total_count} emails\n\n"

for i, email in enumerate(result.emails, 1):
    digest += f"{i}. **{email.subject}**\n"
    digest += f"   From: {email.from_}\n"
    digest += f"   _{email.snippet}_\n\n"

print(digest)

# Optionally email the digest to yourself
request = SendEmailRequest(
    to=["me@example.com"],
    subject=f"Email Digest - {today}",
    body=digest,
)
client.send_email(request)
```

### Example 13: Auto-Reply to Specific Senders

```python
# Find unanswered emails from VIP
vip_emails = client.search_emails(
    query="from:vip@example.com is:unread",
    folder='INBOX',
    max_results=10
)

for email in vip_emails.emails:
    # Send auto-reply
    response = client.reply_email(
        message_id=email.message_id,
        body=(
            "Thank you for your email. "
            "I'm currently out of office and will respond when I return."
        ),
        reply_all=False
    )

    if response.success:
        # Mark as read
        client.modify_labels(email.message_id, remove_labels=['UNREAD'])
        print(f"✅ Auto-replied to: {email.subject}")
```

### Example 14: Pagination Through Large Results

```python
all_emails = []
page_token = None

# Get all SENT emails (potentially thousands)
while True:
    result = client.list_emails(
        folder='SENT',
        max_results=50,  # max per page
        page_token=page_token
    )

    all_emails.extend(result.emails)

    print(f"Fetched {len(result.emails)} emails (total: {len(all_emails)})")

    # Check if more pages exist
    if not result.next_page_token:
        break

    page_token = result.next_page_token

    # Safety: stop after 10 pages (500 emails) for testing
    if len(all_emails) >= 500:
        break

print(f"Total emails fetched: {len(all_emails)}")
```

### Example 15: Find and Summarize Thread

```python
# Get an email
email = client.read_email(message_id, format="full")

# Find all emails in the same thread
thread_emails = client.search_emails(
    query=f"rfc822msgid:{email.message_id}",
    folder='',  # search all mail
    max_results=50
)

print(f"Thread: {email.subject}")
print(f"Emails in thread: {len(thread_emails.emails)}\n")

for i, thread_email in enumerate(thread_emails.emails, 1):
    print(f"{i}. {thread_email.from_} - {thread_email.date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   {thread_email.snippet}\n")
```

### Example 16: Email Backup to Files

```python
import json
from pathlib import Path

# Get recent emails
result = client.list_emails(folder='INBOX', max_results=100)

# Create backup directory
backup_dir = Path('/Users/wz/email_backup')
backup_dir.mkdir(exist_ok=True)

for email in result.emails:
    # Get full content
    full_email = client.read_email(email.message_id, format="full")

    # Save as JSON
    backup_file = backup_dir / f"{email.message_id}.json"
    with open(backup_file, 'w') as f:
        json.dump({
            'subject': full_email.subject,
            'from': str(full_email.from_),
            'to': [str(addr) for addr in full_email.to],
            'date': full_email.date.isoformat(),
            'body': full_email.body_plain or full_email.body_html,
            'labels': full_email.labels,
        }, f, indent=2)

    print(f"Backed up: {email.subject}")

print(f"Backup complete: {len(result.emails)} emails saved to {backup_dir}")
```

## Tips

1. **Always start with summaries**: Use `format="summary"` unless you specifically need email body
2. **Use pagination**: Never fetch more than 50 results at once
3. **Batch operations**: Use `batch_*` methods for multiple emails to avoid rate limits
4. **Test queries**: Test search queries with small `max_results` first
5. **Check response**: Always check `response.success` after sending emails
6. **Label IDs**: Get label IDs with `client.get_folders()` before modifying labels
7. **Thread-safe**: The client handles OAuth token refresh automatically
