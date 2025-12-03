REF---
name: GCLOUD
description: Google Cloud credentials setup and management for Google Drive/Gmail integration
keywords: google, gcloud, credentials, oauth, drive, gmail, api
location: /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/GCLOUD.md
---

# Google Cloud Credentials Setup

## How Credentials Were Located

### Discovery Process

1. **User mentioned Gmail MCP was already configured**
   - Checked Claude Desktop config at `/Users/wz/.claude.json`
   - Found Gmail MCP server configuration:
   ```json
   "@gongrzhe/server-gmail-autoauth-mcp": {
     "env": {
       "GMAIL_OAUTH_PATH": "/Users/wz/Desktop/OAuth2/gcp-oauth.keys.json",
       "GMAIL_CREDENTIALS_PATH": "/Users/wz/.gmail-mcp/credentials.json"
     }
   }
   ```

2. **Located OAuth Credentials**
   - Path: `/Users/wz/Desktop/OAuth2/gcp-oauth.keys.json`
   - Size: 412 bytes
   - Created: Sep 24 16:12
   - Contains: OAuth 2.0 client credentials from Google Cloud Console

3. **Located Stored Token**
   - Path: `/Users/wz/.gmail-mcp/credentials.json`
   - Size: 552 bytes
   - Created: Sep 26 03:44
   - Contains: Authenticated user token (access + refresh tokens)

## File Locations

```bash
# OAuth Client Credentials (from Google Cloud Console)
/Users/wz/Desktop/OAuth2/gcp-oauth.keys.json

# Authenticated User Token (after OAuth flow)
/Users/wz/.gmail-mcp/credentials.json

# Token for Drive API (auto-created by gdrive_sync.py)
/tmp/token.pickle
```

## Using Credentials for Google Drive

### Setup Script

```python
# /tmp/gdrive_sync.py uses these credentials

# 1. Looks for credentials.json (OAuth client config)
CREDENTIALS_FILE = '/tmp/credentials.json'  # Copy of gcp-oauth.keys.json

# 2. Creates/uses token.pickle (authenticated session)
TOKEN_FILE = 'token.pickle'  # Created after first auth
```

### Integration Steps

1. **Copy OAuth credentials to working directory:**
   ```bash
   cp /Users/wz/Desktop/OAuth2/gcp-oauth.keys.json /tmp/credentials.json
   ```

2. **First-time authentication (creates token.pickle):**
   ```bash
   cd /tmp
   python3 gdrive_sync.py /path/to/file.md
   # Opens browser → Login to Google → Grant permissions
   # Creates token.pickle for future use
   ```

3. **Subsequent uses (automatic):**
   ```bash
   python3 gdrive_sync.py /path/to/file.md
   # Uses existing token.pickle, no browser needed
   ```

## API Scopes

### Gmail MCP Scopes
```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.compose
```

### Drive API Scopes (used by gdrive_sync.py)
```
https://www.googleapis.com/auth/drive.file
```

**Note:** Different scopes = Different tokens needed
- Gmail token: `/Users/wz/.gmail-mcp/credentials.json`
- Drive token: `/tmp/token.pickle`

## Quick Commands

### Sync file to Google Drive
```bash
python3 /tmp/gdrive_sync.py /path/to/file.md
```

### List files in Google Drive
```bash
python3 /tmp/gdrive_sync.py list
```

### Via Flask Server (from browser)
```javascript
// Click "📤 Sync to Drive" button in editor
// Calls: POST http://localhost:8765/sync-gdrive
```

## Troubleshooting

### "credentials.json not found"
```bash
cp /Users/wz/Desktop/OAuth2/gcp-oauth.keys.json /tmp/credentials.json
```

### "Token expired"
```bash
rm /tmp/token.pickle
python3 /tmp/gdrive_sync.py /path/to/file.md
# Re-authenticates via browser
```

### "Insufficient permissions"
```bash
# Token might have wrong scopes
rm /tmp/token.pickle
# Re-auth will request correct scopes
```

## Architecture

```
User edits in Browser
    ↓
Flask Server (/tmp/skill-server.py)
    ↓
Saves to local file (/tmp/skills/SKILL.md)
    ↓
Calls gdrive_sync.py
    ↓
Uses OAuth credentials (gcp-oauth.keys.json)
    ↓
Google Drive API
    ↓
Uploads to Google Drive (Skills folder)
```

## Files Created

```
/tmp/
├── credentials.json          # OAuth client config (copied)
├── token.pickle             # Authenticated session
├── gdrive_sync.py           # Sync script
├── skill-server.py          # Flask server with /sync-gdrive endpoint
└── skill-editor-server.html # Editor with "Sync to Drive" button
```

## Success Confirmation

When working correctly, you'll see:
```
✓ Folder 'Skills' created: <folder_id>
✓ Uploaded: SKILL.md (ID: <file_id>)
```

Check Google Drive: https://drive.google.com/drive/my-drive
- Should see "Skills" folder
- Should see uploaded .md files

## References

- OAuth credentials location: `/Users/wz/Desktop/OAuth2/gcp-oauth.keys.json`
- Gmail MCP config: `/Users/wz/.claude.json` (line 1539)
- Google Drive API docs: https://developers.google.com/drive/api/v3/about-sdk
- Official Python client: https://github.com/googleapis/google-api-python-client
