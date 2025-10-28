"""
Gmail OAuth2 Authentication Setup

This script helps you authenticate with Gmail API and save credentials.
"""

import os
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
]

DEFAULT_CREDENTIALS_FILE = Path.home() / ".gmail-mcp" / "credentials.json"
DEFAULT_OAUTH_KEYS_FILE = Path.home() / ".gmail-mcp" / "gcp-oauth.keys.json"
FALLBACK_OAUTH_KEYS = Path.home() / "Desktop" / "OAuth2" / "gcp-oauth.keys.json"


def find_oauth_keys_file():
    """Find OAuth keys file in common locations."""
    candidates = [
        DEFAULT_OAUTH_KEYS_FILE,
        FALLBACK_OAUTH_KEYS,
        Path("gcp-oauth.keys.json"),  # Current directory
    ]

    for path in candidates:
        if path.exists():
            return path

    return None


def setup_authentication(
    oauth_keys_file=None,
    credentials_file=None,
    port=8080,
):
    """
    Set up Gmail API authentication via OAuth2 flow.

    Args:
        oauth_keys_file: Path to OAuth2 client secrets (gcp-oauth.keys.json)
        credentials_file: Path to save credentials (default: ~/.gmail-mcp/credentials.json)
        port: Local server port for OAuth callback (default: 8080)

    Returns:
        Path to saved credentials file
    """

    # Find OAuth keys file
    if oauth_keys_file is None:
        oauth_keys_file = find_oauth_keys_file()

    if oauth_keys_file is None:
        print("❌ OAuth keys file not found!")
        print("\nSearched locations:")
        print(f"  - {DEFAULT_OAUTH_KEYS_FILE}")
        print(f"  - {FALLBACK_OAUTH_KEYS}")
        print(f"  - ./gcp-oauth.keys.json")
        print("\nPlease download your OAuth2 client secrets from Google Cloud Console:")
        print("  https://console.cloud.google.com/apis/credentials")
        print("\nSave it as 'gcp-oauth.keys.json' in one of the above locations.")
        return None

    oauth_keys_file = Path(oauth_keys_file)

    # Set default credentials file
    if credentials_file is None:
        credentials_file = DEFAULT_CREDENTIALS_FILE
    else:
        credentials_file = Path(credentials_file)

    # Create directory if needed
    credentials_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"📁 Using OAuth keys: {oauth_keys_file}")
    print(f"📁 Will save credentials to: {credentials_file}")
    print()

    # Load OAuth keys
    try:
        with open(oauth_keys_file, 'r') as f:
            oauth_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in OAuth keys file: {e}")
        return None

    # Run OAuth flow
    print("🔐 Starting OAuth2 authentication flow...")
    print(f"🌐 Your browser will open to authenticate with Google.")
    print(f"📍 Callback URL: http://localhost:{port}")
    print()

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(oauth_keys_file),
            SCOPES,
        )

        creds = flow.run_local_server(
            port=port,
            success_message="✅ Authentication successful! You can close this window.",
            open_browser=True,
        )

        # Save credentials
        creds_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes,
        }

        with open(credentials_file, 'w') as f:
            json.dump(creds_data, f, indent=2)

        print()
        print("✅ Authentication successful!")
        print(f"✅ Credentials saved to: {credentials_file}")
        print()
        print("You can now use the Gmail CLI:")
        print("  gmail verify")
        print("  gmail list")
        print()

        return credentials_file

    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print()
        print("Common issues:")
        print("  - Make sure the redirect URI 'http://localhost:8080' is configured in Google Cloud Console")
        print("  - Check that the Gmail API is enabled in your GCP project")
        print("  - Verify your OAuth2 client is for 'Desktop app' type")
        return None


def main():
    """Command-line interface for authentication setup."""
    import argparse

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
"""
    )

    parser.add_argument(
        '--oauth-keys',
        type=str,
        help='Path to OAuth2 client secrets (gcp-oauth.keys.json)',
    )

    parser.add_argument(
        '--credentials',
        type=str,
        help='Path to save credentials (default: ~/.gmail-mcp/credentials.json)',
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Local server port for OAuth callback (default: 8080)',
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


if __name__ == '__main__':
    main()
