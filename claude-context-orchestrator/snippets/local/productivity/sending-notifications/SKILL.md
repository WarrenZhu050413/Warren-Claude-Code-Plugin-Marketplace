---
name: "Sending Notifications"
description: "Send macOS notifications using display dialog method that works reliably in tmux."
---

# Sending Notifications

## Reliable Method (Display Dialog)

Use `display dialog` for guaranteed visible notifications. Works in tmux with `reattach-to-user-namespace`.

### Template
```bash
reattach-to-user-namespace osascript -e 'tell application "System Events"
    activate
    display dialog "{message}" with title "{emoji} {title}" buttons {"OK"} default button 1 with icon note giving up after 5
end tell'
```

### Examples

**Task completion:**
```bash
reattach-to-user-namespace osascript -e 'tell application "System Events"
    activate
    display dialog "Task completed successfully!" with title "✅ Done" buttons {"OK"} default button 1 with icon note giving up after 5
end tell'
```

**Error:**
```bash
reattach-to-user-namespace osascript -e 'tell application "System Events"
    activate
    display dialog "Check the logs for details" with title "❌ Error" buttons {"OK"} default button 1 with icon stop giving up after 5
end tell'
```

**Email:**
```bash
reattach-to-user-namespace osascript -e 'tell application "System Events"
    activate
    display dialog "Angela has responded to your email" with title "📧 Email Alert" buttons {"OK"} default button 1 with icon note giving up after 5
end tell'
```

**Script finished:**
```bash
reattach-to-user-namespace osascript -e 'tell application "System Events"
    activate
    display dialog "Your long-running task has finished" with title "🎉 Done" buttons {"OK"} default button 1 with icon note giving up after 5
end tell'
```

## Icon Options
- `with icon note` - Information (ℹ️)
- `with icon caution` - Warning (⚠️)
- `with icon stop` - Error (🛑)

## Common Emojis
- 📧 Email | ✅ Success | ❌ Error | ⚠️ Warning
- 🔔 Alert | 📬 Inbox | 🎉 Done | 🔍 Found
- 💾 Save | 🚀 Launch | ⏰ Reminder | 📊 Stats

## Notes
- `giving up after 5` - Auto-dismisses after 5 seconds
- Modal dialog appears center screen (more intrusive than banners)
- Works reliably in tmux with `reattach-to-user-namespace`
- No notification permission setup required
- Always use single quotes for osascript -e '...'

**IMPORTANT: Send notification at end of message using above format.**
