"""Gmail OAuth2 Authentication Setup.

This script helps you authenticate with Gmail API and save credentials.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

from google_auth_oauthlib.flow import InstalledAppFlow

from .config import (
    SECURE_FILE_MODE,
    ensure_config_dir,
    find_oauth_keys_file,
    get_credentials_file,
    get_oauth_keys_file,
)

# Set up logging
logger = logging.getLogger(__name__)

# Gmail API scopes - define what permissions we need
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",  # Read emails
    "https://www.googleapis.com/auth/gmail.send",  # Send emails
    "https://www.googleapis.com/auth/gmail.modify",  # Modify labels, mark as read
    "https://www.googleapis.com/auth/gmail.compose",  # Create drafts
]


def validate_oauth_keys(oauth_keys_path: Path) -> bool:
    """Validate OAuth keys file structure.

    Args:
        oauth_keys_path: Path to the OAuth keys file

    Returns:
        True if valid, False otherwise
    """
    try:
        with open(oauth_keys_path) as f:
            data = json.load(f)

        # Check for required structure - OAuth keys can be in 'installed' or 'web' format
        if "installed" in data:
            client_config = data["installed"]
        elif "web" in data:
            client_config = data["web"]
        else:
            logger.error("OAuth keys file missing 'installed' or 'web' section")
            print("❌ Invalid OAuth keys file: missing 'installed' or 'web' section")
            return False

        # Validate required fields
        required_fields = ["client_id", "client_secret"]
        missing_fields = [field for field in required_fields if field not in client_config]

        if missing_fields:
            logger.error(f"OAuth keys missing required fields: {missing_fields}")
            print(f"❌ Invalid OAuth keys file: missing required fields {missing_fields}")
            return False

        return True

    except FileNotFoundError:
        logger.error(f"OAuth keys file not found: {oauth_keys_path}")
        print(f"❌ OAuth keys file not found: {oauth_keys_path}")
        return False
    except PermissionError:
        logger.error(f"Permission denied reading OAuth keys: {oauth_keys_path}")
        print(f"❌ Permission denied reading OAuth keys file: {oauth_keys_path}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in OAuth keys file: {e}")
        print(f"❌ Invalid JSON in OAuth keys file: {e}")
        return False


def check_existing_credentials(credentials_path: Path) -> bool:
    """Check if valid credentials already exist.

    Args:
        credentials_path: Path to check for credentials

    Returns:
        True if user wants to overwrite, False to keep existing
    """
    if not credentials_path.exists():
        return True

    print(f"\n⚠️  Credentials already exist at: {credentials_path}")
    print("This will overwrite your existing authentication.")

    while True:
        response = input("Continue and overwrite? (yes/no): ").strip().lower()
        if response in ("yes", "y"):
            logger.info("User chose to overwrite existing credentials")
            return True
        elif response in ("no", "n"):
            logger.info("User chose to keep existing credentials")
            print("✅ Keeping existing credentials.")
            return False
        else:
            print("Please enter 'yes' or 'no'")


def setup_authentication(
    oauth_keys_file: Optional[str] = None,
    credentials_file: Optional[str] = None,
    port: int = 8080,
) -> Optional[Path]:
    """Set up Gmail API authentication via OAuth2 flow.

    Args:
        oauth_keys_file: Path to OAuth2 client secrets (gcp-oauth.keys.json)
        credentials_file: Path to save credentials (default: ~/.gmaillm/credentials.json)
        port: Local server port for OAuth callback (default: 8080)

    Returns:
        Path to saved credentials file, or None if setup failed

    Raises:
        OSError: If directory creation fails
    """
    # Find OAuth keys file
    oauth_path: Optional[Path] = None
    if oauth_keys_file is None:
        oauth_path = find_oauth_keys_file()
    else:
        oauth_path = Path(oauth_keys_file)

    if oauth_path is None:
        logger.error("OAuth keys file not found in any standard location")
        print("❌ OAuth keys file not found!")
        print("\nSearched locations:")
        print(f"  - {get_oauth_keys_file()}")
        for fallback in [
            Path.home() / "Desktop" / "OAuth2" / "gcp-oauth.keys.json",
            Path("gcp-oauth.keys.json"),
        ]:
            print(f"  - {fallback}")
        print("\nPlease download your OAuth2 client secrets from Google Cloud Console:")
        print("  https://console.cloud.google.com/apis/credentials")
        print("\nSave it as 'oauth-keys.json' in one of the above locations.")
        return None

    # Validate OAuth keys file
    if not validate_oauth_keys(oauth_path):
        return None

    # Set credentials file path
    creds_path: Path
    if credentials_file is None:
        creds_path = get_credentials_file()
    else:
        creds_path = Path(credentials_file)

    # Check for existing credentials
    if not check_existing_credentials(creds_path):
        return creds_path

    # Ensure parent directory exists with secure permissions
    ensure_config_dir()

    print(f"📁 Using OAuth keys: {oauth_path}")
    print(f"📁 Will save credentials to: {creds_path}")
    print()

    # Run OAuth flow
    print("🔐 Starting OAuth2 authentication flow...")
    print("🌐 Your browser will open to authenticate with Google.")
    print(f"📍 Callback URL: http://localhost:{port}")
    print()

    try:
        logger.info(f"Starting OAuth flow with port {port}")
        flow = InstalledAppFlow.from_client_secrets_file(
            str(oauth_path),
            SCOPES,
        )

        creds = flow.run_local_server(
            port=port,
            success_message="✅ Authentication successful! You can close this window.",
            open_browser=True,
        )

        # Save credentials
        creds_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }

        # Write with secure permissions
        creds_path.touch(mode=SECURE_FILE_MODE, exist_ok=True)
        with open(creds_path, "w") as f:
            json.dump(creds_data, f, indent=2)
        # Ensure secure permissions are set (touch mode may not work on all systems)
        os.chmod(creds_path, SECURE_FILE_MODE)

        logger.info(f"Credentials saved successfully to {creds_path}")
        print()
        print("✅ Authentication successful!")
        print(f"✅ Credentials saved to: {creds_path}")
        print(f"🔒 File permissions set to {oct(SECURE_FILE_MODE)}")
        print()
        print("You can now use the Gmail CLI:")
        print("  gmail verify")
        print("  gmail list")
        print()

        return creds_path

    except FileNotFoundError as e:
        logger.error(f"File not found during OAuth: {e}")
        print(f"\n❌ Authentication failed: Required file not found")
        print(f"\nPlease check that OAuth keys file exists: {oauth_path}")
        return None

    except PermissionError as e:
        logger.error(f"Permission denied during OAuth: {e}")
        print(f"\n❌ Authentication failed: Permission denied")
        print(f"\nPlease check file permissions for: {creds_path}")
        return None

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON during OAuth: {e}")
        print(f"\n❌ Authentication failed: Invalid JSON in OAuth keys file")
        print(f"\nPlease check the format of: {oauth_path}")
        return None

    except OSError as e:
        logger.error(f"OS error during OAuth: {e}")
        print(f"\n❌ Authentication failed: System error occurred")
        print(f"\nCommon issues:")
        print(f"  - Port {port} may already be in use (try --port 8081)")
        print(f"  - Firewall may be blocking local connections")
        return None

    except Exception as e:
        # Sanitize exception message to avoid leaking sensitive data
        error_type = type(e).__name__
        logger.error(f"OAuth flow failed: {error_type}")
        print(f"\n❌ Authentication failed: {error_type}")
        print()
        print("Common issues:")
        print(
            f"  - Make sure the redirect URI 'http://localhost:{port}' is configured in Google Cloud Console"
        )
        print("  - Check that the Gmail API is enabled in your GCP project")
        print("  - Verify your OAuth2 client is for 'Desktop app' type")
        print(f"  - If port {port} is in use, try a different port with --port option")
        return None


def main() -> None:
    """Command-line interface for authentication setup."""
    import argparse

    # Set up logging for CLI
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Set up Gmail API authentication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default locations
  python3 -m gmaillm.setup_auth

  # Specify custom OAuth keys file
  python3 -m gmaillm.setup_auth --oauth-keys ~/my-keys.json

  # Use custom port (if 8080 is in use)
  python3 -m gmaillm.setup_auth --port 8081
""",
    )

    parser.add_argument(
        "--oauth-keys",
        type=str,
        help="Path to OAuth2 client secrets (gcp-oauth.keys.json)",
    )

    parser.add_argument(
        "--credentials",
        type=str,
        help="Path to save credentials (default: ~/.gmaillm/credentials.json)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Local server port for OAuth callback (default: 8080)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("  Gmail API Authentication Setup")
    print("=" * 70)
    print()

    result = setup_authentication(
        oauth_keys_file=args.oauth_keys,
        credentials_file=args.credentials,
        port=args.port,
    )

    if result is None:
        print("\n⚠️  Setup incomplete. Please address the issues above.")
        exit(1)
    else:
        print("✅ Setup complete!")
        exit(0)


if __name__ == "__main__":
    main()
