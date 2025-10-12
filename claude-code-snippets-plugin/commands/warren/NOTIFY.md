---
SNIPPET_NAME: NOTIFY
ANNOUNCE_USAGE: true
---

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: NOTIFY

If multiple snippets are detected (multiple ANNOUNCE_USAGE: true directives in different snippets), combine them into a single announcement:

📎 **Active Contexts**: snippet1, snippet2, snippet3

---

# Notification Template

Use terminal-notifier to send macOS notifications in this exact format:

## Template Format
```bash
terminal-notifier -title "{emoji} {title}" -subtitle "Some subtitle" -message "More detailed message"
```

## Examples

### Email notification
```bash
terminal-notifier -title "📧 Email Alert" -subtitle "New message received" -message "Angela has responded to your email"
```

### Task completion
```bash
terminal-notifier -title "✅ Task Complete" -subtitle "Build finished" -message "The compilation completed successfully"
```

### Error notification
```bash
terminal-notifier -title "❌ Error" -subtitle "Process failed" -message "Check the logs for details"
```

### Script finished
```bash
terminal-notifier -title "🎉 Done" -subtitle "Script completed" -message "Your long-running task has finished"
```

## Common Emojis
- 📧 Email
- ✅ Success/Complete
- ❌ Error/Failed
- ⚠️ Warning
- 🔔 Alert/Bell
- 📬 Message/Inbox
- 🎉 Celebration/Done
- 🔍 Search/Found
- 💾 Save
- 🚀 Launch/Start
- ⏰ Time/Reminder
- 📊 Data/Stats

## Notes
- No sound parameter = silent notification
- Notifications appear in top-right corner
- Click notification to dismiss
- Check System Settings > Notifications if not appearing

**IMPORTANT: At the end of your message, you should notify using the above format!**

## Verification
**VERIFICATION_HASH:** `b5040ce37609d8a9`
