"""Tests for commands/workflows.py module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import yaml

import typer
from typer.testing import CliRunner

from gmaillm.commands.workflows import app
from gmaillm.workflow_config import WorkflowConfig


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_workflow_config(tmp_path):
    """Create a mock workflow config file."""
    config_path = tmp_path / "workflows.yaml"
    workflows = {
        "workflows": {
            "clear": {
                "name": "Clear Unread Inbox",
                "query": "is:unread in:inbox",
                "description": "Clear unread inbox emails",
                "auto_mark_read": True
            },
            "urgent": {
                "name": "Process Urgent",
                "query": "is:important is:unread",
                "description": "Handle urgent emails",
                "auto_mark_read": True
            }
        }
    }
    with open(config_path, 'w') as f:
        yaml.dump(workflows, f)
    return config_path


class TestExamplesCommand:
    """Test 'workflows examples' command."""

    def test_examples_shows_usage(self, runner):
        """Test examples command shows usage information."""
        result = runner.invoke(app, ["examples"])

        assert result.exit_code == 0
        assert "Example Usage" in result.stdout
        assert "LISTING WORKFLOWS" in result.stdout
        assert "VIEWING WORKFLOW DETAILS" in result.stdout
        assert "RUNNING WORKFLOWS" in result.stdout
        assert "CREATING WORKFLOWS" in result.stdout
        assert "DELETING WORKFLOWS" in result.stdout


class TestListCommand:
    """Test 'workflows list' command."""

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_list_workflows_rich_format(self, mock_manager_class, runner, mock_workflow_config):
        """Test listing workflows in rich format."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.list_workflows.return_value = {
            "clear": WorkflowConfig(
                name="Clear Unread Inbox",
                query="is:unread in:inbox",
                description="Clear unread inbox emails",
                auto_mark_read=True
            ),
            "urgent": WorkflowConfig(
                name="Process Urgent",
                query="is:important is:unread",
                description="Handle urgent emails",
                auto_mark_read=True
            )
        }
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Email Workflows" in result.stdout
        assert "clear" in result.stdout
        assert "Clear Unread Inbox" in result.stdout
        assert "urgent" in result.stdout
        assert "Process Urgent" in result.stdout

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_list_workflows_json_format(self, mock_manager_class, runner):
        """Test listing workflows in JSON format."""
        mock_manager = Mock()
        mock_manager.list_workflows.return_value = {
            "clear": WorkflowConfig(
                name="Clear Unread Inbox",
                query="is:unread in:inbox",
                auto_mark_read=True
            )
        }
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, ["list", "--output-format", "json"])

        assert result.exit_code == 0
        assert "clear" in result.stdout
        assert "is:unread in:inbox" in result.stdout

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_list_workflows_empty(self, mock_manager_class, runner):
        """Test listing when no workflows exist."""
        mock_manager = Mock()
        mock_manager.list_workflows.return_value = {}
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "No workflows configured" in result.stdout

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_list_workflows_error(self, mock_manager_class, runner):
        """Test error handling in list command."""
        mock_manager_class.side_effect = Exception("Config error")

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Error listing workflows" in result.stdout


class TestShowCommand:
    """Test 'workflows show' command."""

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_show_existing_workflow(self, mock_manager_class, runner):
        """Test showing an existing workflow."""
        mock_manager = Mock()
        mock_manager.get_workflow.return_value = WorkflowConfig(
            name="Clear Unread Inbox",
            query="is:unread in:inbox",
            description="Clear unread inbox emails",
            auto_mark_read=True
        )
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, ["show", "clear"])

        assert result.exit_code == 0
        assert "Workflow: clear" in result.stdout
        assert "Clear Unread Inbox" in result.stdout
        assert "is:unread in:inbox" in result.stdout

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_show_workflow_json_format(self, mock_manager_class, runner):
        """Test showing workflow in JSON format."""
        mock_manager = Mock()
        mock_manager.get_workflow.return_value = WorkflowConfig(
            name="Clear Unread Inbox",
            query="is:unread in:inbox",
            auto_mark_read=True
        )
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, ["show", "clear", "--output-format", "json"])

        assert result.exit_code == 0
        assert "clear" in result.stdout
        assert "is:unread in:inbox" in result.stdout

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_show_nonexistent_workflow(self, mock_manager_class, runner):
        """Test showing a workflow that doesn't exist."""
        mock_manager = Mock()
        mock_manager.get_workflow.side_effect = KeyError("Workflow 'missing' not found")
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, ["show", "missing"])

        assert result.exit_code == 1
        assert "not found" in result.stdout


class TestCreateCommand:
    """Test 'workflows create' command."""

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_create_new_workflow(self, mock_manager_class, runner):
        """Test creating a new workflow."""
        mock_manager = Mock()
        mock_manager.get_workflow.side_effect = KeyError("Not found")
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, [
            "create",
            "daily",
            "--query", "is:unread in:inbox",
            "--name", "Daily Clear",
            "--description", "Clear inbox daily"
        ])

        assert result.exit_code == 0
        assert "Workflow created: daily" in result.stdout
        assert "Daily Clear" in result.stdout
        mock_manager.save_workflow.assert_called_once()

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_create_without_name_uses_id(self, mock_manager_class, runner):
        """Test creating workflow without name uses ID as name."""
        mock_manager = Mock()
        mock_manager.get_workflow.side_effect = KeyError("Not found")
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, [
            "create",
            "daily-clear",
            "--query", "is:unread in:inbox"
        ])

        assert result.exit_code == 0
        assert "Workflow created: daily-clear" in result.stdout
        # Check that save_workflow was called
        call_args = mock_manager.save_workflow.call_args
        assert call_args[0][0] == "daily-clear"
        # Name should be title-cased version of ID
        assert "Daily Clear" in call_args[0][1].name

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_create_duplicate_without_force(self, mock_manager_class, runner):
        """Test creating duplicate workflow without --force fails."""
        mock_manager = Mock()
        mock_manager.get_workflow.return_value = WorkflowConfig(
            name="Existing",
            query="existing query"
        )
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, [
            "create",
            "existing",
            "--query", "new query"
        ])

        assert result.exit_code == 1
        assert "already exists" in result.stdout
        assert "Use --force to overwrite" in result.stdout

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_create_duplicate_with_force(self, mock_manager_class, runner):
        """Test creating duplicate workflow with --force overwrites."""
        mock_manager = Mock()
        mock_manager.get_workflow.return_value = WorkflowConfig(
            name="Existing",
            query="existing query"
        )
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, [
            "create",
            "existing",
            "--query", "new query",
            "--force"
        ])

        assert result.exit_code == 0
        assert "Workflow created" in result.stdout
        assert "Overwriting existing workflow" in result.stdout
        mock_manager.save_workflow.assert_called_once()

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_create_with_auto_mark_read_options(self, mock_manager_class, runner):
        """Test creating workflow with auto-mark-read options."""
        mock_manager = Mock()
        mock_manager.get_workflow.side_effect = KeyError("Not found")
        mock_manager_class.return_value = mock_manager

        # Test --no-auto-mark-read
        result = runner.invoke(app, [
            "create",
            "manual",
            "--query", "is:unread",
            "--no-auto-mark-read"
        ])

        assert result.exit_code == 0
        call_args = mock_manager.save_workflow.call_args
        assert call_args[0][1].auto_mark_read is False


class TestDeleteCommand:
    """Test 'workflows delete' command."""

    @patch("gmaillm.commands.workflows.WorkflowManager")
    @patch("gmaillm.commands.workflows.confirm_or_force")
    def test_delete_with_confirmation(self, mock_confirm, mock_manager_class, runner):
        """Test deleting workflow with confirmation."""
        mock_manager = Mock()
        mock_manager.get_workflow.return_value = WorkflowConfig(
            name="Test Workflow",
            query="test query"
        )
        mock_manager_class.return_value = mock_manager
        mock_confirm.return_value = True

        result = runner.invoke(app, ["delete", "test"])

        assert result.exit_code == 0
        assert "Workflow deleted: test" in result.stdout
        mock_manager.delete_workflow.assert_called_once_with("test")

    @patch("gmaillm.commands.workflows.WorkflowManager")
    @patch("gmaillm.commands.workflows.confirm_or_force")
    def test_delete_cancelled(self, mock_confirm, mock_manager_class, runner):
        """Test deleting workflow but cancelling."""
        mock_manager = Mock()
        mock_manager.get_workflow.return_value = WorkflowConfig(
            name="Test Workflow",
            query="test query"
        )
        mock_manager_class.return_value = mock_manager
        mock_confirm.return_value = False

        result = runner.invoke(app, ["delete", "test"])

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout
        mock_manager.delete_workflow.assert_not_called()

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_delete_with_force(self, mock_manager_class, runner):
        """Test deleting workflow with --force flag."""
        mock_manager = Mock()
        mock_manager.get_workflow.return_value = WorkflowConfig(
            name="Test Workflow",
            query="test query"
        )
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, ["delete", "test", "--force"])

        assert result.exit_code == 0
        assert "Workflow deleted: test" in result.stdout
        mock_manager.delete_workflow.assert_called_once_with("test")

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_delete_nonexistent_workflow(self, mock_manager_class, runner):
        """Test deleting a workflow that doesn't exist."""
        mock_manager = Mock()
        mock_manager.get_workflow.side_effect = KeyError("Workflow 'missing' not found")
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, ["delete", "missing"])

        assert result.exit_code == 1
        assert "not found" in result.stdout


class TestRunCommand:
    """Test 'workflows run' command."""

    @patch("gmaillm.commands.workflows.GmailClient")
    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_run_named_workflow_no_emails(self, mock_manager_class, mock_client_class, runner):
        """Test running named workflow with no emails found."""
        # Setup workflow manager
        mock_manager = Mock()
        mock_manager.get_workflow.return_value = WorkflowConfig(
            name="Clear Inbox",
            query="is:unread in:inbox",
            auto_mark_read=True
        )
        mock_manager_class.return_value = mock_manager

        # Setup Gmail client
        mock_client = Mock()
        mock_result = Mock()
        mock_result.emails = []
        mock_client.search_emails.return_value = mock_result
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["run", "clear"])

        assert result.exit_code == 0
        assert "No emails found" in result.stdout

    @patch("gmaillm.commands.workflows.GmailClient")
    def test_run_adhoc_query_no_emails(self, mock_client_class, runner):
        """Test running ad-hoc query with no emails found."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.emails = []
        mock_client.search_emails.return_value = mock_result
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["run", "--query", "is:unread"])

        assert result.exit_code == 0
        assert "No emails found" in result.stdout

    @patch("gmaillm.commands.workflows.GmailClient")
    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_run_workflow_json_output(self, mock_manager_class, mock_client_class, runner):
        """Test running workflow with JSON output."""
        # Setup workflow manager
        mock_manager = Mock()
        mock_manager.get_workflow.return_value = WorkflowConfig(
            name="Clear Inbox",
            query="is:unread in:inbox",
            auto_mark_read=True
        )
        mock_manager_class.return_value = mock_manager

        # Setup Gmail client
        mock_client = Mock()
        mock_result = Mock()
        mock_result.emails = []
        mock_result.model_dump.return_value = {"emails": [], "total_count": 0}
        mock_client.search_emails.return_value = mock_result
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["run", "clear", "--output-format", "json"])

        assert result.exit_code == 0
        # JSON mode should return immediately after printing JSON
        mock_result.model_dump.assert_called_once()

    def test_run_without_workflow_or_query(self, runner):
        """Test running without workflow ID or query fails."""
        result = runner.invoke(app, ["run"])

        assert result.exit_code == 1
        assert "Either workflow ID or --query is required" in result.stdout

    @patch("gmaillm.commands.workflows.WorkflowManager")
    def test_run_nonexistent_workflow(self, mock_manager_class, runner):
        """Test running a workflow that doesn't exist."""
        mock_manager = Mock()
        mock_manager.get_workflow.side_effect = KeyError("Workflow 'missing' not found")
        mock_manager_class.return_value = mock_manager

        result = runner.invoke(app, ["run", "missing"])

        assert result.exit_code == 1
        assert "not found" in result.stdout
