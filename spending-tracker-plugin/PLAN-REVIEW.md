co# Plan Review: Plugin-Directory Data Storage

## Current Architecture Issues

**Problem 1: Data stored outside plugin**
- Current: `~/.claude/spending_data/`
- Issue: Data persists after plugin uninstall
- Issue: Not self-contained

**Problem 2: Tight coupling**
- Script hardcodes data directory path (line 18)
- No way to override without editing code

## Proposed Architecture Changes

### 1. Data Storage Location

**New location:** `~/.claude/plugins/spending-tracker/spending_data/`

**Benefits:**
- ✅ Self-contained: Everything in plugin directory
- ✅ Clean uninstall: Remove plugin = remove data
- ✅ Clear ownership: Data belongs to plugin
- ✅ Multi-instance safe: Each plugin install has own data

### 2. Script Modifications

**Add `--data-dir` argument to `track_spending.py`:**

```python
# Configuration - allow override via environment or argument
DEFAULT_DATA_DIR = os.path.expanduser("~/.claude/spending_data")  # Backward compat
CONFIG = {
    "data_dir": os.getenv("SPENDING_TRACKER_DATA_DIR", DEFAULT_DATA_DIR),
    "retention_days": 30,
    "lock_timeout": 5,
    "decimal_places": 8,
    "enable_cleanup": True,
}

def main():
    parser = argparse.ArgumentParser(description='Track Claude Code API spending')

    # Global argument for all subcommands
    parser.add_argument('--data-dir', type=str,
                       help='Directory to store spending data (default: ~/.claude/spending_data)')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    # ... rest of subparsers

    args = parser.parse_args()

    # Override CONFIG if --data-dir provided
    if args.data_dir:
        CONFIG["data_dir"] = os.path.expanduser(args.data_dir)
```

**Benefits:**
- ✅ Backward compatible: Default still works
- ✅ Flexible: Can specify any directory
- ✅ Environment override: `SPENDING_TRACKER_DATA_DIR` env var

### 3. Helper Script Design

**Key responsibilities:**
1. **Auto-detect plugin directory** using `${BASH_SOURCE[0]}`
2. **Set data directory** to `$PLUGIN_DIR/spending_data`
3. **Call Python script** with `--data-dir` argument
4. **Provide display guidelines** (not display itself)

**Example helper script:**

```bash
#!/bin/bash
# Spending Tracker Helper for Claude Code Statusline

# Get plugin directory (works when sourced)
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRACK_SCRIPT="$PLUGIN_DIR/scripts/track_spending.py"
DATA_DIR="$PLUGIN_DIR/spending_data"

# Track spending silently (recommended - called by statusline)
# Usage: track_spending "$input_json"
track_spending() {
    local input="$1"

    # Extract cost and transcript path
    local cost_raw=$(echo "$input" | jq -r '.cost.total_cost_usd // empty' 2>/dev/null)
    local transcript_path=$(echo "$input" | jq -r '.transcript_path // empty' 2>/dev/null)

    # Only track if we have valid data
    if [ -z "$cost_raw" ] || [ "$cost_raw" = "null" ] || [ "$cost_raw" = "0" ]; then
        return 0
    fi

    # Extract session ID from transcript path
    local session_id="unknown"
    if [ -n "$transcript_path" ] && [ "$transcript_path" != "null" ]; then
        local transcript_name=$(basename "$transcript_path")
        session_id="${transcript_name%.jsonl}"
    fi

    # Track spending with plugin data directory
    python3 "$TRACK_SCRIPT" add-session \
        --data-dir "$DATA_DIR" \
        --session-id "$session_id" \
        --cost "$cost_raw" \
        2>/dev/null >/dev/null
}

# Get spending data for display (user implements their own display)
# Returns JSON with daily_total and hourly_total
# Usage: totals=$(get_spending_data)
get_spending_data() {
    python3 "$TRACK_SCRIPT" get \
        --data-dir "$DATA_DIR" \
        --format json \
        2>/dev/null || echo '{}'
}
```

### 4. User Integration Pattern

**In user's statusline script:**

```bash
#!/bin/bash
input=$(cat)

# Source plugin helper
source ~/.claude/plugins/spending-tracker/scripts/track-spending-helper.sh

# Track spending (silent - happens automatically)
track_spending "$input"

# Optional: Get data and display your way
totals=$(get_spending_data)
daily=$(echo "$totals" | jq -r '.daily_total // 0')

# User's custom statusline output
if [ "$daily" != "0" ]; then
    printf "📁 %s | 💰 $%.2f today" "$(basename "$dir")" "$daily"
else
    printf "📁 %s" "$(basename "$dir")"
fi
```

## Key Design Principles

### 1. Separation of Concerns
- **Plugin provides:** Tracking function + data access
- **User provides:** Display logic and formatting
- **Rationale:** Users have different statusline formats; plugin shouldn't dictate

### 2. Opinionated Tracking, Flexible Display
- **Tracking is automatic:** Just call `track_spending "$input"`
- **Display is optional:** Call `get_spending_data` if you want to show it
- **Rationale:** Some users want tracking without statusline clutter

### 3. Guidelines Over Implementation
- **Provide:** Example configurations showing how to display
- **Don't provide:** Built-in display function that users must use
- **Rationale:** Every user's statusline is different; examples are more useful

## Documentation Updates Needed

### 1. README.md

Add prominent section:

```markdown
## Dependencies

⚠️ **Important:** This plugin requires statusline integration for automatic tracking.

**Why?** Claude Code exposes cost data only through the statusline JSON input. The plugin provides a helper script that you integrate into your existing statusline command.

**Data Storage:** All spending data is stored in `~/.claude/plugins/spending-tracker/spending_data/` within the plugin directory.
```

### 2. Statusline Integration Section

```markdown
## Statusline Integration

### Quick Setup (Tracking Only)

Add to your statusline script (`~/.claude/my-statusline.sh`):

```bash
# Load spending tracker
source ~/.claude/plugins/spending-tracker/scripts/track-spending-helper.sh

# Track spending automatically (silent)
track_spending "$input"
```

That's it! Spending is now tracked. Use `/spending-stats` to view data.

### Adding Display (Optional)

If you want to show spending in your statusline:

```bash
# After tracking, get the data
totals=$(get_spending_data)
daily=$(echo "$totals" | jq -r '.daily_total // 0')
hourly=$(echo "$totals" | jq -r '.hourly_total // 0')

# Display however you like
if [ "$daily" != "0" ]; then
    printf "💰 Today: $%.2f" "$daily"
fi
```

### Example Configurations

See `examples/` directory for complete statusline examples:
- `statusline-minimal.sh` - Track only, no display
- `statusline-daily.sh` - Track + show daily total
- `statusline-full.sh` - Track + show daily + hourly
- `statusline-custom.sh` - Track + custom formatting
```

### 3. INSTALL.md

```markdown
## Post-Installation

After installing the plugin:

1. **Add to your statusline** (required for tracking):
   ```bash
   source ~/.claude/plugins/spending-tracker/scripts/track-spending-helper.sh
   track_spending "$input"
   ```

2. **Optional: Add display** (examples in `~/.claude/plugins/spending-tracker/examples/`)

3. **Verify tracking works:**
   - Have a conversation with Claude Code
   - Run `/spending-stats`
   - You should see tracked data

**Data location:** `~/.claude/plugins/spending-tracker/spending_data/`
```

## Migration Path for Existing Users

For users with existing data in `~/.claude/spending_data/`:

```bash
# Optional: Migrate existing data to plugin directory
mkdir -p ~/.claude/plugins/spending-tracker/spending_data
cp ~/.claude/spending_data/*.json ~/.claude/plugins/spending-tracker/spending_data/

# Remove old data (optional)
# rm -rf ~/.claude/spending_data
```

Or provide migration command:

```bash
/spending-migrate  # New slash command to migrate data
```

## File Structure

```
spending-tracker-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── spending-get.md
│   ├── spending-stats.md
│   └── spending-reset.md
├── scripts/
│   ├── track_spending.py          # Modified: accepts --data-dir
│   └── track-spending-helper.sh   # New: helper for statusline
├── examples/                       # New: example configurations
│   ├── statusline-minimal.sh      # Track only
│   ├── statusline-daily.sh        # Track + daily display
│   ├── statusline-full.sh         # Track + daily + hourly
│   └── statusline-custom.sh       # Track + custom format
├── spending_data/                  # New: data storage (gitignored)
│   ├── daily.json
│   ├── hourly.json
│   └── session_state.json
├── .gitignore                      # Add: spending_data/
├── README.md                       # Updated: new data location
├── INSTALL.md                      # New: installation guide
└── PLAN-statusline-integration.html
```

## Summary of Changes

### Code Changes
1. ✅ Modify `track_spending.py` to accept `--data-dir` argument
2. ✅ Create `track-spending-helper.sh` with auto-detection
3. ✅ Update `.gitignore` to exclude `spending_data/`

### Documentation Changes
1. ✅ Update README with data location and dependencies
2. ✅ Create INSTALL.md with setup steps
3. ✅ Create 4 example statusline configurations
4. ✅ Update slash command docs to reference new location

### Testing Required
1. Test `--data-dir` argument works correctly
2. Test helper script auto-detects plugin directory
3. Test examples work out-of-the-box
4. Test migration from old data location

## Review Decision

**Proceed with implementation?** This approach:
- ✅ Makes plugin self-contained
- ✅ Maintains backward compatibility
- ✅ Gives users full display control
- ✅ Follows plugin best practices
- ✅ Clear separation: tracking (plugin) vs display (user)

**Next step:** Implement the changes if approved.
