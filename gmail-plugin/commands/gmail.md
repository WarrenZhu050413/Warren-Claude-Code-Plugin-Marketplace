---
description: Guide for using the gmail CLI to send, search, and manage emails
---

# Gmail CLI Usage Guide

Use the `gmail` CLI for all email operations.

## Quick Reference

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
gmail read <message_id> --full-thread                # Full with thread context
gmail thread <message_id>                            # View entire thread
gmail thread <message_id> --strip-quotes             # Thread without quoted content
```

### Send & Reply
```bash
# Send from file (preferred for composed emails)
gmail send --to user@example.com --subject "X" --body "$(cat /tmp/email/draft.txt)"
gmail send --to user@example.com --subject "X" --body "$(cat /tmp/email/draft.txt)" --attachment file.pdf

# Send inline (for quick messages)
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

## Composing Emails - Best Practices

### Before Writing
1. **Search past emails** to recipient to extract greeting/tone/sign-off patterns
2. **Check email styles** with `gmail styles list` to match context
3. **Always test** to fuchengwarrenzhu@gmail.com before real sends

### Workflow
1. Draft email to `/tmp/email/{descriptive_name}.txt`
2. Open file for user review with `open /tmp/email/{name}.txt`
3. Test send: `gmail send --to fuchengwarrenzhu@gmail.com --subject "..." --body "$(cat /tmp/email/{name}.txt)" --yolo`
4. After user confirms, send to real recipient

## Configuration

- **Config directory:** `~/.gmaillm/`
- **Email styles:** `~/.gmaillm/email-styles/`
- **Email groups:** `~/.gmaillm/email-groups.json`
- **Credentials:** `~/.gmaillm/credentials.json`

## Troubleshooting

```bash
# Verify setup
gmail verify

# Check account status
gmail status

# Re-authenticate if needed
gmail setup-auth
```

## Related Commands

- `/gmail:setup` - Set up Gmail CLI authentication
