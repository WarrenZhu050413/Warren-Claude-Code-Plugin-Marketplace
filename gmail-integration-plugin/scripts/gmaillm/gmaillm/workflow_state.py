"""Workflow state management for LLM-friendly workflows.

Provides continuation token-based workflow state management for programmatic
email processing workflows.
"""

import base64
import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowState(BaseModel):
    """State for a workflow session."""

    token: str = Field(..., description="Unique token for this workflow session")
    workflow_id: str = Field(..., description="Workflow identifier")
    query: str = Field(..., description="Gmail search query")
    auto_mark_read: bool = Field(..., description="Auto-mark read on skip")
    email_ids: List[str] = Field(..., description="List of email IDs to process")
    current_index: int = Field(..., description="Current email index")
    processed: int = Field(default=0, description="Number of emails processed")
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(default_factory=lambda: datetime.now() + timedelta(hours=1))

    @property
    def current_email_id(self) -> Optional[str]:
        """Get the current email ID."""
        if 0 <= self.current_index < len(self.email_ids):
            return self.email_ids[self.current_index]
        return None

    @property
    def has_more(self) -> bool:
        """Check if there are more emails to process."""
        return self.current_index < len(self.email_ids)

    @property
    def is_expired(self) -> bool:
        """Check if the workflow session has expired."""
        return datetime.now() > self.expires_at

    def advance(self) -> None:
        """Move to the next email."""
        self.processed += 1
        self.current_index += 1


class WorkflowAction(BaseModel):
    """Action to perform on current email."""

    action: str = Field(..., description="Action: view, reply, archive, skip, quit")
    reply_body: Optional[str] = Field(None, description="Reply body (for 'reply' action)")


class WorkflowResponse(BaseModel):
    """Response from workflow operation."""

    success: bool = Field(..., description="Whether operation was successful")
    token: Optional[str] = Field(None, description="Continuation token")
    email: Optional[Dict[str, Any]] = Field(None, description="Current email data")
    message: str = Field(..., description="Status message")
    progress: Dict[str, Any] = Field(..., description="Progress information")
    available_actions: List[str] = Field(
        default_factory=lambda: ["view", "reply", "archive", "skip", "quit"],
        description="Available actions"
    )
    completed: bool = Field(default=False, description="Whether workflow is complete")


class WorkflowStateManager:
    """Manager for workflow state persistence."""

    def __init__(self, state_dir: Optional[Path] = None) -> None:
        """Initialize state manager.

        Args:
            state_dir: Directory for state files (defaults to ~/.gmaillm/workflow-states)
        """
        self.state_dir = state_dir or Path.home() / ".gmaillm" / "workflow-states"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def create_state(
        self,
        workflow_id: str,
        query: str,
        email_ids: List[str],
        auto_mark_read: bool = True
    ) -> WorkflowState:
        """Create a new workflow state.

        Args:
            workflow_id: Workflow identifier
            query: Gmail search query
            email_ids: List of email IDs to process
            auto_mark_read: Auto-mark read on skip

        Returns:
            WorkflowState object with new token
        """
        token = self._generate_token()
        state = WorkflowState(
            token=token,
            workflow_id=workflow_id,
            query=query,
            email_ids=email_ids,
            auto_mark_read=auto_mark_read,
            current_index=0
        )
        self._save_state(state)
        return state

    def load_state(self, token: str) -> WorkflowState:
        """Load workflow state by token.

        Args:
            token: Continuation token

        Returns:
            WorkflowState object

        Raises:
            ValueError: If token is invalid or expired
        """
        state_file = self.state_dir / f"{token}.json"

        if not state_file.exists():
            raise ValueError(f"Invalid or expired token: {token}")

        with open(state_file) as f:
            data = json.load(f)

        state = WorkflowState(**data)

        if state.is_expired:
            self._delete_state(token)
            raise ValueError(f"Token expired: {token}")

        return state

    def save_state(self, state: WorkflowState) -> None:
        """Save workflow state.

        Args:
            state: WorkflowState to save
        """
        self._save_state(state)

    def delete_state(self, token: str) -> None:
        """Delete workflow state.

        Args:
            token: Token to delete
        """
        self._delete_state(token)

    def cleanup_expired(self) -> int:
        """Clean up expired workflow states.

        Returns:
            Number of states deleted
        """
        deleted = 0
        for state_file in self.state_dir.glob("*.json"):
            try:
                with open(state_file) as f:
                    data = json.load(f)
                state = WorkflowState(**data)
                if state.is_expired:
                    state_file.unlink()
                    deleted += 1
            except Exception:
                # Delete invalid state files
                state_file.unlink()
                deleted += 1
        return deleted

    def _generate_token(self) -> str:
        """Generate a unique token.

        Returns:
            Unique token string
        """
        # Generate random bytes and encode to URL-safe base64
        random_bytes = secrets.token_bytes(32)
        token = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
        return token[:32]  # Truncate to reasonable length

    def _save_state(self, state: WorkflowState) -> None:
        """Save state to disk.

        Args:
            state: WorkflowState to save
        """
        state_file = self.state_dir / f"{state.token}.json"
        with open(state_file, 'w') as f:
            json.dump(state.model_dump(mode='json'), f, default=str)

    def _delete_state(self, token: str) -> None:
        """Delete state from disk.

        Args:
            token: Token to delete
        """
        state_file = self.state_dir / f"{token}.json"
        if state_file.exists():
            state_file.unlink()
