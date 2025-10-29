"""Extended tests for thread and status CLI commands."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from gmaillm.cli import app
from gmaillm.models import EmailSummary, EmailFull, EmailAddress, Folder, SearchResult

runner = CliRunner()


# ============ THREAD COMMAND TESTS ============

class TestThreadCommand:
    """Test thread command."""

    @patch("gmaillm.cli.GmailClient")
    def test_thread_basic(self, mock_client_class):
        """Test basic thread retrieval."""
        mock_thread = [
            EmailFull(
                message_id="msg1",
                thread_id="thread123",
                **{"from": EmailAddress(email="alice@example.com")},
                to=[EmailAddress(email="bob@example.com")],
                subject="Discussion",
                date=datetime.now(),
                body_plain="First message"
            ),
            EmailFull(
                message_id="msg2",
                thread_id="thread123",
                **{"from": EmailAddress(email="bob@example.com")},
                to=[EmailAddress(email="alice@example.com")],
                subject="Re: Discussion",
                date=datetime.now(),
                body_plain="Reply message"
            )
        ]

        mock_client = Mock()
        mock_client.get_thread.return_value = mock_thread
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["thread", "msg1"])

        assert result.exit_code == 0
        mock_client.get_thread.assert_called_once_with("msg1")

    @patch("gmaillm.cli.GmailClient")
    def test_thread_single_message(self, mock_client_class):
        """Test thread with single message (no replies)."""
        mock_thread = [
            EmailFull(
                message_id="msg1",
                thread_id="thread123",
                **{"from": EmailAddress(email="alice@example.com")},
                to=[EmailAddress(email="bob@example.com")],
                subject="Standalone",
                date=datetime.now(),
                body_plain="Single message"
            )
        ]

        mock_client = Mock()
        mock_client.get_thread.return_value = mock_thread
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["thread", "msg1"])

        assert result.exit_code == 0

    @patch("gmaillm.cli.GmailClient")
    def test_thread_long_conversation(self, mock_client_class):
        """Test thread with many messages."""
        mock_thread = []
        for i in range(10):
            mock_thread.append(EmailFull(
                message_id=f"msg{i}",
                thread_id="thread123",
                **{"from": EmailAddress(email=f"user{i % 2}@example.com")},
                to=[EmailAddress(email=f"user{(i+1) % 2}@example.com")],
                subject=f"Re: Discussion" if i > 0 else "Discussion",
                date=datetime.now(),
                body_plain=f"Message {i}"
            ))

        mock_client = Mock()
        mock_client.get_thread.return_value = mock_thread
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["thread", "msg1"])

        assert result.exit_code == 0

    @patch("gmaillm.cli.GmailClient")
    def test_thread_nonexistent_message(self, mock_client_class):
        """Test error when message doesn't exist."""
        mock_client = Mock()
        mock_client.get_thread.side_effect = Exception("Message not found")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["thread", "nonexistent"])

        assert result.exit_code == 1
        assert "Error getting thread" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_thread_with_attachments(self, mock_client_class):
        """Test thread with messages containing attachments."""
        from gmaillm.models import Attachment

        mock_thread = [
            EmailFull(
                message_id="msg1",
                thread_id="thread123",
                **{"from": EmailAddress(email="alice@example.com")},
                to=[EmailAddress(email="bob@example.com")],
                subject="Files",
                date=datetime.now(),
                body_plain="See attached",
                attachments=[
                    Attachment(
                        filename="document.pdf",
                        mime_type="application/pdf",
                        size=1024,
                        attachment_id="att1"
                    )
                ]
            )
        ]

        mock_client = Mock()
        mock_client.get_thread.return_value = mock_thread
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["thread", "msg1"])

        assert result.exit_code == 0

    @patch("gmaillm.cli.GmailClient")
    def test_thread_api_error(self, mock_client_class):
        """Test API error during thread retrieval."""
        mock_client = Mock()
        mock_client.get_thread.side_effect = Exception("API timeout")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["thread", "msg1"])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_thread_with_cc_bcc(self, mock_client_class):
        """Test thread with CC and BCC recipients."""
        mock_thread = [
            EmailFull(
                message_id="msg1",
                thread_id="thread123",
                **{"from": EmailAddress(email="alice@example.com")},
                to=[EmailAddress(email="bob@example.com")],
                cc=[EmailAddress(email="manager@example.com")],
                bcc=[EmailAddress(email="audit@example.com")],
                subject="Important",
                date=datetime.now(),
                body_plain="Message with CC/BCC"
            )
        ]

        mock_client = Mock()
        mock_client.get_thread.return_value = mock_thread
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["thread", "msg1"])

        assert result.exit_code == 0

    @patch("gmaillm.cli.GmailClient")
    def test_thread_empty(self, mock_client_class):
        """Test empty thread (edge case)."""
        mock_client = Mock()
        mock_client.get_thread.return_value = []
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["thread", "msg1"])

        assert result.exit_code == 0


# ============ STATUS COMMAND TESTS ============

class TestStatusCommand:
    """Test status command."""

    @patch("gmaillm.cli.GmailClient")
    def test_status_authenticated(self, mock_client_class):
        """Test status with authenticated user."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 10,
            "inbox_accessible": True,
            "errors": []
        }
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=100, unread_count=5),
            Folder(id="SENT", name="SENT", type="system", message_count=50, unread_count=0),
            Folder(id="Label_1", name="Work", type="user", message_count=20, unread_count=2)
        ]
        mock_client.list_emails.return_value = SearchResult(
            emails=[
                EmailSummary(
                    message_id="recent123",
                    thread_id="thread123",
                    **{"from": EmailAddress(email="sender@example.com", name="Sender")},
                    subject="Latest Email",
                    date=datetime.now(),
                    snippet="This is the most recent email",
                    is_unread=True
                )
            ],
            total_count=1,
            query=""
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "user@example.com" in result.stdout
        assert "Folder Statistics" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_status_not_authenticated(self, mock_client_class):
        """Test status when not authenticated."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": False,
            "email_address": None,
            "folders": 0,
            "inbox_accessible": False,
            "errors": ["Not authenticated", "Credentials missing"]
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 1
        assert "Not authenticated" in result.stdout
        assert "Authentication Failed" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_status_with_unread_messages(self, mock_client_class):
        """Test status showing unread message count."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 5,
            "inbox_accessible": True,
            "errors": []
        }
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=100, unread_count=25)
        ]
        mock_client.list_emails.return_value = SearchResult(
            emails=[],
            total_count=0,
            query=""
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "25 unread message" in result.stdout or "25 unread" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_status_all_caught_up(self, mock_client_class):
        """Test status when no unread messages."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 5,
            "inbox_accessible": True,
            "errors": []
        }
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=100, unread_count=0)
        ]
        mock_client.list_emails.return_value = SearchResult(
            emails=[],
            total_count=0,
            query=""
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "All caught up" in result.stdout or "caught up" in result.stdout.lower()

    @patch("gmaillm.cli.GmailClient")
    def test_status_with_custom_labels(self, mock_client_class):
        """Test status showing custom vs system labels."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 10,
            "inbox_accessible": True,
            "errors": []
        }
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=100),
            Folder(id="SENT", name="SENT", type="system", message_count=50),
            Folder(id="Label_1", name="Work", type="user", message_count=20),
            Folder(id="Label_2", name="Personal", type="user", message_count=30),
            Folder(id="Label_3", name="Projects", type="user", message_count=10)
        ]
        mock_client.list_emails.return_value = SearchResult(
            emails=[],
            total_count=0,
            query=""
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Custom:" in result.stdout or "user" in result.stdout.lower()
        assert "System:" in result.stdout or "system" in result.stdout.lower()

    @patch("gmaillm.cli.GmailClient")
    def test_status_recent_email_display(self, mock_client_class):
        """Test status displays most recent email."""
        recent_date = datetime(2025, 1, 15, 10, 30)
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 5,
            "inbox_accessible": True,
            "errors": []
        }
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=10)
        ]
        mock_client.list_emails.return_value = SearchResult(
            emails=[
                EmailSummary(
                    message_id="recent123",
                    thread_id="thread123",
                    **{"from": EmailAddress(email="important@example.com", name="Important Person")},
                    subject="Urgent: Please Review",
                    date=recent_date,
                    snippet="This is a very important message that needs your attention right away",
                    is_unread=False
                )
            ],
            total_count=1,
            query=""
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Most Recent Email" in result.stdout
        assert "Urgent: Please Review" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_status_recent_email_unread(self, mock_client_class):
        """Test status marks recent email as unread."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 5,
            "inbox_accessible": True,
            "errors": []
        }
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=10)
        ]
        mock_client.list_emails.return_value = SearchResult(
            emails=[
                EmailSummary(
                    message_id="unread123",
                    thread_id="thread123",
                    **{"from": EmailAddress(email="sender@example.com")},
                    subject="New Message",
                    date=datetime.now(),
                    snippet="You haven't read this yet",
                    is_unread=True
                )
            ],
            total_count=1,
            query=""
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "UNREAD" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_status_no_recent_email(self, mock_client_class):
        """Test status when inbox is empty."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 5,
            "inbox_accessible": True,
            "errors": []
        }
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=0, unread_count=0)
        ]
        mock_client.list_emails.return_value = SearchResult(
            emails=[],
            total_count=0,
            query=""
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0

    @patch("gmaillm.cli.GmailClient")
    def test_status_recent_email_error(self, mock_client_class):
        """Test status when fetching recent email fails."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 5,
            "inbox_accessible": True,
            "errors": []
        }
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=10)
        ]
        mock_client.list_emails.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        # Should still succeed overall, just skip recent email
        assert result.exit_code == 0
        assert "Could not fetch recent email" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_status_api_error(self, mock_client_class):
        """Test status with API error."""
        mock_client = Mock()
        mock_client.verify_setup.side_effect = Exception("API connection failed")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 1
        assert "Failed to get status" in result.stdout or "Error" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_status_folder_stats_display(self, mock_client_class):
        """Test that folder statistics are displayed."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 5,
            "inbox_accessible": True,
            "errors": []
        }
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=100, unread_count=5),
            Folder(id="SENT", name="SENT", type="system", message_count=200, unread_count=0)
        ]
        mock_client.list_emails.return_value = SearchResult(
            emails=[],
            total_count=0,
            query=""
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Folder Statistics" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_status_shows_label_counts(self, mock_client_class):
        """Test status shows total/custom/system label counts."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 8,
            "inbox_accessible": True,
            "errors": []
        }
        # 5 system + 3 custom = 8 total
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=100),
            Folder(id="SENT", name="SENT", type="system", message_count=50),
            Folder(id="DRAFT", name="DRAFT", type="system", message_count=5),
            Folder(id="TRASH", name="TRASH", type="system", message_count=10),
            Folder(id="SPAM", name="SPAM", type="system", message_count=2),
            Folder(id="Label_1", name="Work", type="user", message_count=20),
            Folder(id="Label_2", name="Personal", type="user", message_count=15),
            Folder(id="Label_3", name="Projects", type="user", message_count=8)
        ]
        mock_client.list_emails.return_value = SearchResult(
            emails=[],
            total_count=0,
            query=""
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        # Should show 8 total, 3 custom, 5 system
        assert "8" in result.stdout
        assert "3" in result.stdout
        assert "5" in result.stdout


class TestStatusEdgeCases:
    """Test edge cases for status command."""

    @patch("gmaillm.cli.GmailClient")
    def test_status_with_zero_folders(self, mock_client_class):
        """Test status when no folders exist (unusual)."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 0,
            "inbox_accessible": False,
            "errors": []
        }
        mock_client.get_folders.return_value = []
        mock_client.list_emails.return_value = SearchResult(
            emails=[],
            total_count=0,
            query=""
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0

    @patch("gmaillm.cli.GmailClient")
    def test_status_with_very_long_snippet(self, mock_client_class):
        """Test status with very long email snippet."""
        long_snippet = "A" * 500  # Very long snippet
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "user@example.com",
            "folders": 1,
            "inbox_accessible": True,
            "errors": []
        }
        mock_client.get_folders.return_value = [
            Folder(id="INBOX", name="INBOX", type="system", message_count=1)
        ]
        mock_client.list_emails.return_value = SearchResult(
            emails=[
                EmailSummary(
                    message_id="long123",
                    thread_id="thread123",
                    **{"from": EmailAddress(email="sender@example.com")},
                    subject="Long Message",
                    date=datetime.now(),
                    snippet=long_snippet,
                    is_unread=False
                )
            ],
            total_count=1,
            query=""
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        # Snippet should be truncated
        assert "..." in result.stdout
