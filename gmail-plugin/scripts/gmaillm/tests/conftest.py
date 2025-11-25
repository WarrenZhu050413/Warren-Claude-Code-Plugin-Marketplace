"""Pytest configuration and shared fixtures."""

import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_credentials_file(temp_dir):
    """Create a mock credentials file."""
    creds_file = temp_dir / "token.json"
    creds_data = {
        "token": "mock_token",
        "refresh_token": "mock_refresh_token",
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
    }
    import json

    creds_file.write_text(json.dumps(creds_data))
    return creds_file


@pytest.fixture
def sample_email_groups():
    """Sample email groups for testing."""
    return {
        "team": ["alice@example.com", "bob@example.com"],
        "managers": ["manager1@example.com", "manager2@example.com"],
        "all": ["alice@example.com", "bob@example.com", "manager1@example.com"],
    }


@pytest.fixture
def sample_email_summary_data():
    """Sample data for creating EmailSummary instances."""
    from datetime import datetime

    from gmaillm.models import EmailAddress

    return {
        "message_id": "msg123",
        "thread_id": "thread123",
        "from_": EmailAddress(email="sender@example.com", name="Sender Name"),
        "subject": "Test Email Subject",
        "date": datetime(2025, 1, 15, 10, 30, 0),
        "snippet": "This is a test email snippet...",
        "labels": ["INBOX", "UNREAD"],
        "has_attachments": False,
        "is_unread": True,
    }
