"""Tests for workflow configuration management."""

import pytest
from pathlib import Path
import yaml

from gmaillm.workflow_config import WorkflowConfig, WorkflowManager


class TestWorkflowConfig:
    """Test WorkflowConfig model."""

    def test_create_minimal_config(self):
        """Test creating config with minimal required fields."""
        config = WorkflowConfig(
            name="Test Workflow",
            query="is:unread"
        )

        assert config.name == "Test Workflow"
        assert config.query == "is:unread"
        assert config.description == ""  # Default
        assert config.auto_mark_read is True  # Default

    def test_create_full_config(self):
        """Test creating config with all fields."""
        config = WorkflowConfig(
            name="Clear Inbox",
            query="is:unread in:inbox",
            description="Process unread inbox emails",
            auto_mark_read=False
        )

        assert config.name == "Clear Inbox"
        assert config.query == "is:unread in:inbox"
        assert config.description == "Process unread inbox emails"
        assert config.auto_mark_read is False

    def test_missing_required_name(self):
        """Test error when name is missing."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            WorkflowConfig(query="is:unread")

    def test_missing_required_query(self):
        """Test error when query is missing."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            WorkflowConfig(name="Test")


class TestWorkflowManager:
    """Test WorkflowManager class."""

    def test_init_creates_default_config(self, tmp_path):
        """Test initialization creates default config if missing."""
        config_path = tmp_path / "workflows.yaml"

        manager = WorkflowManager(config_path)

        assert config_path.exists()
        assert config_path.is_file()

    def test_init_with_existing_config(self, tmp_path):
        """Test initialization with existing config."""
        config_path = tmp_path / "workflows.yaml"
        config_path.write_text("workflows: {}")

        manager = WorkflowManager(config_path)

        # Should not overwrite existing file
        assert config_path.read_text() == "workflows: {}"

    def test_default_config_has_clear_workflow(self, tmp_path):
        """Test default config includes 'clear' workflow."""
        config_path = tmp_path / "workflows.yaml"

        manager = WorkflowManager(config_path)

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "workflows" in config
        assert "clear" in config["workflows"]
        assert config["workflows"]["clear"]["name"] == "Clear Unread Inbox"

    def test_default_config_has_clear_backlog_workflow(self, tmp_path):
        """Test default config includes 'clear-backlog' workflow."""
        config_path = tmp_path / "workflows.yaml"

        manager = WorkflowManager(config_path)

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "clear-backlog" in config["workflows"]
        assert config["workflows"]["clear-backlog"]["name"] == "Clear Read Inbox"

    def test_get_workflow_existing(self, tmp_path):
        """Test getting an existing workflow."""
        config_path = tmp_path / "workflows.yaml"
        workflows = {
            "workflows": {
                "test": {
                    "name": "Test Workflow",
                    "query": "is:unread",
                    "description": "Test description",
                    "auto_mark_read": False
                }
            }
        }
        with open(config_path, 'w') as f:
            yaml.dump(workflows, f)

        manager = WorkflowManager(config_path)
        workflow = manager.get_workflow("test")

        assert isinstance(workflow, WorkflowConfig)
        assert workflow.name == "Test Workflow"
        assert workflow.query == "is:unread"
        assert workflow.description == "Test description"
        assert workflow.auto_mark_read is False

    def test_get_workflow_not_found(self, tmp_path):
        """Test error when workflow doesn't exist."""
        config_path = tmp_path / "workflows.yaml"
        manager = WorkflowManager(config_path)

        with pytest.raises(KeyError) as exc_info:
            manager.get_workflow("nonexistent")

        assert "not found" in str(exc_info.value)
        assert "Available:" in str(exc_info.value)

    def test_get_workflow_missing_name_uses_id(self, tmp_path):
        """Test workflow without name field uses ID as name."""
        config_path = tmp_path / "workflows.yaml"
        workflows = {
            "workflows": {
                "test": {
                    "query": "is:unread"
                    # No 'name' field
                }
            }
        }
        with open(config_path, 'w') as f:
            yaml.dump(workflows, f)

        manager = WorkflowManager(config_path)
        workflow = manager.get_workflow("test")

        assert workflow.name == "test"  # Uses workflow ID as name

    def test_list_workflows(self, tmp_path):
        """Test listing all workflows."""
        config_path = tmp_path / "workflows.yaml"
        workflows = {
            "workflows": {
                "workflow1": {
                    "name": "First",
                    "query": "is:unread"
                },
                "workflow2": {
                    "name": "Second",
                    "query": "is:starred"
                }
            }
        }
        with open(config_path, 'w') as f:
            yaml.dump(workflows, f)

        manager = WorkflowManager(config_path)
        result = manager.list_workflows()

        assert len(result) == 2
        assert "workflow1" in result
        assert "workflow2" in result
        assert result["workflow1"].name == "First"
        assert result["workflow2"].name == "Second"

    def test_list_workflows_empty(self, tmp_path):
        """Test listing workflows when none exist."""
        config_path = tmp_path / "workflows.yaml"
        workflows = {"workflows": {}}
        with open(config_path, 'w') as f:
            yaml.dump(workflows, f)

        manager = WorkflowManager(config_path)
        result = manager.list_workflows()

        assert result == {}

    def test_save_workflow_new(self, tmp_path):
        """Test saving a new workflow."""
        config_path = tmp_path / "workflows.yaml"
        manager = WorkflowManager(config_path)

        new_workflow = WorkflowConfig(
            name="New Workflow",
            query="is:important",
            description="Important emails",
            auto_mark_read=False
        )

        manager.save_workflow("new", new_workflow)

        # Verify saved
        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "new" in config["workflows"]
        assert config["workflows"]["new"]["name"] == "New Workflow"
        assert config["workflows"]["new"]["query"] == "is:important"

    def test_save_workflow_update_existing(self, tmp_path):
        """Test updating an existing workflow."""
        config_path = tmp_path / "workflows.yaml"
        workflows = {
            "workflows": {
                "test": {
                    "name": "Old Name",
                    "query": "old:query"
                }
            }
        }
        with open(config_path, 'w') as f:
            yaml.dump(workflows, f)

        manager = WorkflowManager(config_path)

        updated = WorkflowConfig(
            name="New Name",
            query="new:query"
        )

        manager.save_workflow("test", updated)

        # Verify updated
        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert config["workflows"]["test"]["name"] == "New Name"
        assert config["workflows"]["test"]["query"] == "new:query"

    def test_delete_workflow_existing(self, tmp_path):
        """Test deleting an existing workflow."""
        config_path = tmp_path / "workflows.yaml"
        workflows = {
            "workflows": {
                "test": {"name": "Test", "query": "is:unread"},
                "keep": {"name": "Keep", "query": "is:starred"}
            }
        }
        with open(config_path, 'w') as f:
            yaml.dump(workflows, f)

        manager = WorkflowManager(config_path)
        result = manager.delete_workflow("test")

        assert result is True

        # Verify deleted
        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "test" not in config["workflows"]
        assert "keep" in config["workflows"]  # Other workflows remain

    def test_delete_workflow_not_found(self, tmp_path):
        """Test deleting non-existent workflow returns False."""
        config_path = tmp_path / "workflows.yaml"
        manager = WorkflowManager(config_path)

        result = manager.delete_workflow("nonexistent")

        assert result is False

    def test_load_all_workflows_missing_file(self, tmp_path):
        """Test loading workflows when file doesn't exist."""
        config_path = tmp_path / "workflows.yaml"
        manager = WorkflowManager(config_path)

        # Should create defaults
        workflows = manager._load_all_workflows()

        assert isinstance(workflows, dict)
        assert len(workflows) > 0  # Has default workflows

    def test_config_path_parent_created(self, tmp_path):
        """Test config path parent directories are created."""
        config_path = tmp_path / "nested" / "path" / "workflows.yaml"

        manager = WorkflowManager(config_path)

        assert config_path.parent.exists()
        assert config_path.exists()
