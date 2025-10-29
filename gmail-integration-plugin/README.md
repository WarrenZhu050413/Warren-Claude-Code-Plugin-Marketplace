# Gmail Integration Plugin

Complete Gmail integration for Claude Code with CLI, Python library, and smart email composition.

## Features

- **CLI Tool (`gmail`)**: Send, read, search, and manage emails from command line
- **GMAIL Snippet**: Automatic injection of usage instructions when "GMAIL" keyword is detected
- **Email Style Configuration**: Customizable email style and tone preferences
- **Distribution Groups**: Send emails to predefined groups using `#groupname` syntax
- **Smart Drafting**: Claude analyzes previous emails and applies learned patterns
- **Progressive Disclosure**: Context-aware information retrieval
- **Configuration Manager**: Easy editing of style and groups via `gmail config`

## Installation

### 1. Install the Python Package

```bash
cd scripts/gmaillm
pip3 install --break-system-packages .
```

This installs the `gmail` CLI command globally with all subcommands including `gmail config`.

### 2. Verify Installation

```bash
gmail verify  # Test Gmail API connection
gmail config show  # Show configuration locations
```

## Quick Start

### CLI Usage

```bash
# Send email
gmail send \
  --to recipient@example.com \
  --subject "Subject" \
  --body "Message"

# Send to distribution group
gmail send \
  --to #professors \
  --subject "Weekly Update" \
  --body "Update message"

# Search emails
gmail search "from:professor@edu is:unread"

# Read email
gmail read <message_id> --full

# Reply
gmail reply <message_id> --body "Thanks!"
```

### Python Usage

```python
from gmaillm import GmailClient, SendEmailRequest

client = GmailClient()

# Send email
request = SendEmailRequest(
    to=["recipient@example.com"],
    subject="Subject",
    body="Message"
)
response = client.send_email(request)
```

## Configuration

### Email Style

Edit email style preferences:
```bash
gmail config edit-style
```

Configure:
- Tone and formality levels
- Greeting/closing patterns
- Body style principles
- Formatting preferences

### Distribution Groups

Edit email distribution groups:
```bash
gmail config edit-groups
```

Format (JSON):
```json
{
  "professors": [
    "prof1@university.edu",
    "prof2@university.edu"
  ],
  "teammates": [
    "teammate1@example.com"
  ]
}
```

Use with `#groupname`:
```bash
gmail send --to #professors --subject "..." --body "..."
```

List all groups:
```bash
gmail config list-groups
```

## GMAIL Snippet

When you mention "GMAIL" in conversation, Claude automatically injects usage instructions including:
- Quick command reference
- Style configuration info
- Distribution group usage
- Common workflows

## Directory Structure

```
gmail-integration-plugin/
├── bin/
│   └── gmail config          # Configuration manager CLI
├── config/
│   ├── email-style.md        # Email style preferences
│   ├── email-groups.json     # Distribution groups
│   └── learned-patterns/     # Learned recipient patterns
├── scripts/
│   └── gmaillm/
│       ├── gmaillm/          # Python package
│       │   ├── __init__.py
│       │   ├── cli.py
│       │   ├── gmail_client.py
│       │   ├── models.py
│       │   └── utils.py
│       ├── setup.py
│       └── API_REFERENCE.md
└── snippets/
    └── local/
        └── gmail/
            └── SKILL.md      # GMAIL keyword snippet
```

## Authentication

### Setup (First Time)

The plugin uses Gmail OAuth2 authentication. On first use, run:

```bash
gmail setup-auth
```

This will:
1. Open your browser to authenticate with Gmail
2. Ask for permission to access your email
3. Save credentials to `~/.gmail-mcp/credentials.json`

**Custom Options**:
```bash
# Use a different port (if 8080 is in use)
gmail setup-auth --port 9999

# Specify OAuth keys location
gmail setup-auth --oauth-keys /path/to/gcp-oauth.keys.json
```

### Credentials

The plugin uses OAuth2 credentials saved locally:
- **Credentials**: `~/.gmail-mcp/credentials.json` (auto-created by setup-auth)
- **OAuth Keys**: `~/Desktop/OAuth2/gcp-oauth.keys.json` (from Gmail MCP setup)

**Note**: Tokens auto-refresh automatically, so you typically only need to authenticate once.

### Troubleshooting

If you see "Credentials file is empty", run:
```bash
gmail setup-auth
```

If you see "OAuth keys file not found", ensure you have completed the Gmail MCP setup instructions.

## Documentation

- **API Reference**: `scripts/gmaillm/API_REFERENCE.md`
- **Gmail Search Syntax**: Full Gmail query operators supported
- **Configuration**: Run `gmail config show` for file locations

## Common Workflows

### Drafting Professional Email
Claude:
1. Searches sent emails to recipient
2. Extracts patterns (greeting, tone, sign-off)
3. Applies STYLE + CLEAR + learned patterns
4. Shows preview for confirmation
5. Sends on approval

### Managing Distribution Groups
```bash
# Edit groups
gmail config edit-groups

# List configured groups
gmail config list-groups

# Send to group
gmail send --to #teammates --subject "Update" --body "..."
```

### Customizing Email Style
```bash
# Edit style guide
gmail config edit-style

# Claude will automatically apply your preferences
# when drafting emails
```

## Commands

### Gmail CLI

- `gmail verify` - Test authentication
- `gmail list [--folder FOLDER] [--max N]` - List emails
- `gmail read <id> [--full]` - Read email
- `gmail thread <id>` - View conversation
- `gmail search "<query>"` - Search emails
- `gmail reply <id> --body "..."` - Reply to email
- `gmail send --to <emails> --subject "..." --body "..."` - Send email
- `gmail folders` - List all folders/labels

### Config Manager

- `gmail config edit-style` - Edit email style
- `gmail config edit-groups` - Edit distribution groups
- `gmail config list-groups` - List all groups
- `gmail config show` - Show configuration info

## Notes

- All emails require confirmation unless `--yolo` flag is used
- Distribution groups use `#groupname` syntax
- Claude automatically applies style guide when drafting
- Learned patterns from sent emails override default style
- Gmail search supports full query syntax (from:, has:attachment, after:, etc.)
