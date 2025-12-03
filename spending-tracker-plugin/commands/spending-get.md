---
description: Get current spending totals (daily, weekly, and hourly)
---

# Get Spending Totals

Display current spending totals for today, this week, and the current hour.

## Instructions

1. **Execute command**:
   - Run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/track_spending.py --data-dir ${CLAUDE_PLUGIN_ROOT}/spending_data get --format text`
   - Display the daily, weekly, and hourly spending totals

2. **Format output**:
   - Show daily total with date
   - Show weekly total with week number
   - Show hourly total with time period
   - Use clear formatting for easy reading

## Example Output

```
Daily: $5.25
Weekly: $32.40
Hourly: $1.32
```

## Notes

- No confirmation needed (read-only operation)
- Data is read from `${CLAUDE_PLUGIN_ROOT}/spending_data/`
