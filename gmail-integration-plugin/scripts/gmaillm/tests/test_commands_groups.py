"""Tests for gmaillm.commands.groups module."""

import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest
import typer
from typer.testing import CliRunner

from gmaillm.commands.groups import app

runner = CliRunner()


class TestListGroups:
    """Test list command."""

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_list_empty_groups(self, mock_load):
        """Test listing when no groups exist."""
        mock_load.return_value = {}

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "No groups found" in result.stdout
        assert "Create a group" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_list_single_group(self, mock_load):
        """Test listing a single group."""
        mock_load.return_value = {
            "team": ["alice@example.com", "bob@example.com"]
        }

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "#team" in result.stdout
        assert "2" in result.stdout  # Member count
        assert "Total: 1 group(s)" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_list_multiple_groups(self, mock_load):
        """Test listing multiple groups."""
        mock_load.return_value = {
            "team": ["alice@example.com"],
            "clients": ["client1@example.com", "client2@example.com"],
            "partners": ["partner@example.com"]
        }

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "#team" in result.stdout
        assert "#clients" in result.stdout
        assert "#partners" in result.stdout
        assert "Total: 3 group(s)" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_list_group_with_many_members(self, mock_load):
        """Test listing group with >2 members shows truncation."""
        mock_load.return_value = {
            "large": [
                "user1@example.com",
                "user2@example.com",
                "user3@example.com",
                "user4@example.com"
            ]
        }

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "..." in result.stdout
        assert "2 more" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_list_handles_error(self, mock_load):
        """Test error handling in list command."""
        mock_load.side_effect = Exception("File not found")

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Error listing groups" in result.stdout


class TestShowGroup:
    """Test show command."""

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_show_existing_group(self, mock_load):
        """Test showing an existing group."""
        mock_load.return_value = {
            "team": ["alice@example.com", "bob@example.com", "charlie@example.com"]
        }

        result = runner.invoke(app, ["show", "team"])

        assert result.exit_code == 0
        assert "Group: #team" in result.stdout
        assert "Members: 3" in result.stdout
        assert "alice@example.com" in result.stdout
        assert "bob@example.com" in result.stdout
        assert "charlie@example.com" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_show_nonexistent_group(self, mock_load):
        """Test showing a group that doesn't exist."""
        mock_load.return_value = {
            "team": ["alice@example.com"]
        }

        result = runner.invoke(app, ["show", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.stdout
        assert "Available groups" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_show_group_with_numbered_list(self, mock_load):
        """Test that emails are numbered in output."""
        mock_load.return_value = {
            "team": ["first@example.com", "second@example.com"]
        }

        result = runner.invoke(app, ["show", "team"])

        assert result.exit_code == 0
        assert "1. first@example.com" in result.stdout
        assert "2. second@example.com" in result.stdout


class TestCreateGroup:
    """Test create command."""

    @patch("gmaillm.commands.groups.save_email_groups")
    @patch("gmaillm.commands.groups.load_email_groups")
    def test_create_new_group_with_force(self, mock_load, mock_save):
        """Test creating a new group with --force flag."""
        mock_load.return_value = {}

        result = runner.invoke(app, [
            "create", "team",
            "--emails", "alice@example.com",
            "--emails", "bob@example.com",
            "--force"
        ])

        assert result.exit_code == 0
        assert "Group created" in result.stdout
        assert "#team" in result.stdout

        # Verify save was called
        mock_save.assert_called_once()
        saved_groups = mock_save.call_args[0][0]
        assert "team" in saved_groups
        assert len(saved_groups["team"]) == 2

    @patch("gmaillm.commands.groups.save_email_groups")
    @patch("gmaillm.commands.groups.load_email_groups")
    def test_create_group_with_confirmation(self, mock_load, mock_save):
        """Test creating group with user confirmation."""
        mock_load.return_value = {}

        result = runner.invoke(app, [
            "create", "team",
            "--emails", "alice@example.com",
            "--emails", "bob@example.com"
        ], input="y\n")

        assert result.exit_code == 0
        assert "Group created" in result.stdout
        mock_save.assert_called_once()

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_create_group_cancelled(self, mock_load):
        """Test creating group and cancelling."""
        mock_load.return_value = {}

        result = runner.invoke(app, [
            "create", "team",
            "--emails", "alice@example.com"
        ], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_create_group_missing_name(self, mock_load):
        """Test creating group without name."""
        mock_load.return_value = {}

        result = runner.invoke(app, [
            "create",
            "--emails", "alice@example.com"
        ])

        assert result.exit_code == 1
        assert "required" in result.stdout.lower()

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_create_group_missing_emails(self, mock_load):
        """Test creating group without emails."""
        mock_load.return_value = {}

        result = runner.invoke(app, [
            "create", "team"
        ])

        assert result.exit_code == 1
        assert "email is required" in result.stdout.lower()

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_create_group_invalid_email(self, mock_load):
        """Test creating group with invalid email."""
        mock_load.return_value = {}

        result = runner.invoke(app, [
            "create", "team",
            "--emails", "invalid-email",
            "--force"
        ])

        assert result.exit_code == 1
        assert "Invalid email" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_create_duplicate_group_without_force(self, mock_load):
        """Test creating a group that already exists without --force."""
        mock_load.return_value = {
            "team": ["existing@example.com"]
        }

        result = runner.invoke(app, [
            "create", "team",
            "--emails", "new@example.com"
        ])

        assert result.exit_code == 1
        assert "already exists" in result.stdout
        assert "--force" in result.stdout

    @patch("gmaillm.commands.groups.save_email_groups")
    @patch("gmaillm.commands.groups.load_email_groups")
    def test_create_duplicate_group_with_force(self, mock_load, mock_save):
        """Test overwriting existing group with --force."""
        mock_load.return_value = {
            "team": ["old@example.com"]
        }

        result = runner.invoke(app, [
            "create", "team",
            "--emails", "new@example.com",
            "--force"
        ])

        assert result.exit_code == 0
        assert "Overwriting" in result.stdout
        assert "Group created" in result.stdout

        # Verify old group was replaced
        saved_groups = mock_save.call_args[0][0]
        assert saved_groups["team"] == ["new@example.com"]

    @patch("gmaillm.commands.groups.save_email_groups")
    @patch("gmaillm.commands.groups.load_email_groups")
    @patch("gmaillm.commands.groups.load_and_validate_json")
    def test_create_from_json_file(self, mock_load_validate_json, mock_load, mock_save):
        """Test creating group from JSON file."""
        mock_load.return_value = {}
        mock_load_validate_json.return_value = {
            "name": "team",
            "members": ["alice@example.com", "bob@example.com"]
        }

        result = runner.invoke(app, [
            "create",
            "--json-input", "group.json",
            "--force"
        ])

        assert result.exit_code == 0
        assert "Creating group from JSON" in result.stdout
        assert "Group created" in result.stdout

        saved_groups = mock_save.call_args[0][0]
        assert "team" in saved_groups
        assert len(saved_groups["team"]) == 2

    @patch("gmaillm.commands.groups.load_email_groups")
    @patch("gmaillm.commands.groups.load_and_validate_json")
    def test_create_from_json_file_not_found(self, mock_load_validate_json, mock_load):
        """Test creating from non-existent JSON file."""
        mock_load.return_value = {}
        mock_load_validate_json.side_effect = FileNotFoundError("File not found")

        result = runner.invoke(app, [
            "create",
            "--json-input", "nonexistent.json",
            "--force"
        ])

        assert result.exit_code == 1
        # Error message will vary depending on implementation
        assert result.exit_code == 1

    @patch("gmaillm.commands.groups.load_email_groups")
    @patch("gmaillm.commands.groups.load_and_validate_json")
    def test_create_from_invalid_json(self, mock_load_validate_json, mock_load):
        """Test creating from invalid JSON."""
        mock_load.return_value = {}
        mock_load_validate_json.side_effect = ValueError("Invalid JSON: Missing 'name' field")

        result = runner.invoke(app, [
            "create",
            "--json-input", "invalid.json",
            "--force"
        ])

        assert result.exit_code == 1
        # Error will be caught by exception handler
        assert result.exit_code == 1


class TestAddMember:
    """Test add command."""

    @patch("gmaillm.commands.groups.save_email_groups")
    @patch("gmaillm.commands.groups.load_email_groups")
    def test_add_member_to_existing_group(self, mock_load, mock_save):
        """Test adding a member to an existing group."""
        mock_load.return_value = {
            "team": ["alice@example.com"]
        }

        result = runner.invoke(app, [
            "add", "team", "bob@example.com"
        ])

        assert result.exit_code == 0
        assert "Added bob@example.com" in result.stdout
        assert "#team" in result.stdout

        saved_groups = mock_save.call_args[0][0]
        assert "bob@example.com" in saved_groups["team"]
        assert len(saved_groups["team"]) == 2

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_add_member_to_nonexistent_group(self, mock_load):
        """Test adding member to group that doesn't exist."""
        mock_load.return_value = {}

        result = runner.invoke(app, [
            "add", "nonexistent", "alice@example.com"
        ])

        assert result.exit_code == 1
        assert "not found" in result.stdout
        assert "Create it first" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_add_invalid_email(self, mock_load):
        """Test adding invalid email to group."""
        mock_load.return_value = {
            "team": ["alice@example.com"]
        }

        result = runner.invoke(app, [
            "add", "team", "invalid-email"
        ])

        assert result.exit_code == 1
        assert "Invalid email" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_add_duplicate_member(self, mock_load):
        """Test adding a member that's already in the group."""
        mock_load.return_value = {
            "team": ["alice@example.com"]
        }

        result = runner.invoke(app, [
            "add", "team", "alice@example.com"
        ])

        assert result.exit_code == 0
        assert "already in group" in result.stdout


class TestRemoveMember:
    """Test remove command."""

    @patch("gmaillm.commands.groups.save_email_groups")
    @patch("gmaillm.commands.groups.load_email_groups")
    def test_remove_member_from_group(self, mock_load, mock_save):
        """Test removing a member from a group."""
        mock_load.return_value = {
            "team": ["alice@example.com", "bob@example.com"]
        }

        result = runner.invoke(app, [
            "remove", "team", "alice@example.com"
        ])

        assert result.exit_code == 0
        assert "Removed alice@example.com" in result.stdout

        saved_groups = mock_save.call_args[0][0]
        assert "alice@example.com" not in saved_groups["team"]
        assert len(saved_groups["team"]) == 1

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_remove_member_from_nonexistent_group(self, mock_load):
        """Test removing member from nonexistent group."""
        mock_load.return_value = {}

        result = runner.invoke(app, [
            "remove", "nonexistent", "alice@example.com"
        ])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_remove_nonexistent_member(self, mock_load):
        """Test removing member that's not in the group."""
        mock_load.return_value = {
            "team": ["alice@example.com"]
        }

        result = runner.invoke(app, [
            "remove", "team", "bob@example.com"
        ])

        assert result.exit_code == 0
        assert "is not in group" in result.stdout

    @patch("gmaillm.commands.groups.save_email_groups")
    @patch("gmaillm.commands.groups.load_email_groups")
    def test_remove_last_member_delete_group(self, mock_load, mock_save):
        """Test removing last member and deleting empty group."""
        mock_load.return_value = {
            "team": ["alice@example.com"]
        }

        result = runner.invoke(app, [
            "remove", "team", "alice@example.com"
        ], input="y\n")

        assert result.exit_code == 0
        assert "Group #team is now empty" in result.stdout
        assert "deleted empty group" in result.stdout

        saved_groups = mock_save.call_args[0][0]
        assert "team" not in saved_groups

    @patch("gmaillm.commands.groups.save_email_groups")
    @patch("gmaillm.commands.groups.load_email_groups")
    def test_remove_last_member_keep_group(self, mock_load, mock_save):
        """Test removing last member but keeping empty group."""
        mock_load.return_value = {
            "team": ["alice@example.com"]
        }

        result = runner.invoke(app, [
            "remove", "team", "alice@example.com"
        ], input="n\n")

        assert result.exit_code == 0
        assert "Group #team is now empty" in result.stdout

        saved_groups = mock_save.call_args[0][0]
        assert "team" in saved_groups
        assert len(saved_groups["team"]) == 0


class TestDeleteGroup:
    """Test delete command."""

    @patch("gmaillm.commands.groups.create_backup")
    @patch("gmaillm.commands.groups.get_groups_file_path")
    @patch("gmaillm.commands.groups.save_email_groups")
    @patch("gmaillm.commands.groups.load_email_groups")
    def test_delete_group_with_confirmation(self, mock_load, mock_save, mock_get_path, mock_backup):
        """Test deleting a group with confirmation."""
        mock_load.return_value = {
            "team": ["alice@example.com", "bob@example.com"]
        }
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_get_path.return_value = mock_file
        mock_backup.return_value = Path("/backup/path")

        result = runner.invoke(app, [
            "delete", "team"
        ], input="y\n")

        assert result.exit_code == 0
        assert "Group deleted" in result.stdout
        assert "Backup created" in result.stdout

        saved_groups = mock_save.call_args[0][0]
        assert "team" not in saved_groups

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_delete_group_cancelled(self, mock_load):
        """Test cancelling group deletion."""
        mock_load.return_value = {
            "team": ["alice@example.com"]
        }

        result = runner.invoke(app, [
            "delete", "team"
        ], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout

    @patch("gmaillm.commands.groups.create_backup")
    @patch("gmaillm.commands.groups.get_groups_file_path")
    @patch("gmaillm.commands.groups.save_email_groups")
    @patch("gmaillm.commands.groups.load_email_groups")
    def test_delete_group_with_force(self, mock_load, mock_save, mock_get_path, mock_backup):
        """Test deleting group with --force flag."""
        mock_load.return_value = {
            "team": ["alice@example.com"]
        }
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_get_path.return_value = mock_file
        mock_backup.return_value = Path("/backup/path")

        result = runner.invoke(app, [
            "delete", "team", "--force"
        ])

        assert result.exit_code == 0
        assert "Deleting without confirmation" in result.stdout
        assert "Group deleted" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_delete_nonexistent_group(self, mock_load):
        """Test deleting a group that doesn't exist."""
        mock_load.return_value = {}

        result = runner.invoke(app, [
            "delete", "nonexistent", "--force"
        ])

        assert result.exit_code == 1
        assert "not found" in result.stdout


class TestValidateGroup:
    """Test validate command."""

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_validate_all_groups_valid(self, mock_load):
        """Test validating all groups when all are valid."""
        mock_load.return_value = {
            "team": ["alice@example.com", "bob@example.com"],
            "clients": ["client@example.com"]
        }

        result = runner.invoke(app, ["validate"])

        assert result.exit_code == 0
        assert "All groups are valid" in result.stdout
        assert "✅ #team" in result.stdout
        assert "✅ #clients" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_validate_single_group_valid(self, mock_load):
        """Test validating a single valid group."""
        mock_load.return_value = {
            "team": ["alice@example.com"]
        }

        result = runner.invoke(app, ["validate", "team"])

        assert result.exit_code == 0
        assert "Group #team is valid" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_validate_group_with_invalid_email(self, mock_load):
        """Test validating group with invalid email."""
        mock_load.return_value = {
            "team": ["alice@example.com", "invalid-email"]
        }

        result = runner.invoke(app, ["validate", "team"])

        assert result.exit_code == 1
        assert "✗ #team" in result.stdout
        assert "Invalid email: invalid-email" in result.stdout
        assert "Validation failed" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_validate_group_with_duplicates(self, mock_load):
        """Test validating group with duplicate emails."""
        mock_load.return_value = {
            "team": ["alice@example.com", "bob@example.com", "alice@example.com"]
        }

        result = runner.invoke(app, ["validate", "team"])

        assert result.exit_code == 1
        assert "Duplicate email: alice@example.com" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_validate_nonexistent_group(self, mock_load):
        """Test validating a group that doesn't exist."""
        mock_load.return_value = {
            "team": ["alice@example.com"]
        }

        result = runner.invoke(app, ["validate", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    @patch("gmaillm.commands.groups.load_email_groups")
    def test_validate_all_groups_with_errors(self, mock_load):
        """Test validating all groups when some have errors."""
        mock_load.return_value = {
            "valid": ["alice@example.com"],
            "invalid": ["bad-email"],
            "duplicate": ["bob@example.com", "bob@example.com"]
        }

        result = runner.invoke(app, ["validate"])

        assert result.exit_code == 1
        assert "✅ #valid" in result.stdout
        assert "✗ #invalid" in result.stdout
        assert "✗ #duplicate" in result.stdout
        assert "Validation failed" in result.stdout


class TestEditGroupsDeprecated:
    """Test deprecated edit command."""

    @patch("subprocess.run")
    @patch("gmaillm.commands.groups.get_groups_file_path")
    def test_edit_command_shows_deprecation_warning(self, mock_get_path, mock_subprocess):
        """Test that edit command shows deprecation warning."""
        mock_file = Mock()
        mock_file.__str__ = Mock(return_value="/path/to/file")
        mock_get_path.return_value = mock_file

        with patch("builtins.open", mock_open()):
            result = runner.invoke(app, ["edit"])

        assert "Deprecation Warning" in result.stdout
        assert "deprecated" in result.stdout
        assert "gmail groups create" in result.stdout
        assert "gmail groups add" in result.stdout

    @patch("gmaillm.commands.groups.get_groups_file_path")
    def test_edit_command_file_not_found(self, mock_get_path):
        """Test edit command when file doesn't exist."""
        mock_get_path.return_value = Path("/nonexistent/file")

        result = runner.invoke(app, ["edit"])

        assert result.exit_code == 1
        assert "does not exist" in result.stdout


class TestShowSchema:
    """Test schema command."""

    @patch("gmaillm.commands.groups.display_schema_and_exit")
    def test_show_schema(self, mock_display_schema):
        """Test showing JSON schema."""
        # display_schema_and_exit raises SystemExit, so we mock it
        mock_display_schema.side_effect = SystemExit(0)

        result = runner.invoke(app, ["schema"])

        # Should have called the display function
        mock_display_schema.assert_called_once()

    @patch("gmaillm.commands.groups.display_schema_and_exit")
    def test_show_schema_error(self, mock_display_schema):
        """Test error handling in schema command."""
        mock_display_schema.side_effect = Exception("Schema error")

        result = runner.invoke(app, ["schema"])

        assert result.exit_code == 1
