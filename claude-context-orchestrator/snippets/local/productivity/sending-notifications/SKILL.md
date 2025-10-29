---
name: "Sending Notifications"
description: "Send macOS notifications using terminal-notifier with standardized formatting."
---

# Sending Notifications

## Template
```bash
terminal-notifier -title "{emoji} {title}" -subtitle "Some subtitle" -message "More detailed message"
```

## Examples

**Email:**
```bash
terminal-notifier -title "📧 Email Alert" -subtitle "New message received" -message "Angela has responded to your email"
```

**Task completion:**
```bash
terminal-notifier -title "✅ Task Complete" -subtitle "Build finished" -message "The compilation completed successfully"
```

**Error:**
```bash
terminal-notifier -title "❌ Error" -subtitle "Process failed" -message "Check the logs for details"
```

**Script finished:**
```bash
terminal-notifier -title "🎉 Done" -subtitle "Script completed" -message "Your long-running task has finished"
```

## Common Emojis
- 📧 Email | ✅ Success | ❌ Error | ⚠️ Warning
- 🔔 Alert | 📬 Inbox | 🎉 Done | 🔍 Found
- 💾 Save | 🚀 Launch | ⏰ Reminder | 📊 Stats

## Notes
- No sound parameter = silent
- Top-right corner display
- Click to dismiss
- Check System Settings > Notifications if not appearing

**IMPORTANT: Send notification at end of message using above format.**
