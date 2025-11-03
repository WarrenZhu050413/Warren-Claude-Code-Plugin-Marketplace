# Email Groups Guide

Email groups let you send to multiple addresses using `#groupname`.

## Quick Commands

```bash
gmail groups list                                  # List all groups
gmail groups show team                             # View group details
gmail groups create team --emails user@example.com # Create group
gmail groups add team user@example.com             # Add member
gmail groups remove team user@example.com          # Remove member
gmail groups delete team                           # Delete group
gmail groups validate                              # Check all groups
```

## Using Groups

### Send to Group

```bash
gmail send --to #team --subject "Meeting" --body "Tomorrow at 10am"
```

Expands to all members in `team` group.

### Multiple Groups

```bash
gmail send --to #team #family --subject "Update"
```

### Mix Groups and Emails

```bash
gmail send --to #team alice@example.com --subject "Update"
```

### CC/BCC Groups

```bash
gmail send --to alice@example.com --cc #team --subject "FYI"
gmail send --to alice@example.com --bcc #team --subject "Announcement"
```

## Commands

### list

List all groups with member counts.

```bash
gmail groups list
gmail groups list --output-format json
```

Output shows:
- Group name
- Member count
- First 2 emails (preview)

### show

View all members in a group.

```bash
gmail groups show team
```

### create

Create new group.

```bash
# From CLI
gmail groups create team --emails alice@example.com bob@example.com

# From JSON file
gmail groups create team --json-input-path team.json --force

# Get JSON schema
gmail groups schema
```

**Options:**
- `--emails` - Space-separated email list
- `--json-input-path` - Path to JSON file
- `--force` - Skip confirmation

**JSON format:**
```json
{
  "name": "team",
  "emails": [
    "alice@example.com",
    "bob@example.com"
  ]
}
```

**Validation:**
- Group name: alphanumeric, hyphens, underscores
- Valid email format
- No duplicates
- Unique group name

### add

Add member to group.

```bash
gmail groups add team charlie@example.com
```

Checks:
- Valid email format
- Not already in group

### remove

Remove member from group.

```bash
gmail groups remove team alice@example.com
gmail groups remove team alice@example.com --force  # Skip confirmation
```

### delete

Delete group. Creates backup before deletion.

```bash
gmail groups delete team
gmail groups delete team --force  # Skip confirmation
```

Backup saved to:
```
~/.gmaillm/email-groups.json.backup.YYYYMMDD_HHMMSS
```

### validate

Check groups for errors.

```bash
# Validate specific group
gmail groups validate team

# Validate all groups
gmail groups validate
```

Checks:
- Valid email format
- No duplicates
- Valid group names
- Well-formed JSON

### schema

Show JSON schema for programmatic creation.

```bash
gmail groups schema
```

## Group File Format

Groups stored in `~/.gmaillm/email-groups.json`:

```json
{
  "team": [
    "alice@example.com",
    "bob@example.com"
  ],
  "family": [
    "mom@example.com",
    "dad@example.com"
  ]
}
```

**Structure:**
- Group names as keys
- Email arrays as values
- Names: letters, numbers, hyphens, underscores
- Emails: valid format

## Validation Rules

### Group Names

**Valid:**
- `team`
- `project-alpha`
- `team_2024`
- `dev123`

**Invalid:**
- `#team` (no # prefix)
- `team name` (no spaces)
- `team@project` (no @)
- `team.group` (no dots)

### Email Addresses

**Valid:**
- `user@example.com`
- `first.last@company.org`
- `user+tag@domain.co.uk`

**Invalid:**
- `user` (missing domain)
- `@example.com` (missing local part)
- `user@` (missing domain)

### Duplicates

Within group (not allowed):
```json
{
  "team": [
    "alice@example.com",
    "alice@example.com"  // Error
  ]
}
```

Across groups (allowed):
```json
{
  "team": ["alice@example.com"],
  "family": ["alice@example.com"]  // OK
}
```

## Examples

### Project Team

```bash
# Create
gmail groups create alpha-team --emails \
  lead@company.com \
  dev1@company.com \
  qa@company.com

# Use
gmail send --to #alpha-team \
  --subject "Sprint Complete" \
  --body "Ready for review"
```

### Family Groups

```bash
# Create two groups
gmail groups create family-east --emails mom@ex.com dad@ex.com
gmail groups create family-west --emails uncle@ex.com aunt@ex.com

# Send to both
gmail send --to #family-east #family-west \
  --subject "Holiday Plans"
```

### Stakeholders

```bash
# Create
gmail groups create stakeholders --emails \
  ceo@company.com \
  cto@company.com \
  product-lead@company.com

# Weekly update
gmail send --to #stakeholders \
  --subject "Week 42 Update" \
  --attachments report.pdf
```

## Tips

### Use Descriptive Names

```bash
# Good
gmail groups create marketing-team
gmail groups create q1-2024-project

# Not ideal
gmail groups create group1
gmail groups create temp
```

### Keep Groups Focused

Create specific groups instead of one large group.

```bash
# Good
gmail groups create backend-team --emails ...
gmail groups create frontend-team --emails ...

# Not ideal
gmail groups create everyone --emails ...
```

### Regular Validation

```bash
gmail groups validate
```

### Backup Before Changes

Groups file auto-backs up on delete. Manual backup:

```bash
cp ~/.gmaillm/email-groups.json ~/.gmaillm/email-groups.json.backup.$(date +%Y%m%d)
```

## Troubleshooting

### "Group not found"

```bash
# List available
gmail groups list

# Create it
gmail groups create groupname --emails user@example.com
```

### "Invalid email format"

Check for:
- @ symbol present
- Domain part exists
- No spaces or invalid characters

### "Duplicate email in group"

```bash
# Edit file directly
nano ~/.gmaillm/email-groups.json

# Or recreate
gmail groups delete groupname --force
gmail groups create groupname --emails unique@list.com
```

### "JSON file is corrupted"

```bash
# Validate JSON
cat ~/.gmaillm/email-groups.json | python -m json.tool

# Restore from backup
ls -la ~/.gmaillm/email-groups.json.backup.*
cp ~/.gmaillm/email-groups.json.backup.TIMESTAMP ~/.gmaillm/email-groups.json
```

## Programmatic Usage

### Automation

```bash
# Create groups.json
cat > groups.json <<EOF
{
  "name": "automation-team",
  "emails": [
    "bot@example.com",
    "admin@example.com"
  ]
}
EOF

# Create from JSON
gmail groups create --json-input-path groups.json --force
```

### Batch Operations

```bash
#!/bin/bash
gmail groups create team1 --emails user1@ex.com user2@ex.com --force
gmail groups create team2 --emails user3@ex.com user4@ex.com --force
```

### Export/Import

```bash
# Export
cp ~/.gmaillm/email-groups.json ~/backup/

# Import
cp ~/backup/email-groups.json ~/.gmaillm/
gmail groups validate
```

## File Location

```
~/.gmaillm/email-groups.json              # Main file
~/.gmaillm/email-groups.json.backup.*     # Backups
```
