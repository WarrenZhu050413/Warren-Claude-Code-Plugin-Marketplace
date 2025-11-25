"""Tests for thread and status CLI commands."""

from datetime import datetime
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from gmaillm.cli import app
from gmaillm.models import EmailAddress, EmailSummary, Folder, SearchResult

runner = CliRunner()


class TestThreadCommand:
    """Test thread command."""

    @patch("gmaillm.cli.GmailClient")
    def test_thread_basic(self, mock_client_class):
        """Test basic thread retrieval."""
        mock_thread = [
            EmailSummary(
                message_id="msg1",
                thread_id="thread123",
                **{"from": EmailAddress(email="alice@example.com")},
                subject="Discussion",
                date=datetime.now(),
                snippet="First message",
                labels=["INBOX"],
                has_attachments=False,
                is_unread=False
            ),
            EmailSummary(
                message_id="msg2",
                thread_id="thread123",
                **{"from": EmailAddress(email="bob@example.com")},
                subject="Re: Discussion",
                date=datetime.now(),
                snippet="Reply message",
                labels=["INBOX"],
                has_attachments=False,
                is_unread=False
            )
        ]

        mock_client = Mock()
        mock_client.get_thread.return_value = mock_thread
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["thread", "msg1"])

        assert result.exit_code == 0
        assert "Discussion" in result.output
        mock_client.get_thread.assert_called_once_with("msg1")

    @patch("gmaillm.cli.GmailClient")
    def test_thread_api_error(self, mock_client_class):
        """Test API error during thread retrieval."""
        mock_client = Mock()
        mock_client.get_thread.side_effect = Exception("API timeout")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["thread", "msg1"])

        assert result.exit_code == 1
        assert "Error" in result.output

    @patch("gmaillm.cli.GmailClient")
    def test_thread_with_strip_quotes(self, mock_client_class):
        """Test thread command with --strip-quotes flag.

        Should display thread with quoted content removed from replies.
        """
        from gmaillm.models import EmailFull

        # Mock thread with replies that have quoted content
        mock_thread_full = [
            EmailFull(
                message_id="msg1",
                thread_id="thread123",
                **{"from": EmailAddress(email="alice@example.com", name="Alice")},
                to=[EmailAddress(email="bob@example.com", name="Bob")],
                subject="Original message",
                date=datetime.now(),
                body_plain="This is the original message content.",
                labels=["INBOX"],
            ),
            EmailFull(
                message_id="msg2",
                thread_id="thread123",
                **{"from": EmailAddress(email="bob@example.com", name="Bob")},
                to=[EmailAddress(email="alice@example.com", name="Alice")],
                subject="Re: Original message",
                date=datetime.now(),
                body_plain="This is my reply.\n\nOn date, Alice wrote:\n> This is the original message content.",
                labels=["INBOX"],
            )
        ]

        mock_client = Mock()
        mock_client.get_thread_full.return_value = mock_thread_full
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["thread", "msg1", "--strip-quotes"])

        assert result.exit_code == 0
        # Should show new content
        assert "This is my reply" in result.output
        # Should NOT show quoted content
        assert "This is the original message content" not in result.output or result.output.count("This is the original message content") == 1
        mock_client.get_thread_full.assert_called_once_with("msg1")


class TestStatusCommand:
    """Test status command."""

    @patch("gmaillm.cli.GmailClient")
    def test_status_authenticated(self, mock_client_class):
        """Test status with authenticated user."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "test@example.com",
            "folders": 5,
            "inbox_accessible": True,
            "errors": []
        }
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=50, unread_count=5),
            Folder(id="SENT", name="SENT", type="system", message_count=30, unread_count=0),
        ]
        mock_client.list_emails.return_value = SearchResult(
            emails=[
                EmailSummary(
                    message_id="msg1",
                    thread_id="thread1",
                    **{"from": EmailAddress(email="sender@example.com")},
                    subject="Test",
                    date=datetime.now(),
                    snippet="Test email",
                    labels=["INBOX", "UNREAD"],
                    has_attachments=False,
                    is_unread=True
                )
            ],
            total_count=50,
            next_page_token=None,
            query="label:INBOX"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "test@example.com" in result.output
        mock_client.verify_setup.assert_called_once()

    @patch("gmaillm.cli.GmailClient")
    def test_status_not_authenticated(self, mock_client_class):
        """Test status when not authenticated."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": False,
            "email_address": None,
            "folders": 0,
            "inbox_accessible": False,
            "errors": ["Authentication failed"]
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 1
        assert "not authenticated" in result.output.lower() or "authentication failed" in result.output.lower()
