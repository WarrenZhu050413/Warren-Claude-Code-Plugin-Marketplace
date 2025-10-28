# gmaillm

LLM-friendly Gmail API wrapper with CLI and progressive disclosure patterns.

## Installation

```bash
cd /path/to/gmaillm
pip3 install --break-system-packages -e .
```

## Setup & Authentication

### First Time Setup

1. **Obtain OAuth2 credentials** from Google Cloud Console:
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create OAuth2 Client ID (Application type: Desktop app)
   - Download the credentials as `gcp-oauth.keys.json`
   - Save it to `~/.gmail-mcp/gcp-oauth.keys.json` or `~/Desktop/OAuth2/gcp-oauth.keys.json`

2. **Authenticate with Gmail**:
   ```bash
   python3 -m gmaillm.setup_auth
   ```
   This will:
   - Open your browser for Google authentication
   - Save credentials to `~/.gmail-mcp/credentials.json`
   - Configure Gmail API access

3. **Verify setup**:
   ```bash
   gmail verify
   ```

### Troubleshooting

If you see **"Credentials file is empty"** error:
```bash
# Run authentication setup
python3 -m gmaillm.setup_auth

# If port 8080 is in use, specify a different port
python3 -m gmaillm.setup_auth --port 8081
```

If you see **"Address already in use"** error:
```bash
# Kill any existing auth processes
pkill -f "gmaillm.setup_auth"

# Try a different port
python3 -m gmaillm.setup_auth --port 9999
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
