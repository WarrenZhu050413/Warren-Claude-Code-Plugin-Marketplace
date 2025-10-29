# Mail Wrapper

LLM-friendly Gmail API wrapper with CLI and progressive disclosure patterns.

## Installation

```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/scripts/mail_wrapper
pip3 install --break-system-packages -e .
```

## Quick Start

### CLI Usage

```bash
# Verify setup
gmail verify

# List emails
gmail list
gmail list --folder SENT --max 5

# Read email
gmail read <message_id>
gmail read <message_id> --full

# View thread
gmail thread <message_id>

# Search
gmail search "from:example@gmail.com has:attachment"

# Reply
gmail reply <message_id> --body "Thanks for the update!"

# Send
gmail send --to user@example.com --subject "Test" --body "Hello"

# List folders
gmail folders
```

### Python Library

```python
from mail_wrapper import GmailClient

client = GmailClient()

# List emails
result = client.list_emails(folder='INBOX', max_results=10)
print(result.to_markdown())

# Read email
email = client.read_email(message_id, format="summary")
print(email.to_markdown())
```

## Documentation

See `/skills/mail-wrapper/SKILL.md` for complete documentation, style guide system, and workflows.

## Testing

```bash
python3 -m pytest tests/
```
