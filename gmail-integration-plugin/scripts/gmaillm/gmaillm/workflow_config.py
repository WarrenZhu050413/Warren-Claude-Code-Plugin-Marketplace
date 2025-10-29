"""Workflow configuration management for gmaillm.

Provides configuration management for email processing workflows.
Workflows define queries and processing rules for batch email operations.
"""

from pathlib import Path
from typing import Dict, Optional
import yaml

from pydantic import BaseModel, Field


class WorkflowConfig(BaseModel):
    """Configuration for a single workflow."""

    name: str = Field(..., description="Human-readable workflow name")
    query: str = Field(..., description="Gmail search query")
    description: str = Field(default="", description="Workflow description")
    auto_mark_read: bool = Field(
        default=True,
        description="Automatically mark emails as read when skipped"
    )


class WorkflowManager:
    """Manager for workflow configurations."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize workflow manager.

        Args:
            config_path: Path to workflows.yaml (defaults to ~/.gmaillm/workflows.yaml)
        """
        self.config_path = config_path or Path.home() / ".gmaillm" / "workflows.yaml"
        self._ensure_defaults()

    def _ensure_defaults(self) -> None:
        """Create default workflows if config doesn't exist."""
        if not self.config_path.exists():
            defaults = {
                "workflows": {
                    "clear": {
                        "name": "Clear Unread Inbox",
                        "query": "is:unread in:inbox",
                        "description": "Process all unread emails in inbox",
                        "auto_mark_read": True
                    },
                    "clear-backlog": {
                        "name": "Clear Read Inbox",
                        "query": "is:read in:inbox",
                        "description": "Process read emails still in inbox",
                        "auto_mark_read": False
                    }
                }
            }
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(defaults, f, default_flow_style=False)

    def get_workflow(self, name: str) -> WorkflowConfig:
        """Load a workflow by name.

        Args:
            name: Workflow identifier

        Returns:
            WorkflowConfig object

        Raises:
            KeyError: If workflow doesn't exist
            ValueError: If workflow config is invalid
        """
        workflows = self._load_all_workflows()

        if name not in workflows:
            available = ", ".join(workflows.keys())
            raise KeyError(
                f"Workflow '{name}' not found. Available: {available}"
            )

        workflow_data = workflows[name]
        workflow_data["name"] = workflow_data.get("name", name)

        return WorkflowConfig(**workflow_data)

    def list_workflows(self) -> Dict[str, WorkflowConfig]:
        """List all workflows.

        Returns:
            Dictionary mapping workflow IDs to WorkflowConfig objects
        """
        workflows = self._load_all_workflows()
        result = {}

        for workflow_id, workflow_data in workflows.items():
            workflow_data["name"] = workflow_data.get("name", workflow_id)
            result[workflow_id] = WorkflowConfig(**workflow_data)

        return result

    def save_workflow(self, workflow_id: str, config: WorkflowConfig) -> None:
        """Save/update a workflow.

        Args:
            workflow_id: Workflow identifier (kebab-case)
            config: WorkflowConfig object
        """
        workflows = self._load_all_workflows()
        workflows[workflow_id] = config.model_dump(exclude_none=True)

        with open(self.config_path, 'w') as f:
            yaml.dump({"workflows": workflows}, f, default_flow_style=False)

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            True if deleted, False if didn't exist
        """
        workflows = self._load_all_workflows()

        if workflow_id not in workflows:
            return False

        del workflows[workflow_id]

        with open(self.config_path, 'w') as f:
            yaml.dump({"workflows": workflows}, f, default_flow_style=False)

        return True

    def _load_all_workflows(self) -> Dict:
        """Load all workflows from config file.

        Returns:
            Dictionary of workflow configurations
        """
        if not self.config_path.exists():
            self._ensure_defaults()

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config.get("workflows", {})
