---
description: Set up Gmail CLI authentication with OAuth2
---

# Gmail CLI Setup

This command guides you through setting up the `gmail` CLI for the first time.

## Prerequisites

You need OAuth2 credentials from Google Cloud Console.

## Step 1: Get OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select an existing one
3. Enable the **Gmail API**:
   - Go to "APIs & Services" > "Enable APIs and Services"
   - Search for "Gmail API" and enable it
4. Create OAuth2 credentials:
   - Go to "Credentials" > "Create Credentials" > "OAuth client ID"
   - Application type: **Desktop app**
   - Name: "Gmail CLI" (or any name)
   - Click "Create"
5. Download the credentials JSON file
6. Save it as `~/.gmaillm/oauth-keys.json`:
   ```bash
   mkdir -p ~/.gmaillm
   mv ~/Downloads/client_secret_*.json ~/.gmaillm/oauth-keys.json
   chmod 600 ~/.gmaillm/oauth-keys.json
   ```

## Step 2: Install gmaillm

```bash
# Install from source
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/gmail-integration-plugin/scripts/gmaillm
make install
```

## Step 3: Authenticate

Run the setup command:
```bash
gmail setup-auth
```

This will:
1. Open your browser for Google authentication
2. Ask you to grant Gmail access to the CLI
3. Save credentials to `~/.gmaillm/credentials.json`

**If port 8080 is in use:**
```bash
gmail setup-auth --port 8081
```

## Step 4: Verify Installation

```bash
gmail verify
```

Expected output:
```
Gmail API authentication: OK
```

## Troubleshooting

### "Credentials file is empty" Error
```bash
# Re-run authentication
python3 -m gmaillm.setup_auth

# If port is blocked
python3 -m gmaillm.setup_auth --port 9999
```

### "Address already in use" Error
```bash
# Kill any existing auth processes
pkill -f "gmaillm.setup_auth"

# Try a different port
gmail setup-auth --port 8081
```

### OAuth Keys Location
The CLI searches for OAuth keys in this order:
1. `~/.gmaillm/oauth-keys.json` (recommended)
2. `${CLAUDE_PLUGIN_ROOT}/credentials/oauth-keys.json` (plugin mode)
3. `~/Desktop/OAuth2/gcp-oauth.keys.json` (fallback)

## File Structure After Setup

```
~/.gmaillm/
├── oauth-keys.json     # OAuth2 client secrets (0600)
├── credentials.json    # Saved credentials (0600)
├── email-groups.json   # Email distribution groups
├── output-style.json   # Output formatting preferences
└── email-styles/       # Email style templates
    ├── professional-formal.md
    ├── professional-friendly.md
    └── casual-friend.md
```

## Optional: Shell Completion

Enable tab completion for faster typing:
```bash
gmail --install-completion
exec $SHELL
```

## Related Commands

- `/gmail` - Usage guide for gmail CLI
