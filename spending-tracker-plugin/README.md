# Spending Tracker Plugin

Track your Claude Code API spending with daily and hourly breakdowns. This plugin provides slash commands to view statistics and manage your spending data.

## Features

- Track API spending per day and per hour
- View detailed statistics with averages
- Session-based delta tracking (only counts new spending)
- Thread-safe file operations with locking
- Automatic cleanup of old data (30-day retention)
- Integration with Claude Code statusline

## Installation

### From Marketplace

1. Add the marketplace:
   ```bash
   /plugin marketplace add warren-claude-code-plugin-marketplace
   ```

2. Install the plugin:
   ```bash
   /plugin install spending-tracker@warren-claude-code-plugin-marketplace
   ```

3. Restart Claude Code

### Manual Installation

1. Clone this repository
2. Copy the `spending-tracker-plugin` directory to `~/.claude/plugins/`
3. Restart Claude Code

## Available Commands

### `/spending-get`

Get current spending totals for today and the current hour.

```bash
/spending-get
```

Example output:
```
Daily: $5.25
Hourly: $1.32
```

### `/spending-stats`

Display detailed spending statistics including historical data and averages.

```bash
/spending-stats
```

Example output:
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

### `/spending-reset`

Reset all spending tracking data. This operation is destructive and requires confirmation.

```bash
/spending-reset              # Will ask for confirmation
/spending-reset --confirm    # Skip confirmation
/spending-reset -f           # Skip confirmation (short flag)
```

## Integration with Statusline

This plugin includes the `track_spending.py` script that can be integrated with your Claude Code statusline to automatically track spending and display it in the status bar.

### Setup Instructions

1. The script is located at: `~/.claude/plugins/spending-tracker/scripts/track_spending.py`

2. In your statusline script, you can call:
   ```bash
   # Track spending with session-based delta tracking
   python3 ~/.claude/plugins/spending-tracker/scripts/track_spending.py add-session \
     --session-id "$session_id" \
     --cost "$cost_dollars"

   # Get current totals
   python3 ~/.claude/plugins/spending-tracker/scripts/track_spending.py get --format json
   ```

3. See `statusline-command.sh` example in the repository for full integration

## Data Storage

Spending data is stored in `~/.claude/spending_data/`:

- `daily.json` - Daily spending totals
- `hourly.json` - Hourly spending totals
- `session_state.json` - Session tracking for delta calculations
- `.lock` files - Thread-safe file locking

## Configuration

The script includes configurable options (edit `scripts/track_spending.py`):

```python
CONFIG = {
    "data_dir": "~/.claude/spending_data",
    "retention_days": 30,          # Keep data for 30 days
    "lock_timeout": 5,             # Max 5 seconds to acquire lock
    "decimal_places": 8,           # Precision for cost tracking
    "enable_cleanup": True,        # Auto-cleanup old data
}
```

## How It Works

### Session-Based Delta Tracking

The tracker uses session-based delta tracking to avoid double-counting:

1. Each Claude Code session has a unique session ID
2. The tracker remembers the last known cost for each session
3. Only the delta (new spending) is added to daily/hourly totals
4. This prevents re-adding the same cost on multiple statusline updates

### Example Flow

```
Session starts: $0.00 → Track: $0.00 (delta: $0.00)
After message 1: $0.05 → Track: $0.05 (delta: $0.05)
After message 2: $0.12 → Track: $0.12 (delta: $0.07)
After message 3: $0.20 → Track: $0.20 (delta: $0.08)
Total tracked: $0.20 ✓
```

## CLI Usage

The underlying Python script can also be used directly:

```bash
# Add cost with session tracking (recommended)
python3 ~/.claude/plugins/spending-tracker/scripts/track_spending.py add-session \
  --session-id "unique-session-id" \
  --cost 5.25

# Get totals (JSON format)
python3 ~/.claude/plugins/spending-tracker/scripts/track_spending.py get --format json

# Get totals (text format)
python3 ~/.claude/plugins/spending-tracker/scripts/track_spending.py get --format text

# Show statistics
python3 ~/.claude/plugins/spending-tracker/scripts/track_spending.py stats

# Reset all data (requires --confirm)
python3 ~/.claude/plugins/spending-tracker/scripts/track_spending.py reset --confirm
```

## Troubleshooting

**Commands not appearing:**
- Run `/help` to verify installation
- Check that plugin is enabled in settings
- Restart Claude Code

**Data not tracking:**
- Verify data directory exists: `~/.claude/spending_data/`
- Check file permissions
- Review statusline integration

**Reset not working:**
- Always requires `--confirm` flag for safety
- Use `/spending-reset --confirm` to bypass confirmation prompt

## License

MIT License - Feel free to use and modify as needed.

## Author

Fucheng Warren Zhu (wzhu@college.harvard.edu)

## Contributing

Contributions welcome! Please submit issues and pull requests to the marketplace repository.

---

**Last Updated:** 2025-10-10
