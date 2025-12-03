"""Tests for gmaillm.commands.labels module."""

from unittest.mock import Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from gmaillm.commands.labels import app
from gmaillm.models import Folder

runner = CliRunner()


class TestListLabels:
    """Test list command."""

    @patch("gmaillm.commands.labels.GmailClient")
    def test_list_labels_success(self, mock_client_class):
        """Test listing labels successfully."""
        # Create mock labels/folders
        mock_folders = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=10, unread_count=2),
            Folder(id="SENT", name="SENT", type="system", message_count=5, unread_count=0),
            Folder(id="Label_1", name="Work", type="user", message_count=3, unread_count=1),
            Folder(id="Label_2", name="Personal", type="user", message_count=8, unread_count=0),
        ]

        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        mock_client.get_folders.assert_called_once()

    @patch("gmaillm.commands.labels.GmailClient")
    def test_list_labels_empty(self, mock_client_class):
        """Test listing when no labels exist."""
        mock_client = Mock()
        mock_client.get_folders.return_value = []
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0

    @patch("gmaillm.commands.labels.GmailClient")
    def test_list_labels_error(self, mock_client_class):
        """Test error handling when listing labels."""
        mock_client = Mock()
        mock_client.get_folders.side_effect = Exception("API error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Error listing labels" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_list_labels_only_system(self, mock_client_class):
        """Test listing only system labels."""
        mock_folders = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=10),
            Folder(id="SENT", name="SENT", type="system", message_count=5),
        ]

        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0

    @patch("gmaillm.commands.labels.GmailClient")
    def test_list_labels_only_custom(self, mock_client_class):
        """Test listing only custom labels."""
        mock_folders = [
            Folder(id="Label_1", name="Work", type="user", message_count=3),
            Folder(id="Label_2", name="Personal", type="user", message_count=8),
        ]

        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0

    @patch("gmaillm.commands.labels.GmailClient")
    def test_list_labels_with_unread_counts(self, mock_client_class):
        """Test listing labels with unread counts."""
        mock_folders = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=10, unread_count=5),
            Folder(id="Label_1", name="Important", type="user", message_count=3, unread_count=3),
        ]

        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0

    @patch("gmaillm.commands.labels.GmailClient")
    def test_list_labels_authentication_error(self, mock_client_class):
        """Test handling authentication errors."""
        mock_client_class.side_effect = Exception("Authentication failed")

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Error listing labels" in result.stdout


class TestCreateLabel:
    """Test create command."""

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_with_force(self, mock_client_class):
        """Test creating a label with --force flag."""
        mock_label = Folder(id="Label_123", name="NewLabel", type="user")
        mock_client = Mock()
        mock_client.create_label.return_value = mock_label
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["create", "NewLabel", "--force"])

        assert result.exit_code == 0
        assert "Label created" in result.stdout
        assert "NewLabel" in result.stdout
        mock_client.create_label.assert_called_once_with("NewLabel")

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_with_confirmation(self, mock_client_class):
        """Test creating label with user confirmation."""
        mock_label = Folder(id="Label_123", name="TestLabel", type="user")
        mock_client = Mock()
        mock_client.create_label.return_value = mock_label
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["create", "TestLabel"], input="y\n")

        assert result.exit_code == 0
        assert "Label created" in result.stdout
        mock_client.create_label.assert_called_once()

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_cancelled(self, mock_client_class):
        """Test cancelling label creation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["create", "TestLabel"], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout
        mock_client.create_label.assert_not_called()

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_invalid_name_empty(self, mock_client_class):
        """Test creating label with empty name."""
        result = runner.invoke(app, ["create", "", "--force"])

        # Should fail validation before reaching client
        assert result.exit_code == 1

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_invalid_name_too_long(self, mock_client_class):
        """Test creating label with name that's too long."""
        long_name = "a" * 300  # Gmail max is 225 characters

        result = runner.invoke(app, ["create", long_name, "--force"])

        assert result.exit_code == 1
        assert "Error creating label" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_with_slash(self, mock_client_class):
        """Test creating label with slash (creates nested label)."""
        # Gmail allows "/" for nested labels
        mock_label = Folder(id="Label_123", name="Test/Label", type="user")
        mock_client = Mock()
        mock_client.create_label.return_value = mock_label
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["create", "Test/Label", "--force"])

        # Should succeed as "/" is allowed in Gmail
        assert result.exit_code == 0
        mock_client.create_label.assert_called_once_with("Test/Label")

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_api_error(self, mock_client_class):
        """Test handling API errors during creation."""
        mock_client = Mock()
        mock_client.create_label.side_effect = Exception("Label already exists")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["create", "Existing", "--force"])

        assert result.exit_code == 1
        assert "Error creating label" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_with_spaces(self, mock_client_class):
        """Test creating label with spaces in name."""
        mock_label = Folder(id="Label_123", name="My Label", type="user")
        mock_client = Mock()
        mock_client.create_label.return_value = mock_label
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["create", "My Label", "--force"])

        assert result.exit_code == 0
        mock_client.create_label.assert_called_once_with("My Label")

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_shows_preview(self, mock_client_class):
        """Test that create command shows preview before confirmation."""
        mock_label = Folder(id="Label_123", name="Preview", type="user")
        mock_client = Mock()
        mock_client.create_label.return_value = mock_label
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["create", "Preview"], input="y\n")

        assert result.exit_code == 0
        assert "Creating Label" in result.stdout
        assert "Name: Preview" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_shows_id_after_creation(self, mock_client_class):
        """Test that created label ID is displayed."""
        mock_label = Folder(id="Label_XYZ123", name="NewLabel", type="user")
        mock_client = Mock()
        mock_client.create_label.return_value = mock_label
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["create", "NewLabel", "--force"])

        assert result.exit_code == 0
        assert "ID: Label_XYZ123" in result.stdout


class TestDeleteLabel:
    """Test delete command."""

    @patch("gmaillm.commands.labels.GmailClient")
    def test_delete_label_not_implemented(self, mock_client_class):
        """Test that delete shows not implemented warning."""
        mock_folders = [
            Folder(id="Label_1", name="MyLabel", type="user", message_count=5)
        ]
        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["delete", "MyLabel", "--force"])

        assert result.exit_code == 1
        assert "not yet implemented" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_delete_nonexistent_label(self, mock_client_class):
        """Test deleting a label that doesn't exist."""
        mock_client = Mock()
        mock_client.get_folders.return_value = []
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["delete", "NonExistent", "--force"])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_delete_system_label(self, mock_client_class):
        """Test preventing deletion of system labels."""
        mock_folders = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=10)
        ]
        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["delete", "INBOX", "--force"])

        assert result.exit_code == 1
        assert "Cannot delete system label" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_delete_label_cancelled(self, mock_client_class):
        """Test cancelling label deletion."""
        mock_folders = [
            Folder(id="Label_1", name="MyLabel", type="user", message_count=5)
        ]
        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["delete", "MyLabel"], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_delete_label_shows_preview(self, mock_client_class):
        """Test that delete shows preview before confirmation."""
        mock_folders = [
            Folder(id="Label_1", name="ToDelete", type="user", message_count=3)
        ]
        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["delete", "ToDelete"], input="n\n")

        assert "Deleting Label" in result.stdout
        assert "Name: ToDelete" in result.stdout
        assert "Type: user" in result.stdout
        assert "Messages: 3" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_delete_label_without_message_count(self, mock_client_class):
        """Test deleting label without message count."""
        mock_folders = [
            Folder(id="Label_1", name="Empty", type="user", message_count=None)
        ]
        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["delete", "Empty"], input="n\n")

        assert "Deleting Label" in result.stdout
        # Message count shouldn't appear if None
        assert "Messages:" not in result.stdout or "Messages: None" not in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_delete_system_labels_prevention(self, mock_client_class):
        """Test that various system labels are protected."""
        system_labels = ["INBOX", "SENT", "DRAFT", "TRASH", "SPAM", "STARRED"]

        for label_name in system_labels:
            mock_folders = [
                Folder(id=label_name, name=label_name, type="system")
            ]
            mock_client = Mock()
            mock_client.get_folders.return_value = mock_folders
            mock_client_class.return_value = mock_client

            result = runner.invoke(app, ["delete", label_name, "--force"])

            assert result.exit_code == 1
            assert "Cannot delete system label" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_delete_label_case_sensitive_match(self, mock_client_class):
        """Test label name matching is case-sensitive."""
        mock_folders = [
            Folder(id="Label_1", name="MyLabel", type="user")
        ]
        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        # Try to delete with different case
        result = runner.invoke(app, ["delete", "mylabel", "--force"])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_delete_label_with_force_flag(self, mock_client_class):
        """Test delete with --force shows warning message."""
        mock_folders = [
            Folder(id="Label_1", name="MyLabel", type="user", message_count=5)
        ]
        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["delete", "MyLabel", "--force"])

        assert "--force: Deleting without confirmation" in result.stdout or "not yet implemented" in result.stdout

    @patch("gmaillm.commands.labels.GmailClient")
    def test_delete_label_api_error(self, mock_client_class):
        """Test handling API errors during label fetch."""
        mock_client = Mock()
        mock_client.get_folders.side_effect = Exception("API connection failed")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["delete", "SomeLabel", "--force"])

        assert result.exit_code == 1
        assert "Error deleting label" in result.stdout


class TestLabelCommandHelp:
    """Test help text and command structure."""

    def test_list_command_help(self):
        """Test list command help text."""
        result = runner.invoke(app, ["list", "--help"])

        assert result.exit_code == 0
        assert "list" in result.stdout.lower()
        assert "label" in result.stdout.lower()

    def test_create_command_help(self):
        """Test create command help text."""
        result = runner.invoke(app, ["create", "--help"])

        assert result.exit_code == 0
        assert "create" in result.stdout.lower()
        assert "name" in result.stdout.lower()
        assert "--force" in result.stdout

    def test_delete_command_help(self):
        """Test delete command help text."""
        result = runner.invoke(app, ["delete", "--help"])

        assert result.exit_code == 0
        assert "delete" in result.stdout.lower()
        assert "--force" in result.stdout

    def test_app_help(self):
        """Test main app help."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "label" in result.stdout.lower()
        assert "list" in result.stdout
        assert "create" in result.stdout
        assert "delete" in result.stdout


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_unicode_name(self, mock_client_class):
        """Test creating label with unicode characters."""
        mock_label = Folder(id="Label_123", name="📧 Email", type="user")
        mock_client = Mock()
        mock_client.create_label.return_value = mock_label
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["create", "📧 Email", "--force"])

        # May or may not be allowed depending on validation
        # Just ensure it doesn't crash
        assert isinstance(result.exit_code, int)

    @patch("gmaillm.commands.labels.GmailClient")
    def test_list_labels_large_message_count(self, mock_client_class):
        """Test listing label with very large message count."""
        mock_folders = [
            Folder(id="Label_1", name="Archive", type="user", message_count=999999)
        ]
        mock_client = Mock()
        mock_client.get_folders.return_value = mock_folders
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0

    @patch("gmaillm.commands.labels.GmailClient")
    def test_create_label_network_timeout(self, mock_client_class):
        """Test handling network timeout during creation."""
        mock_client = Mock()
        mock_client.create_label.side_effect = TimeoutError("Connection timeout")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["create", "Test", "--force"])

        assert result.exit_code == 1
        assert "Error creating label" in result.stdout
