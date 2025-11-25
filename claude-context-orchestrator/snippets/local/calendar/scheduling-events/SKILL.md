---
name: "Scheduling Events"
description: "Schedule and manage Google Calendar events using gcallm CLI."
---

# Scheduling Events with gcallm

## Common Workflow (Recommended)

```bash
# 1. Write event details to /tmp/gcal/events.txt
# 2. Pipe to gcallm
cat /tmp/gcal/events.txt | gcallm
```

## Basic Usage

```bash
# Direct text input
gcallm "Meeting with Sarah tomorrow at 3pm"
gcallm "Lunch next Tuesday 12-1pm at Cafe Nero"

# Multiple events at once
gcallm "Team standup Mon-Fri 9:30am, Coffee with Alex Thursday 2pm"
```

## Input from Files (Stdin)

```bash
# Pipe from file
cat /tmp/gcal/events.txt | gcallm
cat schedule.txt | gcallm

# Echo to stdin
echo "Doctor appointment Friday 10am" | gcallm
```

## Other Input Modes

```bash
# From clipboard
gcallm  # Uses clipboard if no stdin provided

# From screenshots (latest screenshot on Desktop)
gcallm -s "Add events from this screenshot"
gcallm --screenshots 2 "Add from last 2 screenshots"
```

## Ask Questions

```bash
# General calendar questions
gcallm ask "What's on my calendar today?"
gcallm ask "When is my next meeting?"
gcallm ask "Am I free Thursday afternoon?"
```

## Key Patterns

1. **Stdin-first**: Prefer `cat file | gcallm` for non-interactive workflows
2. **Natural language**: gcallm understands flexible date/time formats
3. **Multiple events**: Separate with commas or natural language
4. **Today's date**: gcallm automatically knows current date/time
