# Email Groups Guide

Complete guide for managing email distribution groups in gmaillm.

## Overview

Email groups allow you to create reusable lists of email addresses. Instead of typing multiple addresses, reference a group with `#groupname`.

**Benefits:**
- **Save time** - Type `#team` instead of 5 email addresses
- **Reduce errors** - Define addresses once, use everywhere
- **Easy updates** - Add/remove members in one place
- **Organization** - Group by project, team, or context

## Quick Start

### List All Groups

```bash
gmail groups list
```

Shows all groups with member counts.

### Create a Group

```bash
# Create with CLI arguments
gmail groups create team --emails alice@example.com bob@example.com charlie@example.com

# Create interactively (will prompt for emails)
gmail groups create team
```

### View Group Details

```bash
gmail groups show team
```

Shows all members in the group.

### Add Member to Group

```bash
gmail groups add team david@example.com
```

### Remove Member from Group

```bash
gmail groups remove team alice@example.com
```

### Use in Email

```bash
# Send to entire group
gmail send --to #team --subject "Meeting" --body "Tomorrow at 10am"

# Mix groups and individual emails
gmail send --to #team bob@example.com --subject "Update" --body "Progress report"

# CC groups
gmail send --to alice@example.com --cc #team --subject "FYI" --body "For your information"
```

### Delete a Group

```bash
gmail groups delete team
```

### Validate Groups

```bash
# Validate single group
gmail groups validate team

# Validate all groups
gmail groups validate
```

## Commands

### `gmail groups list`

List all email distribution groups.

**Usage:**
```bash
gmail groups list
gmail groups list --output-format json
```

**Output:**
```
Email Distribution Groups
┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Group   ┃ Members ┃ Emails                           ┃
┡━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ #team   │       3 │ alice@ex.com, bob@ex.com, ...    │
│ #family │       5 │ mom@ex.com, dad@ex.com, ...      │
└─────────┴─────────┴──────────────────────────────────┘

Total: 2 group(s)

Usage: gmail send --to #groupname --subject "..." --body "..."
```

### `gmail groups show <name>`

Show detailed information about a specific group.

**Usage:**
```bash
gmail groups show team
```

**Output:**
```
Group Details: #team
─────────────────────────

Members (3):
  • alice@example.com
  • bob@example.com
  • charlie@example.com
```

### `gmail groups create <name>`

Create a new email distribution group.

**Usage:**
```bash
# From CLI arguments
gmail groups create team --emails alice@example.com bob@example.com

# From JSON file
gmail groups create team --json-input-path team.json --force

# Get JSON schema
gmail groups schema
```

**Options:**
- `--emails` - Space-separated list of email addresses
- `--json-input-path` - Path to JSON file with group definition
- `--force` - Skip confirmation prompt

**JSON Format:**
```json
{
  "name": "team",
  "emails": [
    "alice@example.com",
    "bob@example.com",
    "charlie@example.com"
  ]
}
```

**Validation:**
- Group name must be alphanumeric (plus hyphens/underscores)
- All emails must be valid format
- No duplicate emails within group
- Group name must be unique

### `gmail groups add <group> <email>`

Add a member to an existing group.

**Usage:**
```bash
gmail groups add team david@example.com
```

**Validation:**
- Email must be valid format
- Email must not already be in group

### `gmail groups remove <group> <email>`

Remove a member from a group.

**Usage:**
```bash
gmail groups remove team alice@example.com
```

**Confirmation:**
- Prompts for confirmation (use `--force` to skip)

### `gmail groups delete <name>`

Delete an email distribution group.

**Usage:**
```bash
# With confirmation
gmail groups delete team

# Skip confirmation
gmail groups delete team --force
```

**Backup:**
Creates timestamped backup before deletion at:
```
~/.gmaillm/email-groups.json.backup.YYYYMMDD_HHMMSS
```

### `gmail groups validate [name]`

Validate group(s) for email format and duplicates.

**Usage:**
```bash
# Validate specific group
gmail groups validate team

# Validate all groups
gmail groups validate
```

**Checks:**
- All emails have valid format
- No duplicate emails within groups
- Group names are valid
- JSON file is well-formed

**Output:**
```
Validating Groups
─────────────────

✓ team - Valid (3 members)
✗ family - Invalid: Duplicate email mom@example.com
✓ project - Valid (5 members)

Summary: 2 valid, 1 invalid out of 3 groups
```

### `gmail groups schema`

Display JSON schema for programmatic group creation.

**Usage:**
```bash
gmail groups schema
```

Shows complete JSON schema with validation rules.

## Group File Format

Groups are stored in `~/.gmaillm/email-groups.json`:

```json
{
  "team": [
    "alice@example.com",
    "bob@example.com",
    "charlie@example.com"
  ],
  "family": [
    "mom@example.com",
    "dad@example.com"
  ],
  "project-alpha": [
    "lead@example.com",
    "dev1@example.com",
    "dev2@example.com"
  ]
}
```

**Structure:**
- Top-level object with group names as keys
- Each value is an array of email addresses
- Group names can contain letters, numbers, hyphens, underscores
- Email addresses must be valid format

## Using Groups in Commands

### Send Email to Group

```bash
gmail send --to #team --subject "Meeting Tomorrow" --body "10am in conference room"
```

Expands to all members of `team` group.

### Multiple Groups

```bash
gmail send --to #team #family --subject "Party Invitation" --body "Saturday at 7pm"
```

### Mix Groups and Emails

```bash
gmail send --to #team alice@example.com --subject "Update" --body "Latest changes"
```

### CC/BCC Groups

```bash
# CC a group
gmail send --to alice@example.com --cc #team --subject "FYI" --body "..."

# BCC a group
gmail send --to alice@example.com --bcc #team --subject "Announcement" --body "..."
```

### Reply with Groups

```bash
gmail reply <message_id> --body "Thanks!" --cc #team
```

## Validation Rules

### Group Names

**Valid:**
- `team` - Simple name
- `project-alpha` - With hyphen
- `team_2024` - With underscore
- `dev123` - With numbers

**Invalid:**
- `#team` - No # prefix
- `team name` - No spaces
- `team@project` - No @ symbol
- `team.group` - No dots

### Email Addresses

**Valid:**
- `user@example.com`
- `first.last@company.org`
- `user+tag@domain.co.uk`

**Invalid:**
- `user` - Missing domain
- `@example.com` - Missing local part
- `user@` - Missing domain
- `not-an-email` - Invalid format

### Duplicate Detection

Within a group:
```json
{
  "team": [
    "alice@example.com",
    "alice@example.com"  // ✗ Duplicate
  ]
}
```

Across groups (allowed):
```json
{
  "team": ["alice@example.com"],
  "family": ["alice@example.com"]  // ✓ OK - different groups
}
```

## Best Practices

### 1. Use Descriptive Names

```bash
# Good
gmail groups create marketing-team
gmail groups create q1-2024-project
gmail groups create family-east-coast

# Not ideal
gmail groups create group1
gmail groups create temp
gmail groups create test
```

### 2. Keep Groups Focused

Create specific groups rather than one large group:

```bash
# Good - Specific groups
gmail groups create backend-team --emails ...
gmail groups create frontend-team --emails ...
gmail groups create design-team --emails ...

# Not ideal - One big group
gmail groups create everyone --emails ...
```

### 3. Regular Validation

Validate groups periodically to catch errors:

```bash
gmail groups validate
```

### 4. Document Groups

Add comments in your notes about what each group represents:

```
Groups:
- #team: Core development team
- #stakeholders: Project stakeholders for updates
- #family: Family members for personal emails
```

### 5. Backup Before Changes

Groups file is automatically backed up on delete operations, but you can manually backup:

```bash
cp ~/.gmaillm/email-groups.json ~/.gmaillm/email-groups.json.backup.$(date +%Y%m%d)
```

## Troubleshooting

### "Group not found"

**Problem:** Trying to use a group that doesn't exist.

**Solution:**
```bash
# List available groups
gmail groups list

# Create the group
gmail groups create groupname --emails user@example.com
```

### "Invalid email format"

**Problem:** Email address doesn't match valid format.

**Solution:** Check email address for typos:
- Must have @ symbol
- Must have domain part
- No spaces or invalid characters

### "Duplicate email in group"

**Problem:** Same email appears twice in a group.

**Solution:**
```bash
# Edit the file directly
nano ~/.gmaillm/email-groups.json

# Or recreate the group
gmail groups delete groupname --force
gmail groups create groupname --emails unique@list.com
```

### "JSON file is corrupted"

**Problem:** Groups file has invalid JSON.

**Solution:**
```bash
# Validate JSON syntax
cat ~/.gmaillm/email-groups.json | python -m json.tool

# If corrupted, restore from backup
ls -la ~/.gmaillm/email-groups.json.backup.*
cp ~/.gmaillm/email-groups.json.backup.TIMESTAMP ~/.gmaillm/email-groups.json
```

## Advanced Usage

### Programmatic Group Management

Use JSON input for automation:

```bash
# Create groups.json
cat > groups.json <<EOF
{
  "name": "automation-team",
  "emails": [
    "bot@example.com",
    "admin@example.com",
    "monitor@example.com"
  ]
}
EOF

# Create group from JSON
gmail groups create --json-input-path groups.json --force
```

### Batch Operations

Create multiple groups with a script:

```bash
#!/bin/bash
gmail groups create team1 --emails user1@ex.com user2@ex.com --force
gmail groups create team2 --emails user3@ex.com user4@ex.com --force
gmail groups create team3 --emails user5@ex.com user6@ex.com --force
```

### Export/Import Groups

Export groups:
```bash
cp ~/.gmaillm/email-groups.json ~/backup/email-groups.json
```

Import groups:
```bash
cp ~/backup/email-groups.json ~/.gmaillm/email-groups.json
gmail groups validate  # Verify after import
```

## File Location

Groups file:
```
~/.gmaillm/email-groups.json
```

Backups (created on delete):
```
~/.gmaillm/email-groups.json.backup.20241028_143022
~/.gmaillm/email-groups.json.backup.20241027_091533
```

## Examples

### Example 1: Project Team

```bash
# Create project team
gmail groups create alpha-team --emails \
  lead@company.com \
  dev1@company.com \
  dev2@company.com \
  qa@company.com

# Send update
gmail send --to #alpha-team \
  --subject "Sprint 5 Complete" \
  --body "All tasks finished, ready for review"
```

### Example 2: Family Groups

```bash
# East coast family
gmail groups create family-east --emails mom@ex.com dad@ex.com sis@ex.com

# West coast family
gmail groups create family-west --emails uncle@ex.com aunt@ex.com cousin@ex.com

# Send to both
gmail send --to #family-east #family-west \
  --subject "Holiday Plans" \
  --body "Let's coordinate for Thanksgiving"
```

### Example 3: Stakeholder Updates

```bash
# Create stakeholder group
gmail groups create stakeholders --emails \
  ceo@company.com \
  cto@company.com \
  product-lead@company.com

# Weekly update
gmail send --to #stakeholders \
  --subject "Weekly Update - Week 42" \
  --body "Progress report attached" \
  --attachments report.pdf
```
