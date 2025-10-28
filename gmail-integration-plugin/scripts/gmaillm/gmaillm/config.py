"""Configuration management for gmaillm.

Provides centralized path management with plugin-aware defaults.
Defaults to plugin credentials directory if available, otherwise ~/.gmaillm/
"""

import os
from pathlib import Path
from typing import Final


def _get_config_dir() -> Path:
    """Determine the configuration directory.

    Priority:
    1. $CLAUDE_PLUGIN_ROOT/credentials/ (if running from plugin)
    2. ~/.gmaillm/ (standalone fallback)

    Returns:
        Path to the configuration directory
    """
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root) / "credentials"
    return Path.home() / ".gmaillm"


# Config directory - plugin-aware
CONFIG_DIR: Final[Path] = _get_config_dir()

# Core configuration files
CREDENTIALS_FILE: Final[Path] = CONFIG_DIR / "credentials.json"
OAUTH_KEYS_FILE: Final[Path] = CONFIG_DIR / "oauth-keys.json"

# User customization files
EMAIL_GROUPS_FILE: Final[Path] = CONFIG_DIR / "email-groups.json"
OUTPUT_STYLE_FILE: Final[Path] = CONFIG_DIR / "output-style.json"

# Fallback locations for OAuth keys (legacy compatibility)
FALLBACK_OAUTH_LOCATIONS: Final[tuple[Path, ...]] = (
    Path.home() / ".gmaillm" / "oauth-keys.json",  # Standalone installation
    Path.home() / "Desktop" / "OAuth2" / "gcp-oauth.keys.json",  # Common dev location
    Path.home() / ".config" / "gmaillm" / "oauth-keys.json",  # XDG config
    Path("gcp-oauth.keys.json"),  # Current directory
)

# File permissions for sensitive files (owner read/write only)
SECURE_FILE_MODE: Final[int] = 0o600

# File permissions for non-sensitive files (owner read/write, group/others read)
NORMAL_FILE_MODE: Final[int] = 0o644


def ensure_config_dir() -> Path:
    """Ensure the config directory exists with proper permissions.

    Returns:
        Path to the config directory

    Raises:
        OSError: If directory cannot be created
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    return CONFIG_DIR


def get_credentials_file() -> Path:
    """Get path to credentials file, ensuring parent directory exists.

    Returns:
        Path to credentials.json
    """
    ensure_config_dir()
    return CREDENTIALS_FILE


def get_oauth_keys_file() -> Path:
    """Get path to OAuth keys file, ensuring parent directory exists.

    Returns:
        Path to oauth-keys.json
    """
    ensure_config_dir()
    return OAUTH_KEYS_FILE


def find_oauth_keys_file() -> Path | None:
    """Find OAuth keys file in standard locations.

    Searches in order:
    1. ~/.gmaillm/oauth-keys.json (standard location)
    2. Fallback locations for backward compatibility

    Returns:
        Path to OAuth keys file if found, None otherwise
    """
    # Check standard location first
    if OAUTH_KEYS_FILE.exists():
        return OAUTH_KEYS_FILE

    # Check fallback locations
    for path in FALLBACK_OAUTH_LOCATIONS:
        if path.exists():
            return path

    return None
