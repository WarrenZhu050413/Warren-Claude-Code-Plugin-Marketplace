# Gmail Search Syntax Reference

Complete guide to Gmail search operators for use with `client.search_emails()`.

## Basic Operators

### From / To

```python
# Emails from specific sender
query = "from:john@example.com"

# Emails to specific recipient
query = "to:jane@example.com"

# Emails from domain
query = "from:@example.com"
```

### Subject

```python
# Emails with specific subject
query = "subject:invoice"

# Exact phrase in subject
query = "subject:\"monthly report\""

# Multiple words (AND)
query = "subject:(budget meeting)"
```

### Date Operators

```python
# After specific date
query = "after:2024/10/01"

# Before specific date
query = "before:2024/10/31"

# Date range
query = "after:2024/10/01 before:2024/10/31"

# Relative dates
query = "newer_than:7d"  # last 7 days
query = "older_than:1y"  # older than 1 year
```

Date formats:
- `YYYY/MM/DD` - e.g., `2024/10/26`
- Relative: `1d` (day), `1w` (week), `1m` (month), `1y` (year)

### Attachments

```python
# Has any attachment
query = "has:attachment"

# Specific filename
query = "filename:report.pdf"

# File type
query = "filename:pdf"
query = "filename:jpg"
```

## Status Operators

### Read Status

```python
# Unread emails
query = "is:unread"

# Read emails
query = "is:read"
```

### Starred / Important

```python
# Starred emails
query = "is:starred"

# Important (marked by Gmail)
query = "is:important"
```

### Labels

```python
# In specific folder
query = "label:inbox"
query = "label:sent"
query = "label:drafts"

# Custom labels (use label ID)
query = "label:projects"
```

## Boolean Operators

### AND

```python
# Multiple conditions (space or AND)
query = "from:boss@company.com is:unread"
query = "subject:urgent AND has:attachment"
```

### OR

```python
# Either condition
query = "from:alice@example.com OR from:bob@example.com"
query = "subject:invoice OR subject:receipt"
```

### NOT / Minus

```python
# Exclude condition
query = "-from:newsletter@example.com"
query = "NOT label:spam"
```

### Grouping

```python
# Use parentheses for complex queries
query = "(from:alice OR from:bob) AND has:attachment"
query = "subject:(meeting OR conference) -is:read"
```

## Content Search

### Body Text

```python
# Search in email body
query = "deadline November"

# Exact phrase
query = "\"please review the attached document\""

# Words near each other
query = "AROUND 10 invoice payment"  # within 10 words
```

### Size

```python
# Larger than size (in bytes)
query = "size:1000000"  # 1MB
query = "larger:10M"     # 10MB

# Smaller than size
query = "smaller:1M"     # 1MB
```

## Special Operators

### Thread

```python
# Emails in same thread
query = "rfc822msgid:message-id-here"
```

### CC / BCC

```python
# CC'd emails
query = "cc:manager@example.com"

# BCC'd emails (only your sent mail)
query = "bcc:secret@example.com"
```

### List / Category

```python
# Mailing list
query = "list:announcements@example.com"

# Gmail categories
query = "category:social"
query = "category:promotions"
query = "category:updates"
query = "category:forums"
```

### Has

```python
# Has attachments
query = "has:attachment"

# Has YouTube video
query = "has:youtube"

# Has Google Drive link
query = "has:drive"

# Has document
query = "has:document"
query = "has:spreadsheet"
query = "has:presentation"
```

## Common Query Examples

### Find Unprocessed Work Emails

```python
query = "is:unread -category:promotions -category:social after:2024/10/20"
```

### Find Large Emails with Attachments

```python
query = "has:attachment larger:10M"
```

### Find Invoices from Last Quarter

```python
query = "subject:invoice after:2024/07/01 before:2024/09/30"
```

### Find Emails from Team Members

```python
query = "from:@mycompany.com -list:announcements is:unread"
```

### Find Old Newsletters to Clean Up

```python
query = "older_than:6m (from:newsletter OR subject:newsletter)"
```

### Find Starred Emails with Specific Subject

```python
query = "is:starred subject:project"
```

### Find Emails with PDF Attachments

```python
query = "filename:pdf after:2024/01/01"
```

### Find Important Unread Emails

```python
query = "is:important is:unread -category:promotions"
```

### Find Emails in Thread

```python
query = "subject:\"project update\" in:inbox"
```

### Find Draft Emails

```python
query = "in:draft"
```

## Advanced Examples

### Complex Multi-Criteria Search

```python
# Unread emails from VIPs with attachments from last week
query = (
    "(from:boss@company.com OR from:client@example.com) "
    "has:attachment is:unread newer_than:7d"
)
```

### Exclude Multiple Senders

```python
# All emails except from specific senders
query = "-from:spam@example.com -from:newsletter@example.com is:unread"
```

### Find Specific File Types

```python
# Find all spreadsheets
query = "(filename:xlsx OR filename:xls OR filename:csv) has:attachment"
```

### Date Range with Content

```python
# Emails about deadlines from last month
query = "deadline after:2024/09/01 before:2024/09/30"
```

### Find Emails You Need to Reply To

```python
# Important unread emails from last 3 days that you haven't replied to
query = "is:unread is:important newer_than:3d -label:sent"
```

## Tips for Effective Searching

1. **Start Broad, Refine**: Begin with simple queries, add operators to narrow results
2. **Use Quotes**: For exact phrases, use quotes: `"exact phrase"`
3. **Combine Operators**: Mix date, status, and content operators for precise results
4. **Test First**: Test complex queries with small `max_results` before running full search
5. **Case Insensitive**: All searches are case-insensitive
6. **Partial Matching**: Gmail searches use partial word matching
7. **Recent Results**: More recent emails appear first by default

## Operator Precedence

When mixing operators:
1. Parentheses `()` - highest precedence
2. NOT or `-`
3. AND (implicit with space)
4. OR - lowest precedence

Example:
```python
# These are equivalent:
query = "from:alice OR from:bob AND has:attachment"
query = "from:alice OR (from:bob AND has:attachment)"  # bob's emails with attachments OR any from alice

# To get both with attachments:
query = "(from:alice OR from:bob) AND has:attachment"
```

## Common Pitfalls

### 1. Forgetting Quotes for Phrases

```python
# Wrong - searches for "monthly" OR "report"
query = "subject:monthly report"

# Correct - searches for exact phrase
query = "subject:\"monthly report\""
```

### 2. Date Format

```python
# Wrong
query = "after:10/26/2024"

# Correct
query = "after:2024/10/26"
```

### 3. Label Names

```python
# Wrong - spaces not supported
query = "label:my projects"

# Correct - use label ID or no spaces
query = "label:Label_5"
```

### 4. Operator Spacing

```python
# Wrong - needs no space
query = "is: unread"

# Correct
query = "is:unread"
```

## Using Search in Code

```python
from mail_wrapper import GmailClient

client = GmailClient()

# Simple search
result = client.search_emails(
    query="is:unread",
    folder='INBOX',
    max_results=10
)

# Complex search
result = client.search_emails(
    query=(
        "(from:boss@company.com OR from:client@example.com) "
        "has:attachment is:unread newer_than:7d"
    ),
    folder='',  # search all mail, not just INBOX
    max_results=50
)

# Display results
print(result.to_markdown())
```

## References

- [Official Gmail Search Operators](https://support.google.com/mail/answer/7190)
- [Advanced Search Tips](https://support.google.com/mail/answer/7190)
