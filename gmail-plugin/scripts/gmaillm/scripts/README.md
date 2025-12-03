# GMAILLM Automation Scripts

This directory contains Python scripts for automating common email workflows using the gmaillm CLI.

## Available Scripts

### 1. process_workflow.py

Process gmail workflows autonomously with custom decision logic.

**Usage:**
```bash
python scripts/process_workflow.py <workflow_name> [--dry-run]
```

**Examples:**
```bash
# Process gmaillm inbox workflow
python scripts/process_workflow.py gmaillm-inbox

# Test workflow without taking actions
python scripts/process_workflow.py daily-clear --dry-run
```

**Features:**
- Autonomous email processing with workflows
- Customizable decision logic (determine_action function)
- Archive, reply, or skip actions
- Dry-run mode for testing
- Progress tracking and statistics

**Customization:**
Edit the `determine_action()` function to implement your own logic:
```python
def determine_action(email: Dict[str, Any]) -> str:
    from_addr = email.get('from', '').lower()
    subject = email.get('subject', '').lower()

    # Your custom rules here
    if 'newsletter' in from_addr:
        return 'archive'

    return 'skip'
```

### 2. email_notifier.py

Check for new important emails and send desktop notifications.

**Usage:**
```bash
python scripts/email_notifier.py [--query QUERY] [--max-results N] [--notify]
```

**Examples:**
```bash
# Check for unread important emails
python scripts/email_notifier.py --query "is:unread is:important"

# Check and notify for emails from your boss
python scripts/email_notifier.py --query "from:boss@example.com is:unread" --notify

# Check for emails with attachments
python scripts/email_notifier.py --query "has:attachment is:unread" --notify

# Quiet mode (just output count)
python scripts/email_notifier.py --query "is:unread" --quiet
```

**Features:**
- Gmail search query support
- Desktop notifications (macOS)
- Quiet mode for scripting
- Configurable result limits

**Common Gmail Queries:**
- `is:unread` - Unread emails
- `is:important` - Important emails
- `from:user@example.com` - From specific sender
- `to:user@example.com` - To specific recipient
- `has:attachment` - Has attachments
- `in:inbox` - In inbox
- `label:MyLabel` - Has specific label
- `after:2024/10/01` - After specific date

**Cron Job Example:**
```bash
# Check every 5 minutes for important emails
*/5 * * * * /usr/bin/python3 /path/to/scripts/email_notifier.py --query "is:unread is:important" --notify
```

### 3. inbox_cleanup.py

Automated inbox cleanup by archiving emails based on various criteria.

**Usage:**
```bash
python scripts/inbox_cleanup.py [OPTIONS]
```

**Examples:**
```bash
# Archive newsletters
python scripts/inbox_cleanup.py --archive-newsletters

# Archive emails older than 30 days
python scripts/inbox_cleanup.py --archive-older-than 30

# Use workflow for cleanup
python scripts/inbox_cleanup.py --workflow gmaillm-inbox

# Dry run (show what would be done)
python scripts/inbox_cleanup.py --archive-newsletters --dry-run

# Combine multiple actions
python scripts/inbox_cleanup.py --archive-newsletters --archive-older-than 60
```

**Features:**
- Archive newsletters automatically
- Archive old emails by age
- Workflow-based cleanup
- Dry-run mode for safety
- Progress tracking and statistics

**Cron Job Example:**
```bash
# Clean up inbox daily at 2 AM
0 2 * * * /usr/bin/python3 /path/to/scripts/inbox_cleanup.py --archive-newsletters --archive-older-than 30
```

## Installation

No additional installation needed - these scripts use the `gmail` CLI that's already installed.

## Requirements

- Python 3.7+
- gmaillm CLI installed and configured (`gmail verify`)
- macOS (for desktop notifications in email_notifier.py)

## Testing Scripts

All scripts support `--help` for detailed usage information:

```bash
python scripts/process_workflow.py --help
python scripts/email_notifier.py --help
python scripts/inbox_cleanup.py --help
```

## Common Patterns

### JSON Output Parsing

All scripts use JSON output from gmail CLI:

```python
def run_gmail_command(*args: str) -> Optional[Dict[str, Any]]:
    """Run gmail command and return JSON output"""
    cmd = ['gmail'] + list(args) + ['--output-format', 'json']
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return None

    return json.loads(result.stdout)
```

### Error Handling

All scripts handle errors gracefully:

```python
try:
    # Do work
    process_emails()
except KeyboardInterrupt:
    print("\nInterrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

### Dry Run Mode

All scripts that modify data support `--dry-run`:

```python
if dry_run:
    print(f"[DRY RUN] Would archive: {message_id}")
    return True
else:
    # Actually perform action
    archive_email(message_id)
```

## Customization

These scripts are designed to be easily customized:

1. **Copy the script** to create your own version
2. **Modify decision logic** in the relevant functions
3. **Add new features** using the gmail CLI commands
4. **Test with --dry-run** before running live

## Security Notes

- Scripts use subprocess to call gmail CLI
- No credentials are stored in scripts
- All authentication handled by gmail CLI
- Dry-run mode available for safety

## Troubleshooting

**Gmail CLI not found:**
```bash
# Check gmail is installed
which gmail

# If not found, install gmaillm
make install
```

**Permission denied:**
```bash
# Make scripts executable
chmod +x scripts/*.py
```

**JSON parsing errors:**
- Ensure you're using latest gmaillm version
- Check that `--output-format json` is supported
- Run `gmail --help` to verify CLI installation

## Further Reading

- [GMAILLM Documentation](../../README.md)
- [Workflow Guide](../../docs/workflows.md)
- [Gmail Search Operators](https://support.google.com/mail/answer/7190)

## Contributing

To add a new script:

1. Create `scripts/your_script.py`
2. Use the same structure as existing scripts
3. Add documentation to this README
4. Test with `--dry-run` mode
5. Make executable: `chmod +x scripts/your_script.py`
