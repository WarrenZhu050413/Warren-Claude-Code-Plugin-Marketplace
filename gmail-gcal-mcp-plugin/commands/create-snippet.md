---
description: Create a new Gmail or Google Calendar snippet with user confirmation
---

# Create Gmail/Calendar Snippet

Create a new snippet for Gmail or Google Calendar automation.

## Arguments

Input: `$ARGUMENTS`

## Instructions

1. **Parse the arguments**:
   - Check if `$ARGUMENTS` contains `-f` or `--force` flag
   - Extract the snippet type (mail/email or gcal/calendar)
   - Extract any snippet content or instructions

2. **Determine snippet type**:
   - If `$ARGUMENTS` mentions "mail", "email", "gmail" → create `mail.md`
   - If `$ARGUMENTS` mentions "gcal", "calendar", "google calendar" → create `gcal.md`
   - If unclear, ask the user which type to create

3. **Check if snippet already exists**:
   - Read `~/.claude/snippets/snippets/mail.md` or `~/.claude/snippets/snippets/gcal.md`
   - If it exists, warn the user and suggest using update command instead

4. **Create snippet content**:
   - Based on `$ARGUMENTS`, draft the snippet content
   - Follow the format:
     ```markdown
     <email> or <google_calendar>

     **VERIFICATION_HASH:** `[generate random hash]`

     [Content based on user's requirements]
     </email> or </google_calendar>
     ```

5. **Ask for confirmation** (UNLESS `-f` or `--force` flag is present):
   - Show the user the proposed snippet content
   - Ask: "Create this snippet? (yes/no)"
   - Wait for user response
   - If no, abort
   - If yes, proceed

6. **Create the snippet**:
   - Write to `~/.claude/snippets/snippets/[mail|gcal].md`
   - Confirm creation with the user

7. **Update config if needed**:
   - Check if `~/.claude/snippets/config.json` has the mapping
   - If not, add the appropriate mapping
   - Ask for confirmation before updating config (unless forced)

## Example Usage

```
/create-snippet mail with rules for drafting professional emails
/create-snippet gcal --force with timezone PST
/create-snippet -f calendar add default meeting duration 30 mins
```

## Notes

- Always ask for confirmation unless `-f` or `--force` is provided
- Generate unique VERIFICATION_HASH for each snippet
- Backup existing files before any modifications
