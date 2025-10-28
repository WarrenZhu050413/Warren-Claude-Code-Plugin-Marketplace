# gmaillm

LLM-friendly Gmail API wrapper with CLI and progressive disclosure patterns.

## Installation

```bash
cd /path/to/gmaillm
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
from gmaillm import GmailClient

client = GmailClient()

# List emails
result = client.list_emails(folder='INBOX', max_results=10)
print(result.to_markdown())

# Read email
email = client.read_email(message_id, format="summary")
print(email.to_markdown())
```

## Documentation

See the skill documentation for complete reference, style guide system, and workflows.

## Testing

```bash
python3 -m pytest tests/
```
