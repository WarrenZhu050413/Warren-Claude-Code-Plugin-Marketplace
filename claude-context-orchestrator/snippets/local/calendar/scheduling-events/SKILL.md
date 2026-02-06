---
name: "Google Calendar Management"
description: "Create, update, delete, and query Google Calendar events using gcallm CLI, MCP tools, or direct API calls."
---

# Google Calendar Management

Three access methods, in order of preference:

## 1. gcallm CLI (Creating Events)

Best for creating events from natural language or file input.

```bash
# Direct text
gcallm "Meeting with Sarah tomorrow at 3pm"

# From file (preferred for multi-event)
cat /tmp/gcal/events.txt | gcallm

# From clipboard
gcallm

# From screenshot
gcallm -s "Add events from this screenshot"

# Ask questions
gcallm ask "What's on my calendar today?"
gcallm ask "Am I free Thursday afternoon?"
```

## 2. MCP Tools (Full CRUD When Available)

When the `google-calendar` MCP server is connected, these tools are available:

```
mcp__google-calendar__list-events    # List events in a time range
mcp__google-calendar__search-events  # Search by query string
mcp__google-calendar__create-event   # Create event
mcp__google-calendar__update-event   # Update event (supports recurring with modificationScope)
mcp__google-calendar__delete-event   # Delete event
```

### Updating Recurring Events

Use `modificationScope` to control which instances are affected:
- `all` — update/delete the entire series
- `this` — only this instance
- `thisAndFollowing` — this and all future instances

### Color IDs

| ID | Color |
|----|-------|
| 1  | Lavender |
| 2  | Sage |
| 3  | Grape |
| 4  | Flamingo |
| 5  | Banana |
| 6  | Tangerine |
| 7  | Peacock |
| 8  | Graphite |
| 9  | Blueberry |
| 10 | Basil |
| 11 | Tomato (Red) |

## 3. Direct Google Calendar API (Fallback)

When MCP tools are unavailable, use the REST API with stored OAuth tokens.

### Token Location

```
/Users/wz/.config/google-calendar-mcp/tokens.json
```

### Read Token

```bash
TOKEN=$(python3 -c "import json; print(json.load(open('/Users/wz/.config/google-calendar-mcp/tokens.json'))['normal']['access_token'])")
```

### Common API Calls

```bash
# List events
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=2026-01-01T00:00:00Z&timeMax=2026-12-31T23:59:59Z&singleEvents=true"

# Search events
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events?q=SEARCH_TERM&timeMin=...&timeMax=...&singleEvents=true"

# Create event
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events" \
  -d '{"summary":"Event Title","location":"Place","colorId":"11","start":{"dateTime":"2026-02-03T09:00:00","timeZone":"America/New_York"},"end":{"dateTime":"2026-02-03T10:00:00","timeZone":"America/New_York"},"recurrence":["RRULE:FREQ=WEEKLY;COUNT=16;BYDAY=TU"]}'

# Update event (single instance)
curl -s -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events/EVENT_ID" \
  -d '{"colorId":"11"}'

# Delete event (entire recurring series — use base recurring event ID, no instance suffix)
curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events/RECURRING_EVENT_ID"

# Delete single instance
curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events/EVENT_ID_WITH_INSTANCE_SUFFIX"
```

### Recurring Event IDs

- Base ID: `abc123` — represents the series
- Instance ID: `abc123_20260203T140000Z` — represents one occurrence
- Deleting/updating the base ID affects all instances
- Each instance has `recurringEventId` pointing back to the base

### RRULE Examples

```
RRULE:FREQ=WEEKLY;COUNT=16;BYDAY=TU          # Every Tuesday for 16 weeks
RRULE:FREQ=WEEKLY;COUNT=16;BYDAY=MO,WE       # Mon & Wed for 16 weeks
RRULE:FREQ=WEEKLY;COUNT=16;BYDAY=TU,TH       # Tue & Thu for 16 weeks
RRULE:FREQ=DAILY;COUNT=5                      # Daily for 5 days
RRULE:FREQ=WEEKLY;UNTIL=20260530T000000Z      # Weekly until date
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200  | Success (GET/PATCH) |
| 204  | Success (DELETE) |
| 401  | Token expired — need to refresh or re-auth via MCP server |
| 404  | Event not found |
| 409  | Conflict (duplicate) |

## Warren's Calendar

- Account: `wzhu@college.harvard.edu`
- Timezone: `America/New_York`
- Calendar ID: `primary`
