---
description: Read Gmail and Google Calendar snippets
---

# Read Gmail/Calendar Snippets

Read and display the current Gmail and/or Google Calendar snippets.

## Arguments

Input: `$ARGUMENTS`

## Instructions

1. **Parse the arguments**:
   - If `$ARGUMENTS` is empty or contains "all", read ALL snippets
   - If `$ARGUMENTS` mentions "mail", "email", "gmail" → read only `mail.md`
   - If `$ARGUMENTS` mentions "gcal", "calendar", "google calendar" → read only `gcal.md`
   - Can specify multiple types to read both

2. **Default behavior (no arguments)**:
   - Read BOTH `mail.md` and `gcal.md`
   - Display all snippets with clear labels

3. **Read the specified snippets**:
   - For each snippet to read:
     - Check if file exists at `~/.claude/snippets/snippets/[name].md`
     - If exists, read the content
     - If doesn't exist, note that it's not found

4. **Display the content**:
   - For each snippet found:
     - Show a clear header: `=== [Snippet Name] ===`
     - Display the full content
     - Show the file path
     - Show last modified date
     - Extract and highlight key information:
       - VERIFICATION_HASH
       - Main rules/instructions
       - Any custom configurations

5. **Format the output**:
   - Use clear separators between snippets
   - Highlight important sections
   - Make it easy to scan and understand
   - Example format:
     ```
     === Gmail Snippet (mail.md) ===
     Path: ~/.claude/snippets/snippets/mail.md
     Last modified: 2025-10-10 11:30
     Hash: f0b2983e961b49a0

     Content:
     [full content here]

     Key Rules:
     - Rule 1
     - Rule 2

     =====================================
     ```

6. **Summary**:
   - Show count of snippets found
   - List any snippets that were requested but not found
   - Suggest commands to create missing snippets

## Example Usage

```
/read-snippets
/read-snippets mail
/read-snippets gcal
/read-snippets email calendar
/read-snippets all
```

## Notes

- No confirmation needed for read operations
- Default to reading ALL snippets if no arguments
- Filter to specific snippets based on `$ARGUMENTS`
- Display clear, formatted output
- Provide context about what's being shown
