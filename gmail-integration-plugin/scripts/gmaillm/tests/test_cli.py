"""Tests for cli.py module."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from gmaillm.cli import (
    expand_email_groups,
    load_email_groups,
    main,
)
from gmaillm.helpers.config import get_plugin_config_dir
from gmaillm.models import EmailAddress, EmailSummary


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
        # Updated to match new verify_setup return format
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@gmail.com",
            "folders": 10,
            "inbox_accessible": True,
            "errors": [],
        }
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "verify"]):
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_called_with(0)

    @patch("gmaillm.cli.GmailClient")
    def test_verify_command_failure(self, mock_client_class):
        """Test verify command with failed setup."""
        # verify command only exits with 1 if an exception is raised, not for setup errors
        mock_client_class.side_effect = Exception("Authentication failed")

        with patch("sys.argv", ["gmail", "verify"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @patch("gmaillm.cli.GmailClient")
    def test_status_command(self, mock_client_class):
        """Test status command."""
        mock_client = Mock()
        # Updated to match new verify_setup return format
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@gmail.com",
            "folders": 10,
            "inbox_accessible": True,
            "errors": [],
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
        from gmaillm.models import SearchResult

        mock_client = Mock()
        mock_email = EmailSummary(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com", name="Sender"),
            subject="Test Email",
            date=datetime(2025, 1, 15, 10, 30),
            snippet="Email content...",
        )
        # list_emails now returns SearchResult, not a list
        mock_result = SearchResult(
            emails=[mock_email],
            total_count=1,
            query="label:INBOX",
        )
        mock_client.list_emails.return_value = mock_result
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "list", "--folder", "INBOX", "--max", "10"]):
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
    def test_read_command_summary_with_rich_format(self, mock_client_class):
        """Test read command with summary format and rich output.

        This tests the bug where reading an email without --full flag
        returns EmailSummary but the formatter expects EmailFull.

        Bug: cli.py line 883 always calls formatter.print_email_full(email)
        even when email is an EmailSummary (which lacks 'to', 'cc', body fields).
        """
        from gmaillm.models import EmailAddress, EmailSummary

        mock_client = Mock()

        # Create a realistic EmailSummary (what's actually returned)
        email_summary = EmailSummary(
            message_id="19a2d480463360ec",
            thread_id="19a2d480463360ec",
            from_=EmailAddress(email="sender@example.com", name="Test Sender"),
            subject="Test Subject",
            date=datetime(2025, 10, 28, 10, 30, 0),
            snippet="This is a test email snippet...",
            labels=["INBOX", "UNREAD"],
            has_attachments=False,
            is_unread=True,
        )

        mock_client.read_email.return_value = email_summary
        mock_client_class.return_value = mock_client

        # Without --full flag, default format is "rich" which calls formatter.print_email_full()
        # This should fail because EmailSummary doesn't have 'to' attribute
        # The error is caught and exits with code 1
        with patch("sys.argv", ["gmail", "read", "19a2d480463360ec"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        mock_client.read_email.assert_called_once_with("19a2d480463360ec", format="summary")

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
    @patch("typer.confirm")
    def test_send_command_with_confirmation(self, mock_confirm, mock_client_class):
        """Test send command with user confirmation."""
        mock_confirm.return_value = True
        mock_client = Mock()
        mock_response = Mock(success=True, message_id="msg123")
        mock_response.to_markdown.return_value = "✅ Sent"
        mock_client.send_email.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch(
            "sys.argv",
            [
                "gmail",
                "send",
                "--to",
                "recipient@example.com",
                "--subject",
                "Test",
                "--body",
                "Body text",
            ],
        ):
            with patch("sys.exit"):
                main()

        mock_client.send_email.assert_called_once()

    @patch("gmaillm.cli.GmailClient")
    @patch("typer.confirm")
    def test_send_command_cancelled(self, mock_confirm, mock_client_class):
        """Test send command cancelled by user."""
        mock_confirm.return_value = False
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        with patch(
            "sys.argv",
            [
                "gmail",
                "send",
                "--to",
                "recipient@example.com",
                "--subject",
                "Test",
                "--body",
                "Body",
            ],
        ):
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

        with patch(
            "sys.argv",
            [
                "gmail",
                "send",
                "--to",
                "recipient@example.com",
                "--subject",
                "Test",
                "--body",
                "Body",
                "--yolo",
            ],
        ):
            with patch("sys.exit"):
                main()

        mock_client.send_email.assert_called_once()

    @patch("gmaillm.cli.GmailClient")
    @patch("typer.confirm")
    def test_reply_command(self, mock_confirm, mock_client_class):
        """Test reply command."""
        mock_confirm.return_value = True
        mock_client = Mock()

        # Mock the read_email call that reply command uses to get original message
        mock_original = Mock()
        mock_original.from_.email = "original@example.com"
        mock_original.subject = "Original Subject"
        mock_client.read_email.return_value = mock_original

        mock_response = Mock(success=True, message_id="reply123")
        mock_response.to_markdown.return_value = "✅ Sent"
        mock_client.reply_email.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch(
            "sys.argv",
            [
                "gmail",
                "reply",
                "msg123",
                "--body",
                "Reply text",
            ],
        ):
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

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
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

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
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

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
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

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
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


class TestStylesCommands:
    """Tests for styles management commands."""

    # Valid style template for testing
    VALID_STYLE = """---
name: "Test Style"
description: "When to use: Test context. Test characteristics."
---

<examples>
Example email 1
---
Example email 2
</examples>

<greeting>
- "Hi [Name],"
- "Hello [Name],"
</greeting>

<body>
- Clear sentences
- Active voice
</body>

<closing>
- "Best,"
- "Thanks,"
</closing>

<do>
- Be clear
- Be concise
</do>

<dont>
- Be vague
- Be verbose
</dont>
"""

    # Invalid style - missing section
    INVALID_STYLE_MISSING_SECTION = """---
name: "Invalid"
description: "When to use: Missing sections."
---

<examples>
Example
</examples>

<greeting>
- "Hi,"
</greeting>
"""

    # Invalid style - wrong order
    INVALID_STYLE_WRONG_ORDER = """---
name: "Invalid Order"
description: "When to use: Sections out of order."
---

<greeting>
- "Hi,"
</greeting>

<examples>
Example
</examples>

<body>
- Body
</body>

<closing>
- "Best,"
</closing>

<do>
- Do this
</do>

<dont>
- Don't that
</dont>
"""

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_list(self, mock_config_dir, tmp_path):
        """Test listing all styles."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        # Create test styles
        (styles_dir / "formal.md").write_text(self.VALID_STYLE)
        (styles_dir / "casual.md").write_text(self.VALID_STYLE)

        with patch("sys.argv", ["gmail", "styles", "list"]):
            with patch("sys.exit"):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_list_empty(self, mock_config_dir, tmp_path):
        """Test listing styles when directory is empty."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        with patch("sys.argv", ["gmail", "styles", "list"]):
            with patch("sys.exit"):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_show(self, mock_config_dir, tmp_path):
        """Test showing specific style."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        style_file = styles_dir / "formal.md"
        style_file.write_text(self.VALID_STYLE)

        with patch("sys.argv", ["gmail", "styles", "show", "formal"]):
            with patch("sys.exit"):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_show_not_found(self, mock_config_dir, tmp_path):
        """Test showing non-existent style."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        with patch("sys.argv", ["gmail", "styles", "show", "nonexistent"]):
            with pytest.raises(SystemExit):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    @patch("typer.confirm")
    def test_styles_create(self, mock_confirm, mock_config_dir, tmp_path):
        """Test creating new style."""
        mock_confirm.return_value = True
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        with patch("sys.argv", ["gmail", "styles", "create", "new-style"]):
            with patch("sys.exit"):
                main()

        # Verify file was created
        assert (styles_dir / "new-style.md").exists()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    @patch("typer.confirm")
    def test_styles_create_cancelled(self, mock_confirm, mock_config_dir, tmp_path):
        """Test creating style cancelled by user."""
        mock_confirm.return_value = False
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        with patch("sys.argv", ["gmail", "styles", "create", "new-style"]):
            with patch("sys.exit"):
                main()

        # Verify file was not created
        assert not (styles_dir / "new-style.md").exists()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    @patch("typer.confirm")
    def test_styles_create_duplicate(self, mock_confirm, mock_config_dir, tmp_path):
        """Test creating style that already exists."""
        mock_confirm.return_value = True
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        # Create existing style
        (styles_dir / "existing.md").write_text(self.VALID_STYLE)

        with patch("sys.argv", ["gmail", "styles", "create", "existing"]):
            with pytest.raises(SystemExit):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_create_invalid_name(self, mock_config_dir, tmp_path):
        """Test creating style with invalid name."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        # Test with name containing spaces
        with patch("sys.argv", ["gmail", "styles", "create", "invalid name"]):
            with pytest.raises(SystemExit):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    @patch("typer.confirm")
    def test_styles_create_skip_validation(self, mock_confirm, mock_config_dir, tmp_path):
        """Test creating style with --skip-validation flag."""
        mock_confirm.return_value = True
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        with patch("sys.argv", ["gmail", "styles", "create", "new-style", "--skip-validation"]):
            with patch("sys.exit"):
                main()

        assert (styles_dir / "new-style.md").exists()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    @patch("subprocess.run")
    def test_styles_edit(self, mock_subprocess, mock_config_dir, tmp_path):
        """Test editing existing style."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        style_file = styles_dir / "formal.md"
        style_file.write_text(self.VALID_STYLE)

        with patch("sys.argv", ["gmail", "styles", "edit", "formal"]):
            with patch("sys.exit"):
                main()

        # Verify editor was called
        mock_subprocess.assert_called_once()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_edit_not_found(self, mock_config_dir, tmp_path):
        """Test editing non-existent style."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        with patch("sys.argv", ["gmail", "styles", "edit", "nonexistent"]):
            with pytest.raises(SystemExit):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    @patch("subprocess.run")
    def test_styles_edit_skip_validation(self, mock_subprocess, mock_config_dir, tmp_path):
        """Test editing style with --skip-validation flag."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        style_file = styles_dir / "formal.md"
        style_file.write_text(self.VALID_STYLE)

        with patch("sys.argv", ["gmail", "styles", "edit", "formal", "--skip-validation"]):
            with patch("sys.exit"):
                main()

        mock_subprocess.assert_called_once()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    @patch("typer.confirm")
    def test_styles_delete(self, mock_confirm, mock_config_dir, tmp_path):
        """Test deleting style with confirmation."""
        mock_confirm.return_value = True
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        style_file = styles_dir / "old-style.md"
        style_file.write_text(self.VALID_STYLE)

        with patch("sys.argv", ["gmail", "styles", "delete", "old-style"]):
            with patch("sys.exit"):
                main()

        # Verify file was deleted
        assert not style_file.exists()

        # Verify backup was created
        backups = list(styles_dir.glob("old-style.backup.*"))
        assert len(backups) == 1

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    @patch("typer.confirm")
    def test_styles_delete_cancelled(self, mock_confirm, mock_config_dir, tmp_path):
        """Test deleting style cancelled by user."""
        mock_confirm.return_value = False
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        style_file = styles_dir / "keep-style.md"
        style_file.write_text(self.VALID_STYLE)

        with patch("sys.argv", ["gmail", "styles", "delete", "keep-style"]):
            with patch("sys.exit"):
                main()

        # Verify file still exists
        assert style_file.exists()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_delete_force(self, mock_config_dir, tmp_path):
        """Test deleting style with --force flag."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        style_file = styles_dir / "old-style.md"
        style_file.write_text(self.VALID_STYLE)

        with patch("sys.argv", ["gmail", "styles", "delete", "old-style", "--force"]):
            with patch("sys.exit"):
                main()

        assert not style_file.exists()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_delete_not_found(self, mock_config_dir, tmp_path):
        """Test deleting non-existent style."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        with patch("sys.argv", ["gmail", "styles", "delete", "nonexistent"]):
            with pytest.raises(SystemExit):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_validate_valid(self, mock_config_dir, tmp_path):
        """Test validating valid style."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        style_file = styles_dir / "valid.md"
        style_file.write_text(self.VALID_STYLE)

        with patch("sys.argv", ["gmail", "styles", "validate", "valid"]):
            with patch("sys.exit"):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_validate_invalid(self, mock_config_dir, tmp_path):
        """Test validating invalid style."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        style_file = styles_dir / "invalid.md"
        style_file.write_text(self.INVALID_STYLE_MISSING_SECTION)

        with patch("sys.argv", ["gmail", "styles", "validate", "invalid"]):
            with pytest.raises(SystemExit):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_validate_fix(self, mock_config_dir, tmp_path):
        """Test validating and auto-fixing style."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        # Style with trailing whitespace
        style_with_whitespace = self.VALID_STYLE + "   \n"
        style_file = styles_dir / "fixable.md"
        style_file.write_text(style_with_whitespace)

        with patch("sys.argv", ["gmail", "styles", "validate", "fixable", "--fix"]):
            with patch("sys.exit"):
                main()

        # Verify whitespace was removed
        fixed_content = style_file.read_text()
        assert not any(line.endswith("   ") for line in fixed_content.split('\n'))

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_validate_not_found(self, mock_config_dir, tmp_path):
        """Test validating non-existent style."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        with patch("sys.argv", ["gmail", "styles", "validate", "nonexistent"]):
            with pytest.raises(SystemExit):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_validate_all(self, mock_config_dir, tmp_path):
        """Test validating all styles."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        # Create mix of valid and invalid styles
        (styles_dir / "valid1.md").write_text(self.VALID_STYLE)
        (styles_dir / "valid2.md").write_text(self.VALID_STYLE)

        with patch("sys.argv", ["gmail", "styles", "validate-all"]):
            with patch("sys.exit"):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_validate_all_with_invalid(self, mock_config_dir, tmp_path):
        """Test validating all styles when some are invalid."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        (styles_dir / "valid.md").write_text(self.VALID_STYLE)
        (styles_dir / "invalid.md").write_text(self.INVALID_STYLE_MISSING_SECTION)

        with patch("sys.argv", ["gmail", "styles", "validate-all"]):
            with pytest.raises(SystemExit):
                main()

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_validate_all_fix(self, mock_config_dir, tmp_path):
        """Test validating and fixing all styles."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        # Styles with trailing whitespace
        style_with_whitespace = self.VALID_STYLE + "   \n"
        (styles_dir / "style1.md").write_text(style_with_whitespace)
        (styles_dir / "style2.md").write_text(style_with_whitespace)

        with patch("sys.argv", ["gmail", "styles", "validate-all", "--fix"]):
            with patch("sys.exit"):
                main()

        # Verify all files were fixed - check for lines with 3+ spaces at end
        for style_file in styles_dir.glob("*.md"):
            content = style_file.read_text()
            lines = content.split('\n')
            # Check no lines have 3 or more trailing spaces
            assert not any(len(line) - len(line.rstrip()) >= 3 for line in lines)

    @patch("gmaillm.helpers.config.get_plugin_config_dir")
    def test_styles_validate_all_empty(self, mock_config_dir, tmp_path):
        """Test validating all styles when directory is empty."""
        mock_config_dir.return_value = tmp_path
        styles_dir = tmp_path / "email-styles"
        styles_dir.mkdir()

        with patch("sys.argv", ["gmail", "styles", "validate-all"]):
            with patch("sys.exit"):
                main()


class TestStyleLinter:
    """Tests for StyleLinter class."""

    def test_valid_style(self):
        """Test linting valid style."""
        from gmaillm.validators.styles import StyleLinter

        valid_style = TestStylesCommands.VALID_STYLE
        linter = StyleLinter()
        errors = linter.lint(valid_style)

        assert len(errors) == 0

    def test_missing_frontmatter(self):
        """Test style missing YAML frontmatter."""
        from gmaillm.validators.styles import StyleLinter

        invalid_style = "<examples>Test</examples>"
        linter = StyleLinter()
        errors = linter.lint(invalid_style)

        assert any("frontmatter" in err.section for err in errors)

    def test_missing_section(self):
        """Test style missing required section."""
        from gmaillm.validators.styles import StyleLinter

        invalid_style = """---
name: "Test"
description: "When to use: Test."
---

<examples>Test</examples>
"""
        linter = StyleLinter()
        errors = linter.lint(invalid_style)

        # Should have errors for missing sections
        assert len(errors) > 0

    def test_sections_wrong_order(self):
        """Test style with sections in wrong order."""
        from gmaillm.validators.styles import StyleLinter

        linter = StyleLinter()
        errors = linter.lint(TestStylesCommands.INVALID_STYLE_WRONG_ORDER)

        assert any("out of order" in err.message for err in errors)

    def test_description_missing_when_to_use(self):
        """Test description not starting with 'When to use:'."""
        from gmaillm.validators.styles import StyleLinter

        invalid_style = """---
name: "Test"
description: "This is wrong format."
---

<examples>Test</examples>
<greeting>- Hi</greeting>
<body>- Body</body>
<closing>- Best</closing>
<do>- Do this</do>
<dont>- Don't that</dont>
"""
        linter = StyleLinter()
        errors = linter.lint(invalid_style)

        assert any("When to use:" in err.message for err in errors)

    def test_lint_and_fix_trailing_whitespace(self):
        """Test auto-fixing trailing whitespace."""
        from gmaillm.validators.styles import StyleLinter

        style_with_whitespace = TestStylesCommands.VALID_STYLE + "   \n"
        linter = StyleLinter()
        fixed_content, errors = linter.lint_and_fix(style_with_whitespace)

        # Verify whitespace was removed
        assert not any(line.endswith("   ") for line in fixed_content.split('\n'))

    def test_description_too_short(self):
        """Test description that is too short."""
        from gmaillm.validators.styles import StyleLinter

        invalid_style = """---
name: "Test"
description: "When to use: Short."
---

<examples>Test</examples>
<greeting>- Hi</greeting>
<body>- Body</body>
<closing>- Best</closing>
<do>- Do this</do>
<dont>- Don't that</dont>
"""
        linter = StyleLinter()
        errors = linter.lint(invalid_style)

        assert any("too short" in err.message.lower() for err in errors)

    def test_empty_section(self):
        """Test section with no content."""
        from gmaillm.validators.styles import StyleLinter

        invalid_style = """---
name: "Test"
description: "When to use: Test context. Test characteristics."
---

<examples></examples>
<greeting>- Hi</greeting>
<body>- Body</body>
<closing>- Best</closing>
<do>- Do this</do>
<dont>- Don't that</dont>
"""
        linter = StyleLinter()
        errors = linter.lint(invalid_style)

        assert any("empty" in err.message.lower() for err in errors)
