# Tracking Code Extraction Summary

## What Was Extracted

### 1. Session-Based Tracking (Lines 83-104 of original)

**Original code:**
```bash
# Track spending in global tracker with session-based delta tracking
spending_update=""
if (($(echo "$cost_dollars > 0" | bc -l))); then
    # Extract session ID from transcript path (filename without extension)
    session_id="unknown"
    if [ -n "$transcript_path" ] && [ "$transcript_path" != "null" ]; then
        transcript_name=$(basename "$transcript_path")
        session_id="${transcript_name%.jsonl}"
    fi

    # Use add-session for delta-based tracking (only adds new spending)
    add_result=$(python3 ~/.claude/track_spending.py add-session --session-id "$session_id" --cost "$cost_dollars" 2>/dev/null || echo '{}')
    delta_added=$(echo "$add_result" | jq -r '.delta_added // empty' 2>/dev/null)

    # Only show update message if we actually added new spending
    if [ -n "$delta_added" ] && [ "$delta_added" != "0" ] && [ "$delta_added" != "0.0" ]; then
        delta_display=$(printf "\$%.4f" "$delta_added")
        spending_update=$(printf "💰 Added %b%s%b to spending tracker" "\033[96m" "$delta_display" "\033[0m")
    fi
fi
```

**Updated code (in example):**
```bash
# SPENDING TRACKER INTEGRATION
spending_update=""
if (($(echo "$cost_dollars > 0" | bc -l))); then
    session_id="unknown"
    if [ -n "$transcript_path" ] && [ "$transcript_path" != "null" ]; then
        transcript_name=$(basename "$transcript_path")
        session_id="${transcript_name%.jsonl}"
    fi

    # Call plugin script with --data-dir pointing to plugin directory
    PLUGIN_DATA_DIR="$HOME/.claude/plugins/spending-tracker/spending_data"
    add_result=$(python3 ~/.claude/plugins/spending-tracker/scripts/track_spending.py \
        add-session \
        --data-dir "$PLUGIN_DATA_DIR" \
        --session-id "$session_id" \
        --cost "$cost_dollars" \
        2>/dev/null || echo '{}')

    delta_added=$(echo "$add_result" | jq -r '.delta_added // empty' 2>/dev/null)

    if [ -n "$delta_added" ] && [ "$delta_added" != "0" ] && [ "$delta_added" != "0.0" ]; then
        delta_display=$(printf "\$%.4f" "$delta_added")
        spending_update=$(printf "💰 Added %b%s%b to spending tracker" "\033[96m" "$delta_display" "\033[0m")
    fi
fi
```

**Key changes:**
- ✅ Added `PLUGIN_DATA_DIR` variable pointing to plugin directory
- ✅ Added `--data-dir "$PLUGIN_DATA_DIR"` argument to track_spending.py call
- ✅ Changed script path from `~/.claude/track_spending.py` to `~/.claude/plugins/spending-tracker/scripts/track_spending.py`

### 2. Global Spending Totals Display (Lines 107-139 of original)

**Original code:**
```bash
# Get global spending totals
spending_totals=""
if command -v python3 >/dev/null 2>&1; then
    totals_json=$(python3 ~/.claude/track_spending.py get --format json 2>/dev/null || echo '{}')
    daily_total=$(echo "$totals_json" | jq -r '.daily_total // 0' 2>/dev/null || echo "0")
    hourly_total=$(echo "$totals_json" | jq -r '.hourly_total // 0' 2>/dev/null || echo "0")

    # Format daily total with color tiers
    if [ -n "$daily_total" ] && [ "$daily_total" != "0" ] && [ "$daily_total" != "null" ]; then
        # Determine daily color tier
        if (($(echo "$daily_total >= 20.00" | bc -l 2>/dev/null || echo 0))); then
            daily_color="\033[1;91m"  # Bold Red - high spending
        elif (($(echo "$daily_total >= 5.00" | bc -l 2>/dev/null || echo 0))); then
            daily_color="\033[93m"    # Yellow - moderate spending
        else
            daily_color="\033[92m"    # Green - low spending
        fi
        daily_display=$(printf "\$%.2f" "$daily_total")
        spending_totals=$(printf " | 📅 %b%s%b/day" "${daily_color}" "${daily_display}" "\033[0m")
    fi

    # Format hourly total with color tiers
    if [ -n "$hourly_total" ] && [ "$hourly_total" != "0" ] && [ "$hourly_total" != "null" ]; then
        # Determine hourly color tier
        if (($(echo "$hourly_total >= 10.00" | bc -l 2>/dev/null || echo 0))); then
            hourly_color="\033[1;91m"  # Bold Red - very high rate
        elif (($(echo "$hourly_total >= 2.00" | bc -l 2>/dev/null || echo 0))); then
            hourly_color="\033[93m"    # Yellow - moderate rate
        else
            hourly_color="\033[92m"    # Green - low rate
        fi
        hourly_display=$(printf "\$%.2f" "$hourly_total")
        spending_totals="${spending_totals}$(printf " | ⏰ %b%s%b/hr" "${hourly_color}" "${hourly_display}" "\033[0m")"
    fi
fi
```

**Updated code (in example):**
```bash
# GET GLOBAL SPENDING TOTALS (for display)
spending_totals=""
if command -v python3 >/dev/null 2>&1; then
    PLUGIN_DATA_DIR="$HOME/.claude/plugins/spending-tracker/spending_data"
    totals_json=$(python3 ~/.claude/plugins/spending-tracker/scripts/track_spending.py \
        get \
        --data-dir "$PLUGIN_DATA_DIR" \
        --format json \
        2>/dev/null || echo '{}')

    daily_total=$(echo "$totals_json" | jq -r '.daily_total // 0' 2>/dev/null || echo "0")
    hourly_total=$(echo "$totals_json" | jq -r '.hourly_total // 0' 2>/dev/null || echo "0")

    # [Same color tier logic and formatting as original]
fi
```

**Key changes:**
- ✅ Added `PLUGIN_DATA_DIR` variable
- ✅ Added `--data-dir "$PLUGIN_DATA_DIR"` argument
- ✅ Changed script path to plugin location
- ✅ Kept all formatting logic identical

## Summary

### Files Created

1. **`examples/statusline-command-example.sh`**
   - Complete working statusline based on your current setup
   - Uses plugin directory for data storage
   - Includes all your existing features (git, cost tiers, output style, etc.)
   - Clearly marked spending tracker integration sections

### What Stays the Same

✅ All git branch display logic
✅ All cost display formatting (emoji tiers, color gradients)
✅ All spending totals formatting (daily/hourly with color tiers)
✅ Output style display
✅ Transcript path display

### What Changes

🔄 Script path: `~/.claude/track_spending.py` → `~/.claude/plugins/spending-tracker/scripts/track_spending.py`
🔄 Data location: `~/.claude/spending_data/` → `~/.claude/plugins/spending-tracker/spending_data/`
🔄 Added: `--data-dir` argument to all Python script calls

### How to Use

1. **Copy the example to your home directory:**
   ```bash
   cp ~/.claude/plugins/spending-tracker/examples/statusline-command-example.sh ~/.claude/my-statusline.sh
   chmod +x ~/.claude/my-statusline.sh
   ```

2. **Update your settings.json:**
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "bash ~/.claude/my-statusline.sh"
     }
   }
   ```

3. **Restart Claude Code**

4. **Verify tracking works:**
   ```bash
   /spending-stats
   ```

### Data Location

All spending data will be stored in:
```
~/.claude/plugins/spending-tracker/spending_data/
├── daily.json
├── hourly.json
└── session_state.json
```

This keeps everything self-contained within the plugin directory.
