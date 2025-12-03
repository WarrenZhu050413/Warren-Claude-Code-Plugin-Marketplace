---
description: Show detailed spending statistics
---

# Spending Statistics

Display detailed statistics about your Claude Code API spending, including historical data and averages.

## Instructions

1. **Execute command**:
   - Run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/track_spending.py --data-dir ${CLAUDE_PLUGIN_ROOT}/spending_data stats`
   - Display the full statistics output

2. **Show information**:
   - Total days tracked
   - Total spending across all days
   - Average spending per day
   - Total hours tracked
   - Average spending per hour
   - Current day and hour totals

## Example Output

```
=== Spending Statistics ===

Daily Tracking:
  Total days tracked: 15
  Total across all days: $123.45
  Average per day: $8.23

Hourly Tracking:
  Total hours tracked: 89
  Total across all hours: $123.45
  Average per hour: $1.39

Current Period:
  Today (2025-10-10): $12.34
  This hour (2025-10-10T12:00): $2.45
```

## Notes

- No confirmation needed (read-only operation)
- Historical data is kept for 30 days by default
