---
description: Get current spending totals (daily and hourly)
---

# Get Spending Totals

Display current spending totals for today and the current hour.

## Instructions

1. **Execute command**:
   - Run: `python3 ~/.claude/track_spending.py get --format text`
   - Display the daily and hourly spending totals

2. **Format output**:
   - Show daily total with date
   - Show hourly total with time period
   - Use clear formatting for easy reading

## Example Output

```
Daily: $5.25
Hourly: $1.32
```

## Notes

- No confirmation needed (read-only operation)
- Data is read from `~/.claude/spending_data/`
