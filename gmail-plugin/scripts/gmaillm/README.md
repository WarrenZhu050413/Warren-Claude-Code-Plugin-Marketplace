# gmaillm

LLM-friendly Gmail API wrapper with CLI and progressive disclosure patterns.

## Installation

### Recommended: Using Makefile (Easiest)

For the simplest installation with automatic setup:

```bash
cd /path/to/gmaillm

# Install globally and setup shell completion
make install
make verify
make install-completion
```

See `make help` for all available targets.

### Alternative: Manual Installation

```bash
cd /path/to/gmaillm
pip3 install --break-system-packages -e .
```

### With Shell Completion (Recommended)

For faster typing with tab-completion support:

```bash
# 1. Install the package
pip3 install --break-system-packages -e .

# 2. Install shell completions
gmail --install-completion

# 3. Restart your shell
exec $SHELL
```

**Note:** After running `--install-completion`, you'll see a message confirming the completion script was installed. Restart your shell to activate it.

### Supported Shells
- **bash** - Uses `~/.bash_completion.d/` or `~/.bashrc`
- **zsh** - Uses `~/.zshrc` or completion directory
- **fish** - Uses `~/.config/fish/completions/`
- **PowerShell** - Uses profile completion directory

## Setup & Authentication

### Configuration Locations

gmaillm automatically detects whether it's running as a plugin or standalone:

- **Plugin mode** (when `CLAUDE_PLUGIN_ROOT` is set):
  - Config: `${CLAUDE_PLUGIN_ROOT}/credentials/`
  - OAuth keys: `${CLAUDE_PLUGIN_ROOT}/credentials/oauth-keys.json`
  - Credentials: `${CLAUDE_PLUGIN_ROOT}/credentials/credentials.json`

- **Standalone mode** (default):
  - Config: `~/.gmaillm/`
  - OAuth keys: `~/.gmaillm/oauth-keys.json`
  - Credentials: `~/.gmaillm/credentials.json`

### First Time Setup

1. **Obtain OAuth2 credentials** from Google Cloud Console:
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create OAuth2 Client ID (Application type: Desktop app)
   - Download the credentials as `oauth-keys.json`
   - Save to one of these locations:
     - `~/.gmaillm/oauth-keys.json` (recommended for standalone)
     - `${CLAUDE_PLUGIN_ROOT}/credentials/oauth-keys.json` (for plugin use)
     - `~/Desktop/OAuth2/gcp-oauth.keys.json` (fallback)

2. **Authenticate with Gmail**:
   ```bash
   gmail setup-auth
   ```
   This will:
   - Open your browser for Google authentication
   - Save credentials to the appropriate location (plugin or standalone)
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

# Manage labels
gmail label list          # List all labels (system and custom)
gmail label create MyLabel # Create a new label

# Manage email styles
gmail styles list                    # List all email styles
gmail styles show professional-formal # View a specific style
gmail styles create my-style         # Create a new style
gmail styles validate my-style       # Validate style format
gmail styles validate-all --fix      # Validate and auto-fix all styles
```

## Email Styles

gmaillm supports a flexible email style system that allows you to define different writing styles for various contexts. Each style includes templates, formatting guidelines, and usage patterns.

### Style Commands

```bash
# List all styles
gmail styles list

# View a specific style
gmail styles show professional-formal

# Create a new style (opens editor)
gmail styles create my-new-style

# Edit an existing style (opens editor)
gmail styles edit casual-friend

# Delete a style
gmail styles delete old-style
gmail styles delete old-style --force  # Skip confirmation

# Validate style format
gmail styles validate my-style
gmail styles validate my-style --fix   # Auto-fix formatting issues

# Validate all styles
gmail styles validate-all
gmail styles validate-all --fix        # Auto-fix all styles
```

### Style Format

Each style file uses YAML frontmatter and XML-like sections:

```markdown
---
name: "Style Name"
description: "When to use: Context description with usage guidance."
---

<examples>
Example email 1
---
Example email 2
</examples>

<greeting>
- "Hi [Name],"
- "Hello [Name],"
</greeting>

<body>
- Writing guideline 1
- Writing guideline 2
</body>

<closing>
- "Best,"
- "Thanks,"
</closing>

<do>
- What to do
- Best practices
</do>

<dont>
- What to avoid
- Common mistakes
</dont>
```

**Required sections** (in strict order):
1. `examples` - Example emails showing the style in action
2. `greeting` - Greeting patterns and guidelines
3. `body` - Body content guidelines
4. `closing` - Closing patterns
5. `do` - Best practices
6. `dont` - Things to avoid

See [STYLES.md](STYLES.md) for complete style guide documentation.

## Workflows

### Interactive Workflows

Process emails interactively with prompts for each action:

```bash
# Run named workflow
gmail workflows run clear

# Run with custom query
gmail workflows run --query "is:unread from:boss@example.com"
```

### LLM-Friendly Workflows (Programmatic)

Process emails programmatically with continuation tokens for automation:

```bash
# Start workflow (returns JSON with token + first email)
gmail workflows start clear

# Continue with actions (returns next email + same token)
gmail workflows continue <token> archive
gmail workflows continue <token> skip
gmail workflows continue <token> reply --reply-body "Thanks!"
gmail workflows continue <token> view    # View full body
gmail workflows continue <token> quit    # End workflow
```

**JSON Response:**
```json
{
  "success": true,
  "token": "abc123...",
  "email": { /* full email data */ },
  "message": "Archived",
  "progress": {"total": 10, "processed": 3, "remaining": 7, "current": 4},
  "completed": false
}
```

**Automation Example:**
```bash
# Archive all unread emails
TOKEN=$(gmail workflows start clear | jq -r '.token')
while [ "$TOKEN" != "null" ]; do
  RESULT=$(gmail workflows continue "$TOKEN" archive)
  TOKEN=$(echo "$RESULT" | jq -r '.token')
done
```

### Workflow Management

```bash
gmail workflows list              # List configured workflows
gmail workflows show clear        # View workflow details
gmail workflows create daily \
  --query "is:unread" \
  --auto-mark-read                # Create new workflow
gmail workflows cleanup           # Remove expired states
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

## Tips & Tricks

### Speed Up Typing with Completions
Once you've installed shell completions (`gmail --install-completion`), you can:
- Type `gmail l` and press `<TAB>` → expands to available commands
- Type `gmail send --to user` and press `<TAB>` → shows field completions
- Type `gmail ` and press `<TAB>` → shows all available commands

### Quick Command Reference
```bash
# Most common commands
gmail verify                              # Check if setup is working
gmail status                              # See your inbox status
gmail list                                # Show recent emails
gmail search "from:someone@example.com"  # Find specific emails
gmail send --to user@example.com \
  --subject "Hello" --body "Hi there"    # Send an email
```

### Help for Any Command
```bash
# Get help for a specific command
gmail send --help
gmail search --help
```

## Documentation

### User Guides
- **[Email Styles Guide](../docs/email-styles.md)** - Creating and managing email writing styles
- **[Email Groups Guide](../docs/email-groups.md)** - Managing email distribution groups

### Technical Documentation
- **[Testing Guide](TESTING.md)** - Running and writing tests
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Changelog](CHANGELOG.md)** - Version history and changes

## Testing

```bash
make test                 # Run full test suite with coverage
uv run pytest tests/      # Run tests directly
```
