# Plugin-Aware Credentials System

## Overview

gmaillm now automatically detects whether it's running as a Claude Code plugin or standalone, and stores credentials accordingly.

## Configuration Paths

### Plugin Mode (when `CLAUDE_PLUGIN_ROOT` is set)

**Location:** `${CLAUDE_PLUGIN_ROOT}/credentials/`

```
gmail-integration-plugin/
├── credentials/                    # Auto-detected plugin config directory
│   ├── oauth-keys.json            # Your OAuth2 client secrets
│   ├── credentials.json           # Generated after authentication
│   ├── email-groups.json          # (optional) Email group aliases
│   └── output-style.json          # (optional) Custom output styling
└── ...
```

### Standalone Mode (default)

**Location:** `~/.gmaillm/`

```
~/.gmaillm/
├── oauth-keys.json                # Your OAuth2 client secrets
├── credentials.json               # Generated after authentication
├── email-groups.json              # (optional) Email group aliases
└── output-style.json              # (optional) Custom output styling
```

## Setup Instructions

### Option 1: Plugin Use (Recommended for Claude Code)

1. **Download OAuth2 credentials** from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

2. **Save to plugin directory:**
   ```bash
   # Create credentials directory
   mkdir -p ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/gmail-integration-plugin/credentials

   # Copy your OAuth keys
   cp ~/Downloads/client_secret_*.json \
      ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/gmail-integration-plugin/credentials/oauth-keys.json
   ```

3. **Authenticate (sets `CLAUDE_PLUGIN_ROOT` automatically when run from plugin):**
   ```bash
   gmail setup-auth
   ```

   Credentials will be saved to `${CLAUDE_PLUGIN_ROOT}/credentials/credentials.json`

### Option 2: Standalone Use

1. **Download OAuth2 credentials** from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

2. **Save to home directory:**
   ```bash
   mkdir -p ~/.gmaillm
   cp ~/Downloads/client_secret_*.json ~/.gmaillm/oauth-keys.json
   ```

3. **Authenticate:**
   ```bash
   gmail setup-auth
   ```

   Credentials will be saved to `~/.gmaillm/credentials.json`

## Fallback Search Order

When looking for OAuth keys, gmaillm searches in this order:

1. **Primary location** (plugin or standalone depending on `CLAUDE_PLUGIN_ROOT`)
   - Plugin: `${CLAUDE_PLUGIN_ROOT}/credentials/oauth-keys.json`
   - Standalone: `~/.gmaillm/oauth-keys.json`

2. **Fallback locations:**
   - `~/.gmaillm/oauth-keys.json` (legacy standalone)
   - `~/Desktop/OAuth2/gcp-oauth.keys.json` (common dev location)
   - `~/.config/gmaillm/oauth-keys.json` (XDG config)
   - `./gcp-oauth.keys.json` (current directory)

## Security

- All credential files use **0600** permissions (owner read/write only)
- The `credentials/` directory is **gitignored** to prevent accidental commits
- Never commit `credentials.json` or `oauth-keys.json` to version control

## Migration from Old Paths

If you previously used `~/.gmail-mcp/`:

```bash
# Copy old credentials to new location
cp ~/.gmail-mcp/gcp-oauth.keys.json ~/.gmaillm/oauth-keys.json
cp ~/.gmail-mcp/credentials.json ~/.gmaillm/credentials.json

# Or for plugin use:
mkdir -p ~/.claude/plugins/.../gmail-integration-plugin/credentials
cp ~/.gmail-mcp/gcp-oauth.keys.json \
   ~/.claude/plugins/.../gmail-integration-plugin/credentials/oauth-keys.json
cp ~/.gmail-mcp/credentials.json \
   ~/.claude/plugins/.../gmail-integration-plugin/credentials/credentials.json
```

## Verification

Check which mode you're in:

```bash
uv run python3 -c "
from gmaillm.config import CONFIG_DIR
print(f'Config directory: {CONFIG_DIR}')
"
```

**Plugin mode output:**
```
Config directory: /Users/.../gmail-integration-plugin/credentials
```

**Standalone mode output:**
```
Config directory: /Users/username/.gmaillm
```

## Testing

Run the test suite to verify configuration:

```bash
make test
```

Or manually test with environment variable:

```bash
# Test plugin mode
CLAUDE_PLUGIN_ROOT=/path/to/plugin uv run python3 -c "
from gmaillm.config import CONFIG_DIR
print(CONFIG_DIR)
"

# Test standalone mode
uv run python3 -c "
from gmaillm.config import CONFIG_DIR
print(CONFIG_DIR)
"
```

## Changes Made

1. **config.py**: Added `_get_config_dir()` to detect `CLAUDE_PLUGIN_ROOT`
2. **Fallback locations**: Updated to prioritize `~/.gmaillm/` over old `~/.gmail-mcp/`
3. **.gitignore**: Added `credentials/` directory exclusion
4. **README.md**: Documented plugin-aware configuration
5. **Makefile**: Updated to use `uv` commands

## Benefits

✅ **No manual configuration** - Automatically detects plugin vs standalone
✅ **Cleaner organization** - Credentials live with plugin code
✅ **Git-safe** - Credentials directory is gitignored
✅ **Backward compatible** - Standalone mode still works with `~/.gmaillm/`
✅ **Flexible** - Fallback locations for legacy setups
