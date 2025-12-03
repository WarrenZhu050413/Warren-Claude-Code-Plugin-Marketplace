---
description: Guide for using the gcallm CLI to add events to Google Calendar with natural language
---

# Google Calendar CLI Usage Guide

Use the `gcallm` CLI to add events to Google Calendar using natural language.

## Quick Reference

### Add Events
```bash
# Direct text input
gcallm "Meeting with Sarah tomorrow at 3pm"
gcallm "Lunch next Tuesday 12-1pm at Cafe Nero"
gcallm add "Team standup Mon-Fri 9:30am"

# Multiple events at once
gcallm "Team standup Mon-Fri 9:30am, Coffee with Alex Thursday 2pm"
```

### From Files (Preferred for Automation)
```bash
# Pipe from file
cat /tmp/gcal/events.txt | gcallm
cat schedule.txt | gcallm

# Echo to stdin
echo "Doctor appointment Friday 10am" | gcallm
```

### From Clipboard
```bash
# Uses clipboard if no stdin/args provided
gcallm
```

### From Screenshots
```bash
# Parse latest screenshot on Desktop
gcallm -s "Add events from this screenshot"

# Parse multiple screenshots
gcallm --screenshots 2 "Add from last 2 screenshots"
```

### Ask Questions
```bash
# General calendar questions
gcallm ask "What's on my calendar today?"
gcallm ask "When is my next meeting?"
gcallm ask "Am I free Thursday afternoon?"
```

### List Calendars
```bash
gcallm calendars
```

## Common Workflow

**Recommended approach for scripts:**
```bash
# 1. Write event details to a temp file
cat > /tmp/gcal/events.txt << 'EOF'
Meeting with Prof. Smith Monday 2pm
Coffee with Alex Tuesday 10am
Team standup Wed-Fri 9:30am
EOF

# 2. Pipe to gcallm
cat /tmp/gcal/events.txt | gcallm
```

## Natural Language Examples

gcallm understands flexible date/time formats:
- "tomorrow at 3pm"
- "next Tuesday 12-1pm"
- "Monday through Friday at 9:30am"
- "December 15th 2pm for 2 hours"
- "Coffee with Alex 10am at Starbucks"
- "Team meeting every Monday 9am"

## Configuration

```bash
# Configure model (default: claude-sonnet-4-20250514)
gcallm config --model claude-sonnet-4-20250514

# Configure custom prompt
gcallm config --prompt "Custom extraction prompt"

# Show current config
gcallm config --show
```

Config stored at: `~/.config/gcallm/config.json`

## Verification

```bash
# Verify setup
gcallm verify
```

## Troubleshooting

### "MCP server not configured" Error
Ensure the Google Calendar MCP is configured in Claude Code:
```bash
claude mcp add gcal npx @anthropic/mcp-google-calendar -s local
```

### OAuth Issues
Re-run setup:
```bash
gcallm setup ~/path/to/oauth-keys.json
```

## Related Commands

- `/gcal:setup` - Set up gcallm with OAuth credentials
