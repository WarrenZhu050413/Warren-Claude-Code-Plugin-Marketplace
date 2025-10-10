# Usage Examples

## Gmail Examples

### Example 1: Sending an Email

**Your message**:
```
Can you send an email to sarah@example.com about the project update?
Subject: Q4 Project Status Update
```

**What happens**:
1. The "mail" snippet activates (keyword: "email")
2. Claude drafts the email for your review
3. Searches your past emails for tone/style
4. Shows you the draft
5. After approval, sends via Gmail API
6. Adds "Sent from Claude Code" signature

### Example 2: Searching Emails

**Your message**:
```
Find emails from john@company.com in the last week about the budget
```

**What happens**:
1. Snippet activates (keyword: "emails")
2. Uses Gmail search with filters:
   - From: john@company.com
   - Date range: last 7 days
   - Keyword: "budget"
3. Returns matching emails with summaries

### Example 3: Draft a Reply

**Your message**:
```
Draft a reply to the latest message in my inbox from the HR team
```

**What happens**:
1. Fetches latest email from HR
2. Analyzes context and content
3. Searches similar past replies for your style
4. Drafts response matching your tone
5. Shows draft for your review

## Google Calendar Examples

### Example 1: Create an Event

**Your message**:
```
Schedule a team standup tomorrow at 10am for 30 minutes
```

**What happens**:
1. The "gcal" snippet activates (keyword: "Schedule")
2. Gets today's date (from snippet context)
3. Calculates tomorrow's date
4. Creates event:
   - Title: "Team Standup"
   - Time: Tomorrow at 10:00 AM
   - Duration: 30 minutes
5. Confirms creation

### Example 2: Check Calendar

**Your message**:
```
What meetings do I have this week?
```

**What happens**:
1. Snippet activates (keyword: "meetings", "calendar" implied)
2. Gets current date
3. Queries Google Calendar for this week
4. Returns list of events with times

### Example 3: Update an Event

**Your message**:
```
Move my 2pm meeting today to 3pm
```

**What happens**:
1. Finds events at 2pm today
2. Updates start time to 3pm
3. Preserves duration and other details
4. Confirms update

## Combined Workflow Examples

### Example 1: Meeting + Email Follow-up

**Your message**:
```
I have a meeting with the sales team about Q4 planning. Can you:
1. Add it to my calendar for next Monday at 2pm
2. Send an email to the team with the agenda
```

**What happens**:
1. Both snippets activate (keywords: "calendar", "email")
2. Creates calendar event
3. Drafts email with meeting details
4. Shows both for review
5. Executes after approval

### Example 2: Event from Email

**Your message**:
```
Check my latest email from Alice and add the meeting she proposed to my calendar
```

**What happens**:
1. Searches Gmail for latest from Alice
2. Extracts meeting details (time, date, topic)
3. Creates calendar event
4. Optionally replies confirming

## Keyword Reference

### Email Triggers
- `email` - "Can you email John?"
- `mail` - "Check my mail for updates"
- `e-mail` - "Send an e-mail to support"
- `message` - "Message the team about this"
- `inbox` - "What's in my inbox?"
- `send to` - "Send to sarah@example.com"
- `send message` - "Send message to the group"

### Calendar Triggers
- `gcal` - "Add to gcal"
- `g-cal` - "Check g-cal for conflicts"
- `google calendar` - "Google calendar shows..."
- `calendar` - "Put it on my calendar"
- `event` - "Create an event for the meeting"
- `schedule` - "Schedule a call with Alex"
- `appointment` - "Book an appointment"

## Tips

1. **Be specific with dates**: "tomorrow at 2pm" is better than "soon"
2. **Review drafts**: Emails are shown before sending
3. **Use natural language**: No need for rigid commands
4. **Combine tasks**: Claude can handle multi-step workflows
5. **Check context**: Make sure keywords trigger the right snippets

## Advanced Examples

### Batch Email Operations

**Your message**:
```
Find all unread emails from last week and summarize the action items
```

### Recurring Events

**Your message**:
```
Schedule a weekly team sync every Monday at 10am starting next week
```

### Calendar Availability

**Your message**:
```
When am I free for a 1-hour meeting this week?
```

### Email Templates

**Your message**:
```
Send a follow-up email to everyone who attended yesterday's meeting
```
