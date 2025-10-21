#!/bin/bash

# Read JSON input from stdin
input=$(cat)

# Extract values from JSON
dir=$(echo "$input" | jq -r '.workspace.current_dir')
model=$(echo "$input" | jq -r '.model.display_name')
cost_raw=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')
output_style=$(echo "$input" | jq -r '.output_style.name // "default"')
transcript_path=$(echo "$input" | jq -r '.transcript_path // empty')
# Debug: Write JSON structure to a temp file for inspection (remove this line after debugging)
echo "$input" >/tmp/statusline_debug.json

# Get git information
git_branch=""
git_status=""
if [ -n "$dir" ]; then
	git_branch=$(cd "$dir" 2>/dev/null && git branch --show-current 2>/dev/null)
	if [ -n "$git_branch" ]; then
		git_status=$(cd "$dir" 2>/dev/null && git status --porcelain 2>/dev/null)
	fi
fi

# Format git info with lighter cyan colors
git_info=""
if [ -n "$git_branch" ]; then
	if [ -n "$git_status" ]; then
		git_info=$(printf " 🌿 %b%s*%b" "\033[96m" "$git_branch" "\033[0m") # Bright cyan for git with changes
	else
		git_info=$(printf " 🌿 %b%s%b" "\033[96m" "$git_branch" "\033[0m") # Bright cyan for git
	fi
fi

# Format cost with luxury tiers
cost_info=""
if [ -n "$cost_raw" ] && [ "$cost_raw" != "null" ]; then
	# Cost is already in dollars, just format it properly
	cost_dollars=$(echo "$cost_raw" | awk '{printf "%.8f", $1}')

	# Determine luxury tier with GREEN TO RED gradient (money heat map)
	if (($(echo "$cost_dollars <= 0.10" | bc -l))); then
		# Tier 1: Minimal spending (Green)
		emoji="🪙"
		color="\033[92m" # Bright Green (coolest)
	elif (($(echo "$cost_dollars <= 1.00" | bc -l))); then
		# Tier 2: Light spending (Bold Green)
		emoji="💵"
		color="\033[1;92m" # Bold Bright Green
	elif (($(echo "$cost_dollars <= 5.00" | bc -l))); then
		# Tier 3: Moderate spending (Yellow)
		emoji="💳"
		color="\033[93m" # Bright Yellow (warming)
	elif (($(echo "$cost_dollars <= 20.00" | bc -l))); then
		# Tier 4: Premium spending (Bold Yellow)
		emoji="✨"
		color="\033[1;93m" # Bold Bright Yellow
	elif (($(echo "$cost_dollars <= 100.00" | bc -l))); then
		# Tier 5: Luxury spending (Red)
		emoji="🎉"
		color="\033[91m" # Bright Red (getting hot)
	elif (($(echo "$cost_dollars <= 500.00" | bc -l))); then
		# Tier 6: Ultra-luxury spending (Bold Red)
		emoji="🎆"
		color="\033[1;91m" # Bold Bright Red
	else
		# Tier 7: Ultimate luxury spending (Bold Red - maximum)
		emoji="💎"
		color="\033[1;91m" # Bold Bright Red (maximum heat)
	fi

	# Format based on amount with dollar sign
	if (($(echo "$cost_dollars < 0.01" | bc -l))); then
		# Show 4 decimal places for very small amounts (less than 1 cent)
		cost_display=$(printf "\$%.4f" "$cost_dollars")
	else
		# Show 2 decimal places for amounts 1 cent and above
		cost_display=$(printf "\$%.2f" "$cost_dollars")
	fi

	# Apply color and emoji with reset
	cost_info=$(printf " | %s %b%s%b" "${emoji}" "${color}" "${cost_display}" "\033[0m")

	# ============================================================================
	# SPENDING TRACKER INTEGRATION
	# ============================================================================
	# Track spending using plugin (data stored in plugin directory)
	spending_update=""
	if (($(echo "$cost_dollars > 0" | bc -l))); then
		# Extract session ID from transcript path (filename without extension)
		session_id="unknown"
		if [ -n "$transcript_path" ] && [ "$transcript_path" != "null" ]; then
			transcript_name=$(basename "$transcript_path")
			session_id="${transcript_name%.jsonl}"
		fi

		# Call plugin script with --data-dir pointing to plugin directory
		PLUGIN_DIR="$HOME/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/spending-tracker-plugin"
		PLUGIN_DATA_DIR="$PLUGIN_DIR/spending_data"
		add_result=$(python3 "$PLUGIN_DIR/scripts/track_spending.py" \
			--data-dir "$PLUGIN_DATA_DIR" \
			add-session \
			--session-id "$session_id" \
			--cost "$cost_dollars" \
			2>/dev/null || echo '{}')
		delta_added=$(echo "$add_result" | jq -r '.delta_added // empty' 2>/dev/null)

		# Only show update message if we actually added new spending
		if [ -n "$delta_added" ] && [ "$delta_added" != "0" ] && [ "$delta_added" != "0.0" ]; then
			delta_display=$(printf "\$%.4f" "$delta_added")
			spending_update=$(printf "💰 Added %b%s%b to spending tracker" "\033[96m" "$delta_display" "\033[0m")
		fi
	fi
fi

# ============================================================================
# GET GLOBAL SPENDING TOTALS (for display)
# ============================================================================
spending_totals=""
if command -v python3 >/dev/null 2>&1; then
	PLUGIN_DIR="$HOME/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/spending-tracker-plugin"
	PLUGIN_DATA_DIR="$PLUGIN_DIR/spending_data"
	totals_json=$(python3 "$PLUGIN_DIR/scripts/track_spending.py" \
		--data-dir "$PLUGIN_DATA_DIR" \
		get \
		--format json \
		2>/dev/null || echo '{}')

	daily_total=$(echo "$totals_json" | jq -r '.daily_total // 0' 2>/dev/null || echo "0")
	weekly_total=$(echo "$totals_json" | jq -r '.weekly_total // 0' 2>/dev/null || echo "0")
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

	# Format weekly total with color tiers
	if [ -n "$weekly_total" ] && [ "$weekly_total" != "0" ] && [ "$weekly_total" != "null" ]; then
		# Determine weekly color tier
		if (($(echo "$weekly_total >= 100.00" | bc -l 2>/dev/null || echo 0))); then
			weekly_color="\033[1;91m"  # Bold Red - high weekly spending
		elif (($(echo "$weekly_total >= 30.00" | bc -l 2>/dev/null || echo 0))); then
			weekly_color="\033[93m"    # Yellow - moderate weekly spending
		else
			weekly_color="\033[92m"    # Green - low weekly spending
		fi
		weekly_display=$(printf "\$%.2f" "$weekly_total")
		spending_totals="${spending_totals}$(printf " | 📆 %b%s%b/wk" "${weekly_color}" "${weekly_display}" "\033[0m")"
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

# Format output style with bright pink color
style_info=""
if [ -n "$output_style" ] && [ "$output_style" != "null" ]; then
	style_info=$(printf " | 🎨 %b%s%b" "\033[1;95m" "$output_style" "\033[0m") # Bold bright magenta for style
fi

# Note: transcript path will be handled separately on its own line

# Output formatted status line with colored elements
# Directory in default color, Model in lighter blue
dir_display="$(basename "$dir")"                                          # Default color for directory
model_colored=$(printf "%b%s%b" "\033[94m" "$model" "\033[0m")           # Bright blue for model

printf "📁 %s%s ⚙️ %s%s%s%s" "$dir_display" "$git_info" "$model_colored" "$cost_info" "$spending_totals" "$style_info"

# Output spending update on separate line if it exists
if [ -n "$spending_update" ]; then
	printf "\n%s" "$spending_update"
fi

# Output transcript path on separate line if it exists (cyan)
if [ -n "$transcript_path" ] && [ "$transcript_path" != "null" ]; then
	transcript_name=$(basename "$transcript_path")
	transcript_colored=$(printf "%b%s%b" "\033[36m" "$transcript_name" "\033[0m") # Cyan for transcript
	printf "\n📝 %s" "$transcript_colored"
fi

