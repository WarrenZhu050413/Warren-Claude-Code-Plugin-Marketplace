"""Extended tests for config.py to cover edge cases."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from gmaillm.config import (
    ensure_config_dir,
    get_credentials_file,
    get_oauth_keys_file,
    find_oauth_keys_file,
    CONFIG_DIR,
    CREDENTIALS_FILE,
    OAUTH_KEYS_FILE,
    FALLBACK_OAUTH_LOCATIONS,
)


class TestFindOAuthKeysFile:
    """Test find_oauth_keys_file function."""

    def test_finds_file_in_standard_location(self, tmp_path, monkeypatch):
        """Test finding OAuth keys in standard ~/.gmaillm location."""
        # Create a temporary config dir
        fake_config_dir = tmp_path / ".gmaillm"
        fake_config_dir.mkdir()
        oauth_file = fake_config_dir / "oauth-keys.json"
        oauth_file.write_text('{"key": "value"}')

        # Mock CONFIG_DIR and OAUTH_KEYS_FILE
        monkeypatch.setattr("gmaillm.config.CONFIG_DIR", fake_config_dir)
        monkeypatch.setattr("gmaillm.config.OAUTH_KEYS_FILE", oauth_file)

        result = find_oauth_keys_file()

        assert result == oauth_file
        assert result.exists()

    def test_finds_file_in_fallback_location(self, tmp_path, monkeypatch):
        """Test finding OAuth keys in fallback locations."""
        # Standard location doesn't exist
        fake_config_dir = tmp_path / ".gmaillm"
        fake_oauth_file = fake_config_dir / "oauth-keys.json"

        # Create fallback location
        fallback_dir = tmp_path / "Desktop" / "OAuth2"
        fallback_dir.mkdir(parents=True)
        fallback_file = fallback_dir / "gcp-oauth.keys.json"
        fallback_file.write_text('{"key": "fallback"}')

        # Mock paths
        monkeypatch.setattr("gmaillm.config.CONFIG_DIR", fake_config_dir)
        monkeypatch.setattr("gmaillm.config.OAUTH_KEYS_FILE", fake_oauth_file)
        monkeypatch.setattr("gmaillm.config.FALLBACK_OAUTH_LOCATIONS", (
            fake_oauth_file,  # Standard location (doesn't exist)
            fallback_file,    # Fallback location (exists)
        ))

        result = find_oauth_keys_file()

        assert result == fallback_file
        assert result.exists()

    def test_returns_none_when_no_file_found(self, tmp_path, monkeypatch):
        """Test returns None when OAuth keys not found anywhere."""
        # Create non-existent paths
        fake_config_dir = tmp_path / ".gmaillm"
        fake_oauth_file = fake_config_dir / "oauth-keys.json"
        fake_fallback1 = tmp_path / "fallback1" / "oauth.json"
        fake_fallback2 = tmp_path / "fallback2" / "oauth.json"

        # Mock paths (none exist)
        monkeypatch.setattr("gmaillm.config.CONFIG_DIR", fake_config_dir)
        monkeypatch.setattr("gmaillm.config.OAUTH_KEYS_FILE", fake_oauth_file)
        monkeypatch.setattr("gmaillm.config.FALLBACK_OAUTH_LOCATIONS", (
            fake_fallback1,
            fake_fallback2,
        ))

        result = find_oauth_keys_file()

        assert result is None

    def test_prefers_standard_location_over_fallback(self, tmp_path, monkeypatch):
        """Test standard location is checked before fallbacks."""
        # Create both standard and fallback locations
        fake_config_dir = tmp_path / ".gmaillm"
        fake_config_dir.mkdir()
        standard_file = fake_config_dir / "oauth-keys.json"
        standard_file.write_text('{"location": "standard"}')

        fallback_dir = tmp_path / "fallback"
        fallback_dir.mkdir()
        fallback_file = fallback_dir / "oauth-keys.json"
        fallback_file.write_text('{"location": "fallback"}')

        # Mock paths
        monkeypatch.setattr("gmaillm.config.CONFIG_DIR", fake_config_dir)
        monkeypatch.setattr("gmaillm.config.OAUTH_KEYS_FILE", standard_file)
        monkeypatch.setattr("gmaillm.config.FALLBACK_OAUTH_LOCATIONS", (
            fallback_file,
        ))

        result = find_oauth_keys_file()

        # Should find standard location first
        assert result == standard_file
        assert result.read_text() == '{"location": "standard"}'

    def test_finds_first_existing_fallback(self, tmp_path, monkeypatch):
        """Test finds first existing file in fallback locations."""
        # Standard location doesn't exist
        fake_config_dir = tmp_path / ".gmaillm"
        fake_oauth_file = fake_config_dir / "oauth-keys.json"

        # Create multiple fallback locations
        fallback1 = tmp_path / "fallback1" / "oauth.json"  # Doesn't exist

        fallback2_dir = tmp_path / "fallback2"
        fallback2_dir.mkdir()
        fallback2 = fallback2_dir / "oauth.json"
        fallback2.write_text('{"location": "fallback2"}')

        fallback3_dir = tmp_path / "fallback3"
        fallback3_dir.mkdir()
        fallback3 = fallback3_dir / "oauth.json"
        fallback3.write_text('{"location": "fallback3"}')

        # Mock paths
        monkeypatch.setattr("gmaillm.config.CONFIG_DIR", fake_config_dir)
        monkeypatch.setattr("gmaillm.config.OAUTH_KEYS_FILE", fake_oauth_file)
        monkeypatch.setattr("gmaillm.config.FALLBACK_OAUTH_LOCATIONS", (
            fallback1,  # Doesn't exist
            fallback2,  # First existing
            fallback3,  # Also exists but shouldn't be checked
        ))

        result = find_oauth_keys_file()

        # Should find first existing fallback
        assert result == fallback2
        assert result.read_text() == '{"location": "fallback2"}'


class TestEnsureConfigDir:
    """Test ensure_config_dir edge cases."""

    def test_creates_parent_directories(self, tmp_path, monkeypatch):
        """Test creates nested parent directories if needed."""
        nested_config_dir = tmp_path / "level1" / "level2" / ".gmaillm"

        monkeypatch.setattr("gmaillm.config.CONFIG_DIR", nested_config_dir)

        result = ensure_config_dir()

        assert result == nested_config_dir
        assert nested_config_dir.exists()
        assert nested_config_dir.is_dir()

    def test_succeeds_when_directory_already_exists(self, tmp_path, monkeypatch):
        """Test succeeds when config directory already exists."""
        existing_dir = tmp_path / ".gmaillm"
        existing_dir.mkdir(mode=0o700)

        monkeypatch.setattr("gmaillm.config.CONFIG_DIR", existing_dir)

        result = ensure_config_dir()

        assert result == existing_dir
        assert existing_dir.exists()


class TestGetCredentialsFile:
    """Test get_credentials_file function."""

    def test_creates_config_dir_if_needed(self, tmp_path, monkeypatch):
        """Test ensures config directory exists."""
        fake_config_dir = tmp_path / ".gmaillm"
        fake_credentials_file = fake_config_dir / "credentials.json"

        monkeypatch.setattr("gmaillm.config.CONFIG_DIR", fake_config_dir)
        monkeypatch.setattr("gmaillm.config.CREDENTIALS_FILE", fake_credentials_file)

        result = get_credentials_file()

        assert result == fake_credentials_file
        assert fake_config_dir.exists()  # Directory was created


class TestGetOAuthKeysFile:
    """Test get_oauth_keys_file function."""

    def test_creates_config_dir_if_needed(self, tmp_path, monkeypatch):
        """Test ensures config directory exists."""
        fake_config_dir = tmp_path / ".gmaillm"
        fake_oauth_file = fake_config_dir / "oauth-keys.json"

        monkeypatch.setattr("gmaillm.config.CONFIG_DIR", fake_config_dir)
        monkeypatch.setattr("gmaillm.config.OAUTH_KEYS_FILE", fake_oauth_file)

        result = get_oauth_keys_file()

        assert result == fake_oauth_file
        assert fake_config_dir.exists()  # Directory was created
