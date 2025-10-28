"""Tests for cli.py module."""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import argparse
import json
from pathlib import Path
from io import StringIO

from gmaillm.cli import (
    get_plugin_config_dir,
    load_email_groups,
    expand_email_groups,
    main,
)
from gmaillm.models import EmailSummary, EmailAddress
from datetime import datetime


class TestGetPluginConfigDir:
    """Tests for get_plugin_config_dir function."""

    @patch.dict("os.environ", {"CLAUDE_PLUGIN_ROOT": "/test/plugin/root"})
    def test_with_env_variable(self):
        """Test getting config dir from environment variable."""
        result = get_plugin_config_dir()
        assert result == Path("/test/plugin/root/config")

    @patch.dict("os.environ", {}, clear=True)
    @patch("pathlib.Path.home")
    def test_without_env_variable(self, mock_home):
        """Test getting config dir without environment variable."""
        mock_home.return_value = Path("/home/user")
        result = get_plugin_config_dir()
        # Should fall back to a default location
        assert isinstance(result, Path)


class TestLoadEmailGroups:
    """Tests for load_email_groups function."""

    def test_load_valid_groups(self, tmp_path):
        """Test loading valid email groups from JSON."""
        groups_file = tmp_path / "email-groups.json"
        groups_data = {
            "team": ["alice@example.com", "bob@example.com"],
            "managers": ["manager@example.com"],
        }
        groups_file.write_text(json.dumps(groups_data))

        result = load_email_groups(groups_file)
        assert result == groups_data
        assert "team" in result
        assert len(result["team"]) == 2

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file returns empty dict."""
        result = load_email_groups(Path("/nonexistent/path.json"))
        assert result == {}

    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON returns empty dict."""
        groups_file = tmp_path / "invalid.json"
        groups_file.write_text("not valid json {")

        result = load_email_groups(groups_file)
        assert result == {}


class TestExpandEmailGroups:
    """Tests for expand_email_groups function."""

    def test_expand_single_group(self):
        """Test expanding single group."""
        groups = {"team": ["alice@example.com", "bob@example.com"]}
        emails = ["#team"]

        result = expand_email_groups(emails, groups)
        assert result == ["alice@example.com", "bob@example.com"]

    def test_expand_multiple_groups(self):
        """Test expanding multiple groups."""
        groups = {
            "team": ["alice@example.com", "bob@example.com"],
            "managers": ["manager@example.com"],
        }
        emails = ["#team", "#managers"]

        result = expand_email_groups(emails, groups)
        assert len(result) == 3
        assert "alice@example.com" in result
        assert "manager@example.com" in result

    def test_expand_mixed_emails_and_groups(self):
        """Test expanding mix of emails and groups."""
        groups = {"team": ["alice@example.com"]}
        emails = ["direct@example.com", "#team", "another@example.com"]

        result = expand_email_groups(emails, groups)
        assert len(result) == 3
        assert "direct@example.com" in result
        assert "alice@example.com" in result
        assert "another@example.com" in result

    def test_expand_nonexistent_group(self):
        """Test expanding nonexistent group preserves the string."""
        groups = {"team": ["alice@example.com"]}
        emails = ["#nonexistent"]

        result = expand_email_groups(emails, groups)
        assert result == ["#nonexistent"]

    def test_expand_with_empty_groups(self):
        """Test expanding with no groups defined."""
        emails = ["regular@example.com"]
        result = expand_email_groups(emails, {})
        assert result == ["regular@example.com"]

    def test_expand_removes_duplicates(self):
        """Test that expansion removes duplicate emails."""
        groups = {
            "team1": ["alice@example.com", "bob@example.com"],
            "team2": ["bob@example.com", "charlie@example.com"],
        }
        emails = ["#team1", "#team2"]

        result = expand_email_groups(emails, groups)
        assert len(result) == 3  # alice, bob (once), charlie


class TestCLICommands:
    """Tests for CLI command handling."""

    @patch("gmaillm.cli.GmailClient")
    def test_verify_command_success(self, mock_client_class):
        """Test verify command with successful setup."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "success": True,
            "email": "user@gmail.com",
            "total_messages": 1000,
            "total_threads": 500,
        }
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "verify"]):
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_called_with(0)

    @patch("gmaillm.cli.GmailClient")
    def test_verify_command_failure(self, mock_client_class):
        """Test verify command with failed setup."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "success": False,
            "error": "Authentication failed",
        }
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "verify"]):
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_called_with(1)

    @patch("gmaillm.cli.GmailClient")
    def test_status_command(self, mock_client_class):
        """Test status command."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "success": True,
            "email": "user@gmail.com",
            "total_messages": 1000,
            "total_threads": 500,
        }
        mock_client.get_folders.return_value = [
            Mock(name="INBOX", unread_count=5, message_count=100),
        ]
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "status"]):
            with patch("sys.exit"):
                main()

    @patch("gmaillm.cli.GmailClient")
    def test_list_command(self, mock_client_class):
        """Test list command."""
        mock_client = Mock()
        mock_email = EmailSummary(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com", name="Sender"),
            subject="Test Email",
            date=datetime(2025, 1, 15, 10, 30),
            snippet="Email content...",
        )
        mock_client.list_emails.return_value = [mock_email]
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "list", "--folder", "INBOX", "--limit", "10"]):
            with patch("sys.exit"):
                main()

        # Verify list_emails was called with correct args
        mock_client.list_emails.assert_called_once()

    @patch("gmaillm.cli.GmailClient")
    def test_read_command(self, mock_client_class):
        """Test read command."""
        mock_client = Mock()
        mock_email = Mock()
        mock_email.to_markdown.return_value = "# Email Content"
        mock_client.read_email.return_value = mock_email
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "read", "msg123"]):
            with patch("sys.exit"):
                main()

        mock_client.read_email.assert_called_once_with("msg123", format="summary")

    @patch("gmaillm.cli.GmailClient")
    def test_search_command(self, mock_client_class):
        """Test search command."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.to_markdown.return_value = "# Search Results"
        mock_client.search_emails.return_value = mock_result
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "search", "from:sender@example.com"]):
            with patch("sys.exit"):
                main()

        mock_client.search_emails.assert_called_once()

    @patch("gmaillm.cli.GmailClient")
    @patch("builtins.input")
    def test_send_command_with_confirmation(self, mock_input, mock_client_class):
        """Test send command with user confirmation."""
        mock_input.return_value = "yes"
        mock_client = Mock()
        mock_response = Mock(success=True)
        mock_response.to_markdown.return_value = "✅ Sent"
        mock_client.send_email.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "send",
            "--to", "recipient@example.com",
            "--subject", "Test",
            "--body", "Body text",
        ]):
            with patch("sys.exit"):
                main()

        mock_client.send_email.assert_called_once()

    @patch("gmaillm.cli.GmailClient")
    @patch("builtins.input")
    def test_send_command_cancelled(self, mock_input, mock_client_class):
        """Test send command cancelled by user."""
        mock_input.return_value = "no"
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "send",
            "--to", "recipient@example.com",
            "--subject", "Test",
            "--body", "Body",
        ]):
            with patch("sys.exit"):
                main()

        # Should not call send_email
        mock_client.send_email.assert_not_called()

    @patch("gmaillm.cli.GmailClient")
    def test_send_command_with_yolo(self, mock_client_class):
        """Test send command with --yolo flag (no confirmation)."""
        mock_client = Mock()
        mock_response = Mock(success=True)
        mock_response.to_markdown.return_value = "✅ Sent"
        mock_client.send_email.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "send",
            "--to", "recipient@example.com",
            "--subject", "Test",
            "--body", "Body",
            "--yolo",
        ]):
            with patch("sys.exit"):
                main()

        mock_client.send_email.assert_called_once()

    @patch("gmaillm.cli.GmailClient")
    @patch("builtins.input")
    def test_reply_command(self, mock_input, mock_client_class):
        """Test reply command."""
        mock_input.return_value = "yes"
        mock_client = Mock()
        mock_response = Mock(success=True)
        mock_response.to_markdown.return_value = "✅ Sent"
        mock_client.reply_email.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "reply",
            "msg123",
            "--body", "Reply text",
        ]):
            with patch("sys.exit"):
                main()

        mock_client.reply_email.assert_called_once()

    @patch("gmaillm.cli.GmailClient")
    def test_thread_command(self, mock_client_class):
        """Test thread command."""
        mock_client = Mock()
        mock_email = Mock()
        mock_email.to_markdown.return_value = "# Email 1"
        mock_client.get_thread.return_value = [mock_email]
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "thread", "thread123"]):
            with patch("sys.exit"):
                main()

        mock_client.get_thread.assert_called_once_with("thread123")

    @patch("gmaillm.cli.GmailClient")
    def test_folders_command(self, mock_client_class):
        """Test folders command."""
        mock_client = Mock()
        mock_folder = Mock()
        mock_folder.to_markdown.return_value = "- **INBOX**"
        mock_client.get_folders.return_value = [mock_folder]
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "folders"]):
            with patch("sys.exit"):
                main()

        mock_client.get_folders.assert_called_once()

    @patch("gmaillm.cli.get_plugin_config_dir")
    @patch("subprocess.run")
    def test_config_edit_style(self, mock_subprocess, mock_config_dir, tmp_path):
        """Test config edit-style command."""
        mock_config_dir.return_value = tmp_path
        style_file = tmp_path / "email-style.md"
        style_file.write_text("# Email Style")

        with patch("sys.argv", ["gmail", "config", "edit-style"]):
            with patch("sys.exit"):
                main()

        # Verify editor was called
        mock_subprocess.assert_called_once()

    @patch("gmaillm.cli.get_plugin_config_dir")
    @patch("subprocess.run")
    def test_config_edit_groups(self, mock_subprocess, mock_config_dir, tmp_path):
        """Test config edit-groups command."""
        mock_config_dir.return_value = tmp_path
        groups_file = tmp_path / "email-groups.json"
        groups_file.write_text("{}")

        with patch("sys.argv", ["gmail", "config", "edit-groups"]):
            with patch("sys.exit"):
                main()

        mock_subprocess.assert_called_once()

    @patch("gmaillm.cli.get_plugin_config_dir")
    def test_config_list_groups(self, mock_config_dir, tmp_path):
        """Test config list-groups command."""
        mock_config_dir.return_value = tmp_path
        groups_file = tmp_path / "email-groups.json"
        groups_data = {
            "team": ["alice@example.com", "bob@example.com"],
        }
        groups_file.write_text(json.dumps(groups_data))

        with patch("sys.argv", ["gmail", "config", "list-groups"]):
            with patch("sys.exit"):
                main()

    @patch("gmaillm.cli.get_plugin_config_dir")
    def test_config_show(self, mock_config_dir, tmp_path):
        """Test config show command."""
        mock_config_dir.return_value = tmp_path

        with patch("sys.argv", ["gmail", "config", "show"]):
            with patch("sys.exit"):
                main()

    def test_send_command_with_group_expansion(self):
        """Test send command expands email groups."""
        groups = {"team": ["alice@example.com", "bob@example.com"]}

        with patch("gmaillm.cli.load_email_groups", return_value=groups):
            result = expand_email_groups(["#team"], groups)
            assert len(result) == 2
            assert "alice@example.com" in result


class TestArgumentParsing:
    """Tests for argument parsing."""

    def test_no_args_shows_help(self):
        """Test running without arguments shows help."""
        with patch("sys.argv", ["gmail"]):
            with pytest.raises(SystemExit):
                main()

    def test_invalid_command(self):
        """Test invalid command raises error."""
        with patch("sys.argv", ["gmail", "invalid-command"]):
            with pytest.raises(SystemExit):
                main()
