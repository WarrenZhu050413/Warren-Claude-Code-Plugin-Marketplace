# Gmail Plugin

Send, search, and manage emails from the command line.

## Use Case

You want Claude to help compose emails, search your inbox, or send messages without leaving the terminal. The `/gmail` command teaches Claude how to use the CLI. The `/gmail:setup` command walks through authentication.

## Setup

1. Install the plugin:
   ```bash
   /plugin install gmail-plugin@warren-claude-code-plugin-marketplace
   ```

2. Install the CLI:
   ```bash
   cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/gmail-plugin/scripts/gmaillm
   make install
   ```

3. Get OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/apis/credentials):
   - Enable Gmail API
   - Create Desktop app OAuth credentials
   - Save as `~/.gmaillm/oauth-keys.json`

4. Authenticate:
   ```bash
   gmail setup-auth
   gmail verify
   ```

## Usage

```bash
gmail list --max 10                              # List recent emails
gmail search "from:someone@example.com"          # Search
gmail read <id> --full                           # Read email
gmail send --to user@example.com --subject "Hi" --body "Hello"
```

Run `/gmail` for the full command reference.

Hope you enjoy!
