---
description: Delete a Gmail or Google Calendar snippet with user confirmation
---

# Delete Gmail/Calendar Snippet

Delete an existing snippet for Gmail or Google Calendar automation.

## Arguments

Input: `$ARGUMENTS`

## Instructions

1. **Parse the arguments**:
   - Check if `$ARGUMENTS` contains `-f` or `--force` flag
   - Extract the snippet type (mail/email or gcal/calendar)

2. **Determine which snippet to delete**:
   - If `$ARGUMENTS` mentions "mail", "email", "gmail" → delete `mail.md`
   - If `$ARGUMENTS` mentions "gcal", "calendar", "google calendar" → delete `gcal.md`
   - If unclear, ask the user which snippet to delete

3. **Check if snippet exists**:
   - Read `~/.claude/snippets/snippets/mail.md` or `~/.claude/snippets/snippets/gcal.md`
   - If it doesn't exist, inform user and exit

4. **Show snippet content and ask for confirmation** (UNLESS `-f` or `--force` flag is present):
   - Display the current snippet content
   - Ask: "Are you sure you want to delete this snippet? This action cannot be undone. (yes/no)"
   - Wait for user response
   - If no, abort
   - If yes, proceed

5. **Create backup**:
   - Copy the file to `~/.claude/snippets/snippets/[name].md.deleted.[timestamp]`
   - Inform user about backup location

6. **Delete the snippet**:
   - Remove `~/.claude/snippets/snippets/[name].md`
   - Confirm deletion with the user

7. **Optionally update config**:
   - Ask if user wants to remove the mapping from `config.json`
   - If yes (and not forced), show the mapping and ask for confirmation
   - If yes confirmed, remove the mapping
   - If forced, remove the mapping without asking

8. **Confirm completion**:
   - Show what was deleted
   - Remind user about backup location
   - Suggest how to restore if needed

## Example Usage

```
/delete-snippet mail
/delete-snippet gcal --force
/delete-snippet -f calendar
```

## Notes

- Always create backup before deleting
- Always ask for confirmation unless `-f` or `--force` is provided
- Store backups with timestamp for recovery
- Provide clear instructions for restoration
- Consider offering to remove config mappings as well
