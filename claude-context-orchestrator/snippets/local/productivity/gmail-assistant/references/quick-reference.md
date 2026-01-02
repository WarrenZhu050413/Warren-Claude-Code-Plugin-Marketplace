# Gmail Assistant Quick Reference

This file provides quick examples for common gmaillm operations. Load this when you need concrete syntax examples.

## Email Sending Examples

### Basic Send

```bash
gmail send \
  --to "recipient@example.com" \
  --subject "Subject line" \
  --body "Email body content"
```

### Send with CC and BCC

```bash
gmail send \
  --to "person1@example.com,person2@example.com" \
  --cc "cc@example.com" \
  --bcc "bcc@example.com" \
  --subject "Subject" \
  --body "Body"
```

### Send to Group

```bash
gmail send \
  --to "#group-name" \
  --subject "Broadcast message" \
  --body "Message to entire group"
```

### Send with Attachments

```bash
gmail send \
  --to "recipient@example.com" \
  --subject "Files attached" \
  --body "See attachments" \
  --attachments "file1.pdf,file2.jpg"
```

## Search Examples

### Search by Subject

```bash
gmail search "subject:keyword" --max 10
```

### Search by Sender

```bash
gmail search "from:person@example.com" --max 5
```

### Search by Date Range

```bash
gmail search "after:2025/01/01 before:2025/12/31"
```

### Complex Search

```bash
gmail search "from:person subject:project has:attachment" --max 5
```

### Search Unread

```bash
gmail search "is:unread" --max 20
```

## Reading Emails

### Read Summary

```bash
gmail read <message_id>
```

### Read Full Content

```bash
gmail read <message_id> --full
```

### Read Entire Thread

```bash
gmail thread <message_id>
```

### JSON Output for Parsing

```bash
gmail read <message_id> --output-format json
```

## Group Management

### List Groups

```bash
gmail groups list
```

### Show Group Details

```bash
gmail groups show "#group-name"
```

### Create Group

```bash
gmail groups create \
  --name "#new-group" \
  --emails "person1@example.com,person2@example.com,person3@example.com"
```

### Add Member to Group

```bash
gmail groups add "#group-name" "newperson@example.com"
```

### Remove Member

```bash
gmail groups remove "#group-name" "person@example.com"
```

### Validate Group

```bash
gmail groups validate "#group-name"
```

## Style Management

### List All Styles

```bash
gmail styles list
```

### Show Style Content

```bash
gmail styles show <style-name>
```

### Create New Style

```bash
gmail styles create --name "my-style"
# Opens editor for you to define the style
```

### Edit Existing Style

```bash
gmail styles edit <style-name>
```

### Validate Style Format

```bash
gmail styles validate <style-name>
```

### Validate All Styles

```bash
gmail styles validate-all
```

## Workflow Management

### List Workflows

```bash
gmail workflows list
```

### Show Workflow Details

```bash
gmail workflows show <workflow-id>
```

### Create Workflow

```bash
gmail workflows create \
  --id "daily-review" \
  --name "Daily Email Review" \
  --query "is:unread -label:spam" \
  --auto-mark-read
```

### Run Workflow

```bash
gmail workflows run <workflow-id>
```

### Run Ad-hoc Query

```bash
gmail workflows run --query "is:unread from:important@person.com"
```

## Gmail Query Syntax

Common Gmail search operators:

| Operator | Example | Description |
|----------|---------|-------------|
| `from:` | `from:alice@example.com` | Emails from sender |
| `to:` | `to:bob@example.com` | Emails to recipient |
| `subject:` | `subject:meeting` | Subject contains word |
| `is:unread` | `is:unread` | Unread emails |
| `is:read` | `is:read` | Read emails |
| `has:attachment` | `has:attachment` | Has attachments |
| `label:` | `label:important` | Has label |
| `after:` | `after:2025/01/01` | After date (YYYY/MM/DD) |
| `before:` | `before:2025/12/31` | Before date |
| `newer_than:` | `newer_than:7d` | Last N days (d/m/y) |
| `older_than:` | `older_than:1m` | Older than N time |
| `OR` | `from:alice OR from:bob` | Either condition |
| `-` | `-label:spam` | Exclude (NOT) |

**Combine operators:**
```bash
gmail search "from:boss subject:urgent is:unread"
```

## Email Style Format

Email styles use YAML frontmatter + XML-like sections:

```markdown
---
name: "style-name"
description: "When to use: Context description (30-200 chars)."
---

<examples>
Example 1
---
Example 2
</examples>

<greeting>
- "Hi [Name],"
</greeting>

<body>
- Guideline 1
- Guideline 2
</body>

<closing>
- "Best,"
</closing>

<do>
- Best practice 1
</do>

<dont>
- What to avoid
</dont>
```

Required sections in strict order: examples → greeting → body → closing → do → dont

## Common Email Workflows

### 1. Research + Draft + Send

```bash
# Search for similar emails
gmail search "subject:similar topic" --max 3

# Read one for context
gmail read <message_id> --full

# Check style
gmail styles show professional-formal

# TEST first
gmail send --to fuchengwarrenzhu@gmail.com --subject "[TEST] ..." --body "..."

# Send for real
gmail send --to real@email.com --subject "..." --body "..." --yolo
```

### 2. Bulk Processing with Workflow

```bash
# Create workflow for common query
gmail workflows create \
  --id "newsletter-cleanup" \
  --name "Clean Up Newsletters" \
  --query "label:newsletters is:read older_than:30d"

# Run workflow
gmail workflows run newsletter-cleanup
```

### 3. Group Broadcast

```bash
# Verify group
gmail groups show "#team"

# Check style
gmail styles show posts

# TEST
gmail send --to fuchengwarrenzhu@gmail.com --subject "[TEST] Update" --body "..."

# Broadcast
gmail send --to "#team" --subject "Update" --body "..." --yolo
```

## Status and Configuration

### Check Account Status

```bash
gmail status
```

### Verify Authentication

```bash
gmail verify
```

### Show Configuration

```bash
gmail config show
```

### List Labels

```bash
gmail labels list
```

## JSON Output for Automation

All commands support `--output-format json` for programmatic parsing:

```bash
# Get JSON for parsing
gmail search "is:unread" --output-format json | jq '.emails[] | {from: .from_.email, subject: .subject}'

# List groups in JSON
gmail groups list --output-format json

# Read email as JSON
gmail read <message_id> --output-format json
```

## Common Gotchas

1. **Email IDs**: Displayed short (12 chars) but use full ID in commands
2. **Group prefix**: Always use `#` prefix (e.g., `#team` not `team`)
3. **YOLO flag**: Skips confirmation, use after testing
4. **Date format**: Use YYYY/MM/DD for Gmail queries
5. **Test emails**: ALWAYS test to fuchengwarrenzhu@gmail.com first
6. **Style order**: Sections must be in exact order (examples, greeting, body, closing, do, dont)
7. **Attachment paths**: Use absolute or relative file paths, comma-separated
