# Google Drive API Authentication Setup

## Quick Setup (Already Configured)

Authentication is already configured at:
- **Credentials**: `~/.gdrivelm/credentials.json`
- **Settings**: `~/.gdrivelm/settings.yaml`
- **Token**: `~/.gdrivelm/token.json` (auto-generated)
- **Virtual Env**: `~/Desktop/zPersonalProjects/gdrivelm/venv/` (update to your path)

## Authentication Code Pattern

```python
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

def authenticate():
    """Authenticate with Google Drive API"""
    settings_path = os.path.expanduser('~/.gdrivelm/settings.yaml')
    token_path = os.path.expanduser('~/.gdrivelm/token.json')

    gauth = GoogleAuth(settings_file=settings_path)
    gauth.LoadCredentialsFile(token_path)

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile(token_path)
    return GoogleDrive(gauth)
```

## Settings Configuration

Located at `~/.gdrivelm/settings.yaml`:

```yaml
client_config_backend: file
client_config_file: /Users/wz/.gdrivelm/credentials.json

save_credentials: True
save_credentials_backend: file
save_credentials_file: /Users/wz/.gdrivelm/token.json

get_refresh_token: True

oauth_scope:
  - https://www.googleapis.com/auth/drive
  - https://www.googleapis.com/auth/drive.file
  - https://www.googleapis.com/auth/drive.metadata.readonly
```

## OAuth Scopes

- `https://www.googleapis.com/auth/drive` - Full Drive access
- `https://www.googleapis.com/auth/drive.file` - Per-file access
- `https://www.googleapis.com/auth/drive.metadata.readonly` - Metadata reading

## First Run

On first use, the authentication will:
1. Open browser for OAuth consent
2. Save token to `~/.gdrivelm/token.json`
3. Auto-refresh on subsequent uses

## Python Environment

Always activate the virtual environment first:

```bash
cd ~/Desktop/zPersonalProjects/gdrivelm
source venv/bin/activate
```

## Installed Packages

- PyDrive2 v1.21.3
- google-api-python-client v2.187.0
- google-auth-oauthlib v1.2.3
- google-auth-httplib2 v0.2.1
