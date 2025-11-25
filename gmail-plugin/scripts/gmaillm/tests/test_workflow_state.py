"""Tests for workflow state management."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from gmaillm.workflow_state import WorkflowState, WorkflowStateManager


@pytest.fixture
def temp_state_dir(tmp_path):
    """Create temporary state directory."""
    state_dir = tmp_path / "workflow-states"
    state_dir.mkdir()
    return state_dir


@pytest.fixture
def state_manager(temp_state_dir):
    """Create state manager with temp directory."""
    return WorkflowStateManager(state_dir=temp_state_dir)


class TestWorkflowState:
    """Tests for WorkflowState model."""

    def test_create_state(self):
        """Test creating a workflow state."""
        state = WorkflowState(
            token="test-token",
            workflow_id="test-workflow",
            query="is:unread",
            auto_mark_read=True,
            email_ids=["email1", "email2", "email3"],
            current_index=0
        )

        assert state.token == "test-token"
        assert state.workflow_id == "test-workflow"
        assert state.query == "is:unread"
        assert state.auto_mark_read is True
        assert len(state.email_ids) == 3
        assert state.current_index == 0
        assert state.processed == 0

    def test_current_email_id(self):
        """Test getting current email ID."""
        state = WorkflowState(
            token="test-token",
            workflow_id="test",
            query="is:unread",
            auto_mark_read=True,
            email_ids=["email1", "email2", "email3"],
            current_index=0
        )

        assert state.current_email_id == "email1"

        state.current_index = 1
        assert state.current_email_id == "email2"

        state.current_index = 10  # Out of range
        assert state.current_email_id is None

    def test_has_more(self):
        """Test checking if there are more emails."""
        state = WorkflowState(
            token="test-token",
            workflow_id="test",
            query="is:unread",
            auto_mark_read=True,
            email_ids=["email1", "email2"],
            current_index=0
        )

        assert state.has_more is True

        state.current_index = 1
        assert state.has_more is True

        state.current_index = 2
        assert state.has_more is False

    def test_advance(self):
        """Test advancing to next email."""
        state = WorkflowState(
            token="test-token",
            workflow_id="test",
            query="is:unread",
            auto_mark_read=True,
            email_ids=["email1", "email2", "email3"],
            current_index=0
        )

        assert state.current_index == 0
        assert state.processed == 0

        state.advance()
        assert state.current_index == 1
        assert state.processed == 1

        state.advance()
        assert state.current_index == 2
        assert state.processed == 2

    def test_is_expired(self):
        """Test expiration checking."""
        # Create state that expires in the future
        state = WorkflowState(
            token="test-token",
            workflow_id="test",
            query="is:unread",
            auto_mark_read=True,
            email_ids=["email1"],
            current_index=0,
            expires_at=datetime.now() + timedelta(hours=1)
        )
        assert state.is_expired is False

        # Create expired state
        expired_state = WorkflowState(
            token="test-token",
            workflow_id="test",
            query="is:unread",
            auto_mark_read=True,
            email_ids=["email1"],
            current_index=0,
            expires_at=datetime.now() - timedelta(hours=1)
        )
        assert expired_state.is_expired is True


class TestWorkflowStateManager:
    """Tests for WorkflowStateManager."""

    def test_create_state(self, state_manager):
        """Test creating a new state."""
        state = state_manager.create_state(
            workflow_id="test-workflow",
            query="is:unread in:inbox",
            email_ids=["email1", "email2", "email3"],
            auto_mark_read=True
        )

        assert state.token is not None
        assert len(state.token) > 0
        assert state.workflow_id == "test-workflow"
        assert state.query == "is:unread in:inbox"
        assert state.auto_mark_read is True
        assert state.email_ids == ["email1", "email2", "email3"]
        assert state.current_index == 0
        assert state.processed == 0

    def test_token_uniqueness(self, state_manager):
        """Test that generated tokens are unique."""
        state1 = state_manager.create_state(
            workflow_id="test1",
            query="is:unread",
            email_ids=["email1"],
            auto_mark_read=True
        )

        state2 = state_manager.create_state(
            workflow_id="test2",
            query="is:unread",
            email_ids=["email1"],
            auto_mark_read=True
        )

        assert state1.token != state2.token

    def test_save_and_load_state(self, state_manager):
        """Test saving and loading state."""
        # Create and save state
        original_state = state_manager.create_state(
            workflow_id="test-workflow",
            query="is:unread",
            email_ids=["email1", "email2"],
            auto_mark_read=True
        )

        # Load state
        loaded_state = state_manager.load_state(original_state.token)

        assert loaded_state.token == original_state.token
        assert loaded_state.workflow_id == original_state.workflow_id
        assert loaded_state.query == original_state.query
        assert loaded_state.email_ids == original_state.email_ids
        assert loaded_state.current_index == original_state.current_index

    def test_load_invalid_token(self, state_manager):
        """Test loading with invalid token."""
        with pytest.raises(ValueError, match="Invalid or expired token"):
            state_manager.load_state("invalid-token-12345")

    def test_load_expired_token(self, state_manager, temp_state_dir):
        """Test loading expired state."""
        # Create state with past expiration
        expired_state = WorkflowState(
            token="expired-token",
            workflow_id="test",
            query="is:unread",
            auto_mark_read=True,
            email_ids=["email1"],
            current_index=0,
            expires_at=datetime.now() - timedelta(hours=1)
        )

        # Manually save expired state
        state_file = temp_state_dir / f"{expired_state.token}.json"
        import json
        with open(state_file, 'w') as f:
            json.dump(expired_state.model_dump(mode='json'), f, default=str)

        # Try to load expired state
        with pytest.raises(ValueError, match="Token expired"):
            state_manager.load_state("expired-token")

        # Verify state file was deleted
        assert not state_file.exists()

    def test_update_state(self, state_manager):
        """Test updating state."""
        # Create state
        state = state_manager.create_state(
            workflow_id="test",
            query="is:unread",
            email_ids=["email1", "email2", "email3"],
            auto_mark_read=True
        )

        # Modify state
        state.advance()

        # Save updated state
        state_manager.save_state(state)

        # Load and verify
        loaded_state = state_manager.load_state(state.token)
        assert loaded_state.current_index == 1
        assert loaded_state.processed == 1

    def test_delete_state(self, state_manager, temp_state_dir):
        """Test deleting state."""
        # Create state
        state = state_manager.create_state(
            workflow_id="test",
            query="is:unread",
            email_ids=["email1"],
            auto_mark_read=True
        )

        # Verify state file exists
        state_file = temp_state_dir / f"{state.token}.json"
        assert state_file.exists()

        # Delete state
        state_manager.delete_state(state.token)

        # Verify state file was deleted
        assert not state_file.exists()

        # Try to load deleted state
        with pytest.raises(ValueError, match="Invalid or expired token"):
            state_manager.load_state(state.token)

    def test_cleanup_expired(self, state_manager, temp_state_dir):
        """Test cleaning up expired states."""
        import json

        # Create valid state
        valid_state = WorkflowState(
            token="valid-token",
            workflow_id="test",
            query="is:unread",
            auto_mark_read=True,
            email_ids=["email1"],
            current_index=0,
            expires_at=datetime.now() + timedelta(hours=1)
        )
        valid_file = temp_state_dir / f"{valid_state.token}.json"
        with open(valid_file, 'w') as f:
            json.dump(valid_state.model_dump(mode='json'), f, default=str)

        # Create expired states
        for i in range(3):
            expired_state = WorkflowState(
                token=f"expired-token-{i}",
                workflow_id="test",
                query="is:unread",
                auto_mark_read=True,
                email_ids=["email1"],
                current_index=0,
                expires_at=datetime.now() - timedelta(hours=1)
            )
            expired_file = temp_state_dir / f"{expired_state.token}.json"
            with open(expired_file, 'w') as f:
                json.dump(expired_state.model_dump(mode='json'), f, default=str)

        # Create invalid state file
        invalid_file = temp_state_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("invalid json {")

        # Run cleanup
        deleted = state_manager.cleanup_expired()

        # Should delete 3 expired + 1 invalid = 4 files
        assert deleted == 4

        # Valid state should still exist
        assert valid_file.exists()

        # Expired and invalid files should be gone
        for i in range(3):
            assert not (temp_state_dir / f"expired-token-{i}.json").exists()
        assert not invalid_file.exists()

    def test_empty_email_list(self, state_manager):
        """Test handling empty email list."""
        state = state_manager.create_state(
            workflow_id="test",
            query="is:unread",
            email_ids=[],
            auto_mark_read=True
        )

        assert state.current_email_id is None
        assert not state.has_more
        assert len(state.email_ids) == 0

    def test_workflow_progress(self, state_manager):
        """Test tracking workflow progress."""
        state = state_manager.create_state(
            workflow_id="test",
            query="is:unread",
            email_ids=["email1", "email2", "email3", "email4", "email5"],
            auto_mark_read=True
        )

        # Initial state
        assert state.current_index == 0
        assert state.processed == 0
        assert state.has_more is True

        # Process some emails
        state.advance()  # Process email1
        assert state.current_index == 1
        assert state.processed == 1

        state.advance()  # Process email2
        assert state.current_index == 2
        assert state.processed == 2

        # Skip to end
        state.current_index = 5
        assert not state.has_more
