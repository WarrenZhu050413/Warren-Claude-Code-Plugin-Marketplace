---
description: Set up gcallm CLI with Google Calendar OAuth2 credentials
---

# Google Calendar CLI Setup

This command guides you through setting up the `gcallm` CLI for adding events to Google Calendar.

## Prerequisites

You need:
1. OAuth2 credentials from Google Cloud Console
2. Google Calendar MCP server configured in Claude Code

## Step 1: Get OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select an existing one
3. Enable the **Google Calendar API**:
   - Go to "APIs & Services" > "Enable APIs and Services"
   - Search for "Google Calendar API" and enable it
4. Create OAuth2 credentials:
   - Go to "Credentials" > "Create Credentials" > "OAuth client ID"
   - Application type: **Desktop app**
   - Name: "Calendar CLI" (or any name)
   - Click "Create"
5. Download the credentials JSON file
6. Save it somewhere accessible (e.g., `~/gcp-oauth.keys.json`)

## Step 2: Install gcallm

```bash
# Install from PyPI
uv tool install gcallm

# Or with pip
pip install gcallm
```

Verify installation:
```bash
which gcallm
# Should output: ~/.local/bin/gcallm (or similar)
```

## Step 3: Configure OAuth Path

Point gcallm to your OAuth credentials:
```bash
gcallm setup ~/gcp-oauth.keys.json
```

Or interactively:
```bash
gcallm setup
# Will prompt for path
```

## Step 4: Configure Google Calendar MCP

gcallm requires the Google Calendar MCP server. Add it to Claude Code:

```bash
claude mcp add gcal npx @anthropic/mcp-google-calendar -s local
```

This uses the OAuth credentials you configured.

## Step 5: Verify Setup

```bash
gcallm verify
```

Expected output:
```
Google Calendar MCP: OK
OAuth credentials: Configured
```

Test with a simple query:
```bash
gcallm ask "What's on my calendar today?"
```

## Configuration Files

```
~/.config/gcallm/
├── config.json         # Settings (model, prompt)
└── oauth_path          # Path to OAuth credentials

# OAuth credentials (shared with other Google tools)
~/gcp-oauth.keys.json   # Or wherever you saved it
```

## Troubleshooting

### "MCP server not configured" Error

The Google Calendar MCP server isn't set up:
```bash
# Add the MCP server
claude mcp add gcal npx @anthropic/mcp-google-calendar -s local

# Verify it's configured
claude mcp list
```

### "OAuth credentials not found" Error

Re-run setup with the correct path:
```bash
gcallm setup /correct/path/to/oauth-keys.json
```

### Authentication Failed

Your OAuth token may have expired. Re-authenticate:
1. Delete existing credentials: `rm ~/.config/gcallm/*`
2. Re-run: `gcallm setup ~/gcp-oauth.keys.json`
3. Complete the browser authentication flow

### Permission Denied

Ensure the OAuth app has calendar scope:
1. Go to Google Cloud Console > APIs & Services > OAuth consent screen
2. Add scope: `https://www.googleapis.com/auth/calendar`

## Related Commands

- `/gcal` - Usage guide for gcallm CLI
