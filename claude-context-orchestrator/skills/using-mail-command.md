---
name: Using Mail Command
description: Comprehensive tutorial for the Unix mail/mailx command with Gmail OAuth integration
keywords: mail, mailx, email, unix, command-line, gmail, smtp, tutorial
---

HELLO WORLD

# Mail Command Tutorial

Complete guide to using the Unix `mail` command for sending and receiving emails from the command line.

## Table of Contents
1. [Basic Sending](#basic-sending)
2. [Advanced Sending Options](#advanced-sending-options)
3. [Interactive Mode](#interactive-mode)
4. [Reading Mail](#reading-mail)
5. [Special Characters & Escapes](#special-characters--escapes)
6. [Aliases & Distribution Lists](#aliases--distribution-lists)
7. [Configuration](#configuration)
8. [Gmail Integration](#gmail-integration)

---

## Basic Sending

### Simple Email with Piped Content

```bash
# Basic syntax
echo "Message body" | mail -s "Subject" recipient@example.com

# Example
echo "The build passed successfully!" | mail -s "Build Status" team@example.com
```

### Multiple Recipients

```bash
# Multiple recipients (space or comma separated)
echo "Team update" | mail -s "Update" alice@example.com bob@example.com

# Or comma-separated
echo "Team update" | mail -s "Update" alice@example.com,bob@example.com
```

### From a File

```bash
# Send file contents as email body
mail -s "Log Report" admin@example.com < /var/log/app.log

# Or with cat
cat report.txt | mail -s "Daily Report" boss@example.com
```

### Empty Body Email

```bash
# Subject-only email (empty body)
echo "" | mail -s "Server Restarted" sysadmin@example.com
```

---

## Advanced Sending Options

### CC (Carbon Copy)

```bash
# Send with CC
echo "Meeting notes" | mail -s "Notes" \
  -c "cc1@example.com,cc2@example.com" \
  primary@example.com
```

### BCC (Blind Carbon Copy)

```bash
# Send with BCC (recipients won't see each other)
echo "Announcement" | mail -s "News" \
  -b "secret@example.com" \
  public@example.com
```

### Combining CC and BCC

```bash
echo "Project update" | mail -s "Update" \
  -c "team@example.com" \
  -b "manager@example.com" \
  stakeholder@example.com
```

### Don't Send Empty Messages

```bash
# -E flag: skip if body is empty
some_command_that_might_fail | mail -E -s "Error Report" admin@example.com
```

### Verbose Mode

```bash
# -v flag: see delivery details
echo "Test" | mail -v -s "Test" recipient@example.com
```

---

## Interactive Mode

### Basic Interactive Sending

```bash
# Start interactive mode
mail recipient@example.com

# You'll see a prompt like:
Subject: Your Subject Here
# Type your message (multiple lines allowed):
This is line 1 of my message
This is line 2
This is line 3
# Press Ctrl+D to send
^D
EOT
```

### Interactive Mode with Subject

```bash
# Pre-set subject
mail -s "Project Update" team@example.com
# Now just type message and Ctrl+D to send
Status: All tests passing
Ready for deployment
^D
```

### Interactive Special Commands (Tilde Escapes)

When in interactive mode, lines starting with `~` have special meaning:

```bash
mail recipient@example.com
Subject: Test
~?          # Show help (list all tilde commands)
~v          # Open message in editor (uses $EDITOR)
~e          # Edit message with default editor
~p          # Print current message
~s "New Subject"  # Change subject
~c email@example.com  # Add CC recipient
~b email@example.com  # Add BCC recipient
~r filename # Read file into message
~w filename # Write message to file
~m 5        # Include message #5 (when replying)
~f 5        # Include message #5 with headers
~!command   # Run shell command
~|command   # Pipe message through command
~~          # Insert literal ~ at start of line
~.          # Send message (alternative to Ctrl+D)
~q          # Quit, save in ~/dead.letter
```

### Example Interactive Session

```bash
$ mail alice@example.com
Subject: Meeting Tomorrow
Hi Alice,
~p
# (Shows your message so far)
~s "Important: Meeting Tomorrow"
# (Changed subject)
~c bob@example.com
# (Added Bob as CC)
Let's meet at 2pm.
~.
# (Sent!)
```

---

## Reading Mail

### Check for New Mail

```bash
# Test if mailbox has mail (exit code 0 = yes, 1 = no)
mail -e
echo $?  # 0 if mail exists

# Show header summary
mail -H
```

### Read Your Mailbox

```bash
# Open default mailbox
mail

# You'll see message list:
# >  1 alice@example.com  Mon Oct 23  Project Update
#    2 bob@example.com    Tue Oct 24  Question
# >  3 system@example.com Wed Oct 25  Alert

# The > indicates current message
```

### Reading Commands

```bash
# In mail reading mode:
p       # Print current message
n       # Next message
-       # Previous message
1       # Go to message 1
p 5     # Print message 5
t 1-5   # Type messages 1 through 5
h       # Show headers
h+      # Next page of headers
h-      # Previous page of headers
z       # Scroll through headers
```

### Message Selection

```bash
# Print specific messages
p 1 3 5         # Messages 1, 3, and 5
p 1-10          # Messages 1 through 10
p *             # All messages
p $             # Last message
p .             # Current message
```

### Managing Messages

```bash
# Delete messages
d               # Delete current message
d 1-5           # Delete messages 1-5
d *             # Delete all messages

# Undelete
u 3             # Undelete message 3

# Save to file
s 5 saved.txt   # Save message 5 to saved.txt
s 1-10 archive  # Save messages 1-10 to archive file

# Copy (save without marking deleted)
c 5 backup.txt  # Copy message 5

# Hold (keep in mailbox)
ho 1-5          # Keep messages 1-5 in mailbox (don't move to mbox)
```

### Replying

```bash
r       # Reply to sender only
R       # Reply to sender only (same as r)
r 5     # Reply to message 5

# When replying, tilde escapes work:
~m      # Include original message (indented)
~f      # Include original with headers
```

### Folders

```bash
# Switch folders
fo inbox        # Open inbox folder
fo +work        # Open ~/Mail/work
fo %            # System mailbox
fo %bob         # Bob's system mailbox
fo &            # Your ~/mbox file
fo #            # Previous folder

# List folders
folders
```

### Exiting

```bash
q       # Quit - save read messages to ~/mbox, delete deleted ones
x       # Exit - don't save changes, restore deleted messages
quit    # Same as q
exit    # Same as x
```

---

## Special Characters & Escapes

### In Message Body (Interactive Mode)

All lines starting with `~` are special when composing interactively:

```
~!ls -la        # Run shell command
~|fmt -w 70     # Pipe message through formatter
~< filename     # Insert file at cursor
~r filename     # Read file into message (same as ~<)
~w filename     # Write message to file
~v              # Edit with vi/vim
~e              # Edit with $EDITOR
~p              # Print message so far
~h              # Edit headers (To, Cc, Bcc, Subject)
~t users        # Add recipients
~c users        # Add CC
~b users        # Add BCC
~s subject      # Change subject
~m [msglist]    # Include messages (indented with tab)
~f [msglist]    # Include messages with headers
~d              # Read ~/dead.letter
~q              # Quit, save to ~/dead.letter
~.              # Send message
~~text          # Insert literal ~text
```

---

## Aliases & Distribution Lists

### Personal Aliases

Create `~/.mailrc` file:

```bash
# Define aliases
alias team alice@example.com bob@example.com charlie@example.com
alias devs "dev1@example.com dev2@example.com dev3@example.com"
alias boss manager@company.com

# Use them
echo "Update" | mail -s "Status" team
```

### Managing Aliases

```bash
# In mail command:
alias               # List all aliases
alias team          # Show specific alias
alias newteam person1 person2  # Create new alias
```

### System-Wide Aliases

Defined in `/etc/mail/aliases` (requires admin access):

```
# /etc/mail/aliases
postmaster: root
webmaster: alice
support: team@example.com
```

---

## Configuration

### ~/.mailrc Configuration File

```bash
# ~/.mailrc - Personal mail configuration

# Use custom sendmail (for Gmail integration)
set sendmail="/tmp/gmail-send.py"

# Set your email and name
set from="yourname@gmail.com"
set realname="Your Full Name"

# Editor for composing
set EDITOR=vim
set VISUAL=code

# Ask for CC every time
set askcc

# Ask for BCC
set askbcc

# Don't ask for subject (useful for scripts)
unset asksub

# Save sent mail
set record=~/sent-mail

# Custom signature
set sign="~/.signature"

# Ignore headers when reading
ignore Received Message-Id Via Dkim-Signature

# Retain specific headers
retain From To Cc Subject Date

# Aliases
alias team alice@corp.com bob@corp.com
alias support help@company.com

# Auto-save to folders
set folder=~/Mail
set mbox=+mbox
set hold  # Keep messages in system mailbox by default
```

### Environment Variables

```bash
# Set in ~/.bashrc or ~/.zshrc
export MAIL=/var/mail/$USER        # System mailbox location
export MAILRC=~/.mailrc             # Config file
export DEAD=~/dead.letter           # Save unsent messages
export EDITOR=vim                   # Text editor for ~v
export PAGER=less                   # Pager for reading mail
```

---

## Gmail Integration

### Setup (Already Done for You!)

Your system is configured to use Gmail with OAuth (no app password needed):

**Files:**
- `/tmp/gmail-send.py` - Sends via Gmail API
- `~/.mailrc` - Configured to use gmail-send.py
- `/Users/wz/.gmail-mcp/credentials.json` - OAuth token
- `/Users/wz/Desktop/OAuth2/gcp-oauth.keys.json` - OAuth client keys

### Sending via Gmail

```bash
# Simple send
echo "Hello from command line!" | mail -s "Test" recipient@gmail.com

# With CC
echo "Team update" | mail -s "Update" \
  -c "teammate@company.com" \
  boss@company.com

# From file
mail -s "Report" manager@company.com < monthly-report.txt

# Interactive
mail colleague@gmail.com
Subject: Quick Question
Hey, do you have time for a call today?
^D
```

### Checking Gmail

To read Gmail via command line, you'd need:
1. Fetch mail using Gmail API or IMAP
2. Store in local mailbox
3. Read with `mail` command

**Alternative:** Use Gmail MCP tools directly in Claude Code for reading.

---

## Practical Examples

### Daily Log Email

```bash
#!/bin/bash
# Send daily system log
tail -100 /var/log/system.log | \
  mail -s "Daily System Log $(date +%Y-%m-%d)" \
  sysadmin@company.com
```

### Build Notification

```bash
#!/bin/bash
# Notify on build failure
if ! make build; then
  echo "Build failed at $(date)" | \
    mail -s "❌ Build Failed" \
    -c "team@company.com" \
    oncall@company.com
fi
```

### Multi-File Report

```bash
#!/bin/bash
# Send report with multiple sections
{
  echo "=== Summary ==="
  cat summary.txt
  echo ""
  echo "=== Details ==="
  cat details.txt
  echo ""
  echo "=== Metrics ==="
  cat metrics.txt
} | mail -s "Weekly Report $(date +%Y-%m-%d)" stakeholders@company.com
```

### Cron Job with Conditional Email

```bash
# In crontab (only email on errors)
0 2 * * * /path/to/backup.sh 2>&1 | mail -E -s "Backup Error" admin@company.com
```

### Quick Note to Self

```bash
# Add to ~/.bashrc
note() {
  echo "$*" | mail -s "Note: $(date +%H:%M)" yourname@gmail.com
}

# Usage:
note "Remember to review PR #123"
note "Meeting with Alice at 3pm"
```

### Emergency Alert

```bash
#!/bin/bash
# Alert multiple people immediately
ALERT_LIST="oncall@company.com cto@company.com"

echo "URGENT: Server down at $(hostname)" | \
  mail -s "🚨 CRITICAL ALERT" \
  -c "$ALERT_LIST" \
  sysadmin@company.com
```

---

## Troubleshooting

### Mail Not Sending?

```bash
# Check verbose mode for errors
echo "test" | mail -v -s "test" you@gmail.com

# Verify sendmail path
grep sendmail ~/.mailrc
ls -l /tmp/gmail-send.py

# Test sendmail directly
echo -e "Subject: Test\n\nBody" | /tmp/gmail-send.py you@gmail.com
```

### Permission Denied?

```bash
# Make sure gmail-send.py is executable
chmod +x /tmp/gmail-send.py

# Check ~/.mailrc permissions
ls -l ~/.mailrc
```

### OAuth Token Expired?

```bash
# Refresh token is automatic, but if issues persist:
# Re-run Gmail MCP authentication
# The token at ~/.gmail-mcp/credentials.json will refresh
```

---

## Quick Reference

### Most Common Commands

```bash
# SENDING
echo "msg" | mail -s "subj" recipient@email.com    # Simple send
mail -s "subj" recipient@email.com < file.txt      # From file
mail -s "subj" -c cc@email.com to@email.com        # With CC

# READING
mail                    # Open mailbox
p                       # Print message
n                       # Next message
d                       # Delete message
r                       # Reply
s file                  # Save to file
q                       # Quit and save
x                       # Quit without saving

# INTERACTIVE COMPOSING
~p                      # Print message
~v                      # Edit in editor
~m                      # Include original (reply)
~.                      # Send message
~q                      # Quit, save draft
```

### Exit Codes

```bash
0   # Success (for -e: mailbox has mail)
1   # Error (for -e: mailbox empty)
```

---

## See Also

- `man mail` - Complete manual
- `man mailx` - Extended features
- `~/.mailrc` - Your configuration
- `/tmp/gmail-send.py` - Gmail integration script

---

**Last Updated:** October 2025
**Configured for:** Gmail OAuth integration (no app password needed)
