# Gmail Search Syntax Reference

Complete reference for Gmail search operators. Use these with the `gmail search` command.

## Quick Start

```bash
# Basic search
gmail search "from:user@example.com"

# Combined search
gmail search "from:user@example.com has:attachment after:2024/10/01"

# Complex search
gmail search "(from:alice OR from:bob) subject:report -is:read"
```

---

## Basic Operators

### From/To/CC/BCC

```
from:sender@example.com       # Emails from sender
to:recipient@example.com      # Emails to recipient
cc:person@example.com         # CC'd to person
bcc:person@example.com        # BCC'd to person (only sent emails)
```

**Examples:**
```bash
# All emails from professor
gmail search "from:professor@university.edu" --max 20

# All emails to colleague
gmail search "to:colleague@company.com" --max 10

# Emails CC'd to manager
gmail search "cc:manager@company.com" --max 5
```

### Subject

```
subject:keyword               # Subject contains keyword
subject:"exact phrase"        # Subject contains exact phrase
subject:(word1 word2)         # Subject contains both words
```

**Examples:**
```bash
# Emails about meetings
gmail search "subject:meeting" --max 10

# Exact subject phrase
gmail search 'subject:"Weekly Report"' --max 5

# Subject with multiple keywords
gmail search "subject:(project deadline)" --max 10
```

### Body Content

```
keyword                       # Body or subject contains keyword
"exact phrase"                # Body or subject has exact phrase
```

**Examples:**
```bash
# Emails mentioning budget
gmail search "budget" --max 10

# Exact phrase in email
gmail search '"quarterly results"' --max 5
```

---

## Date Operators

### Absolute Dates

```
after:YYYY/MM/DD             # After specific date
before:YYYY/MM/DD            # Before specific date
```

**Examples:**
```bash
# Emails after October 1, 2024
gmail search "after:2024/10/01" --max 20

# Emails before September 30, 2024
gmail search "before:2024/09/30" --max 10

# Emails in date range
gmail search "after:2024/10/01 before:2024/10/31" --max 20
```

### Relative Dates

```
newer_than:Nd                # Newer than N days
older_than:Nd                # Older than N days
newer_than:Nm                # Newer than N months
older_than:Nm                # Older than N months
newer_than:Ny                # Newer than N years
older_than:Ny                # Older than N years
```

**Examples:**
```bash
# Last 7 days
gmail search "newer_than:7d" --max 20

# Older than 30 days
gmail search "older_than:30d" --max 10

# Last 2 months
gmail search "newer_than:2m" --max 20

# Last year
gmail search "newer_than:1y" --max 50
```

---

## Status Operators

### Read/Unread

```
is:read                      # Read emails
is:unread                    # Unread emails
```

**Examples:**
```bash
# All unread emails
gmail search "is:unread" --max 20

# Unread emails from specific person
gmail search "from:boss@company.com is:unread" --max 10
```

### Starred/Important

```
is:starred                   # Starred emails
is:important                 # Marked important
-is:important                # NOT important
```

**Examples:**
```bash
# Starred emails
gmail search "is:starred" --max 20

# Important emails from last week
gmail search "is:important newer_than:7d" --max 10
```

---

## Attachment Operators

### Has Attachment

```
has:attachment               # Has any attachment
has:drive                    # Has Google Drive attachment
has:document                 # Has document
has:spreadsheet              # Has spreadsheet
has:presentation             # Has presentation
has:youtube                  # Has YouTube link
```

**Examples:**
```bash
# All emails with attachments
gmail search "has:attachment" --max 20

# Emails with PDFs
gmail search "filename:pdf" --max 10

# Emails with Google Drive files
gmail search "has:drive" --max 10
```

### Filename

```
filename:name                # Attachment filename contains name
filename:pdf                 # Attachment is PDF
filename:xlsx                # Attachment is Excel file
```

**Examples:**
```bash
# Emails with PDF attachments
gmail search "filename:pdf" --max 10

# Specific filename
gmail search 'filename:"report.pdf"' --max 5

# Invoices
gmail search "filename:invoice" --max 20
```

---

## Size Operators

```
size:N                       # Larger than N bytes
larger:N                     # Larger than N (use M/K for MB/KB)
smaller:N                    # Smaller than N
```

**Examples:**
```bash
# Larger than 1MB
gmail search "larger:1M" --max 10

# Larger than 10MB
gmail search "larger:10M" --max 5

# Smaller than 500KB
gmail search "smaller:500K" --max 10

# Large emails with attachments
gmail search "has:attachment larger:5M" --max 10
```

---

## Label Operators

```
label:name                   # Has specific label
-label:name                  # Does NOT have label
```

**System labels:**
- `INBOX` - In inbox
- `SENT` - Sent emails
- `DRAFT` - Drafts
- `TRASH` - Trash
- `SPAM` - Spam
- `STARRED` - Starred
- `IMPORTANT` - Important
- `UNREAD` - Unread
- `CATEGORY_PERSONAL` - Personal category
- `CATEGORY_SOCIAL` - Social category
- `CATEGORY_PROMOTIONS` - Promotions category
- `CATEGORY_UPDATES` - Updates category
- `CATEGORY_FORUMS` - Forums category

**Examples:**
```bash
# Emails in inbox
gmail search "label:inbox" --max 20

# Archived emails (not in inbox)
gmail search "-label:inbox" --max 20

# Sent emails
gmail search "label:sent" --max 10

# Custom label
gmail search "label:work" --max 20
```

---

## Boolean Operators

### AND (implicit)

```
keyword1 keyword2            # Both keywords (space = AND)
keyword1 AND keyword2        # Explicit AND
```

**Examples:**
```bash
# Both keywords
gmail search "project deadline" --max 10

# Explicit AND
gmail search "project AND deadline" --max 10
```

### OR

```
keyword1 OR keyword2         # Either keyword
```

**Examples:**
```bash
# Emails from either person
gmail search "from:alice@example.com OR from:bob@example.com" --max 10

# Multiple subjects
gmail search "subject:meeting OR subject:schedule" --max 10
```

### NOT (-)

```
-keyword                     # Does NOT contain keyword
-operator:value              # Does NOT match operator
```

**Examples:**
```bash
# Exclude sender
gmail search "subject:report -from:manager@company.com" --max 10

# Not in inbox (archived)
gmail search "-label:inbox" --max 20

# Not read
gmail search "-is:read" --max 10
```

### Grouping ( )

```
(condition1 OR condition2)   # Group conditions
```

**Examples:**
```bash
# Emails from alice OR bob with attachments
gmail search "(from:alice OR from:bob) has:attachment" --max 10

# Multiple subjects with specific date range
gmail search "(subject:meeting OR subject:schedule) after:2024/10/01" --max 20
```

---

## Thread Operators

```
in:thread_id                 # Emails in specific thread
```

**Example:**
```bash
# Get all emails in a thread (use thread_id from email details)
gmail search "in:19abc123def456" --max 20
```

---

## Wildcard Operator

```
*                           # Wildcard (limited use in Gmail)
```

**Note:** Gmail's wildcard support is limited. It works best with:
- Email addresses: `from:*@example.com`
- Not recommended for general text searches

---

## Common Search Patterns

### Workflow-Specific Searches

#### Before Composing to Someone

Find all correspondence (sent + received):
```bash
gmail search "to:person@example.com OR from:person@example.com" --max 10
```

#### Finding Unread Important Emails

```bash
gmail search "is:unread is:important" --max 20
```

#### Recent Emails About a Topic

```bash
gmail search "subject:project-name newer_than:30d" --max 10
```

#### Emails from Team with Attachments

```bash
gmail search "(from:alice@team.com OR from:bob@team.com) has:attachment" --max 10
```

#### Large Emails to Clean Up

```bash
gmail search "larger:10M older_than:1y" --max 20
```

#### Unanswered Emails

```bash
gmail search "is:unread from:important@person.com newer_than:7d" --max 10
```

---

## Advanced Search Patterns

### Finding Email Threads

Search for initial email and use thread view:
```bash
# Find thread starter
gmail search "subject:keyword from:person@example.com" --max 5

# Then use thread command
gmail thread <message_id>
```

### Combining Multiple Criteria

```bash
# Complex search: unread emails from professor with attachments in last 30 days
gmail search "from:professor@edu.edu is:unread has:attachment newer_than:30d" --max 10

# Emails from multiple people about specific topic
gmail search "(from:alice OR from:bob) subject:budget newer_than:7d" --max 10
```

### Excluding Common Patterns

```bash
# Important emails excluding automated notifications
gmail search "is:important -from:noreply -from:no-reply" --max 20

# Emails with attachments excluding newsletters
gmail search "has:attachment -label:promotions" --max 20
```

---

## Search Best Practices

### 1. Start Broad, Then Refine

```bash
# Start broad
gmail search "project" --max 20

# Refine
gmail search "project from:alice@example.com" --max 10

# Further refine
gmail search "project from:alice@example.com after:2024/10/01" --max 5
```

### 2. Use Date Ranges for Context

```bash
# Recent context (last 7 days)
gmail search "to:person@example.com newer_than:7d" --max 5

# Historical context (last 6 months)
gmail search "to:person@example.com newer_than:6m" --max 20
```

### 3. Combine Sender and Recipient

```bash
# All correspondence with someone
gmail search "to:person@example.com OR from:person@example.com" --max 10
```

### 4. Use Labels for Organization

```bash
# Search within labeled emails
gmail search "label:work subject:report" --max 10

# Exclude certain labels
gmail search "has:attachment -label:spam -label:trash" --max 20
```

---

## CLI-Specific Options

### Max Results

```bash
# Limit results (1-50)
gmail search "query" --max 10
gmail search "query" --max 20
gmail search "query" --max 50
```

### Folder Filtering

```bash
# Search within specific folder
gmail search "is:unread" --folder INBOX --max 10
gmail search "keyword" --folder SENT --max 20
```

---

## Common Mistakes

### 1. Not Quoting Phrases

**Wrong:**
```bash
gmail search "subject:meeting notes"  # Searches for subject:meeting AND notes anywhere
```

**Right:**
```bash
gmail search 'subject:"meeting notes"'  # Searches for exact phrase in subject
```

### 2. Forgetting OR is Uppercase

**Wrong:**
```bash
gmail search "from:alice or from:bob"  # "or" treated as keyword
```

**Right:**
```bash
gmail search "from:alice OR from:bob"  # OR is operator
```

### 3. Using Wildcards for General Text

**Wrong:**
```bash
gmail search "meet*"  # Limited wildcard support
```

**Right:**
```bash
gmail search "meeting"  # Use complete words
```

### 4. Not Using Parentheses for Complex Queries

**Wrong:**
```bash
gmail search "from:alice OR from:bob has:attachment"  # Ambiguous
```

**Right:**
```bash
gmail search "(from:alice OR from:bob) has:attachment"  # Clear grouping
```

---

## Quick Reference Table

| Operator | Description | Example |
|----------|-------------|---------|
| `from:` | From sender | `from:user@example.com` |
| `to:` | To recipient | `to:user@example.com` |
| `subject:` | Subject contains | `subject:meeting` |
| `after:` | After date | `after:2024/10/01` |
| `before:` | Before date | `before:2024/10/31` |
| `newer_than:` | Newer than N days/months/years | `newer_than:7d` |
| `older_than:` | Older than N days/months/years | `older_than:30d` |
| `is:unread` | Unread emails | `is:unread` |
| `is:starred` | Starred emails | `is:starred` |
| `has:attachment` | Has attachment | `has:attachment` |
| `filename:` | Attachment filename | `filename:pdf` |
| `larger:` | Larger than size | `larger:10M` |
| `smaller:` | Smaller than size | `smaller:500K` |
| `label:` | Has label | `label:inbox` |
| `-` | NOT operator | `-from:noreply` |
| `OR` | OR operator | `from:alice OR from:bob` |
| `( )` | Grouping | `(from:a OR from:b) subject:x` |

---

## Testing Searches

Always test searches with small result sets first:

```bash
# Test with --max 5 first
gmail search "complex query here" --max 5

# If results look good, increase
gmail search "complex query here" --max 20
```

---

## Pagination

For large result sets, use pagination:

```bash
# Get first page
gmail search "query" --max 50

# Use next_page_token from results for subsequent pages
# (Python API supports this; CLI shows truncated results)
```

---

## Additional Resources

- Gmail search operators: https://support.google.com/mail/answer/7190
- gmaillm API reference: `references/api-reference.md`
