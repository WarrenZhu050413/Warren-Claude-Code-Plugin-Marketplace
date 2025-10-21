---
description: Reset all spending tracking data
---

# Reset Spending Data

Reset all spending tracking data (daily, weekly, and hourly). This operation is destructive and cannot be undone.

## Arguments

Input: `$ARGUMENTS`

## Instructions

1. **Parse arguments**:
   - Check if `--confirm` or `-f` flag is present in `$ARGUMENTS`

2. **Ask for confirmation** (UNLESS `--confirm` or `-f` flag is present):
   - Warn user: "⚠️  This will delete ALL spending tracking data (daily, weekly, and hourly). This cannot be undone."
   - Show affected files:
     - `${CLAUDE_PLUGIN_ROOT}/spending_data/daily.json`
     - `${CLAUDE_PLUGIN_ROOT}/spending_data/weekly.json`
     - `${CLAUDE_PLUGIN_ROOT}/spending_data/hourly.json`
     - `${CLAUDE_PLUGIN_ROOT}/spending_data/session_state.json`
   - Ask: "Are you sure you want to proceed? (yes/no)"
   - If user responds "no" or anything other than "yes", abort
   - If user responds "yes", proceed

3. **Execute reset**:
   - Run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/track_spending.py --data-dir ${CLAUDE_PLUGIN_ROOT}/spending_data reset --confirm`
   - Display success message

## Example Usage

```
/spending-reset
/spending-reset --confirm
/spending-reset -f
```

## Notes

- ALWAYS ask for confirmation unless `--confirm` or `-f` is provided
- This operation is irreversible
- Session state will also be cleared
