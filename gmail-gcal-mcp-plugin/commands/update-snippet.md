---
description: Update an existing Gmail or Google Calendar snippet with user confirmation
---

# Update Gmail/Calendar Snippet

Update an existing snippet for Gmail or Google Calendar automation.

## Arguments

Input: `$ARGUMENTS`

## Instructions

1. **Parse the arguments**:
   - Check if `$ARGUMENTS` contains `-f` or `--force` flag
   - Extract the snippet type (mail/email or gcal/calendar)
   - Extract the update instructions or new content

2. **Determine which snippet to update**:
   - If `$ARGUMENTS` mentions "mail", "email", "gmail" → update `mail.md`
   - If `$ARGUMENTS` mentions "gcal", "calendar", "google calendar" → update `gcal.md`
   - If unclear, ask the user which snippet to update

3. **Read existing snippet**:
   - Read `~/.claude/snippets/snippets/mail.md` or `~/.claude/snippets/snippets/gcal.md`
   - If it doesn't exist, inform user and suggest using create command instead

4. **Prepare the update**:
   - Based on `$ARGUMENTS`, determine what changes to make:
     - If specific content provided, incorporate it
     - If adding rules, append them
     - If replacing content, prepare new version
   - Preserve the VERIFICATION_HASH or generate new one if major changes

5. **Show diff and ask for confirmation** (UNLESS `-f` or `--force` flag is present):
   - Display the current version
   - Display the proposed new version
   - Highlight the changes
   - Ask: "Apply these changes? (yes/no)"
   - Wait for user response
   - If no, abort
   - If yes, proceed

6. **Apply the update**:
   - Backup the original file: `~/.claude/snippets/snippets/[name].md.backup.[timestamp]`
   - Write the updated content
   - Confirm update with the user

7. **Verify the update**:
   - Show the final content
   - Confirm the snippet is properly formatted

## Example Usage

```
/update-snippet mail add signature with my title
/update-snippet gcal --force set default reminder to 15 minutes
/update-snippet -f email change drafting style to casual
```

## Notes

- Always create backup before modifying
- Always ask for confirmation unless `-f` or `--force` is provided
- Preserve structure and VERIFICATION_HASH unless major rewrite
- Show clear before/after comparison
