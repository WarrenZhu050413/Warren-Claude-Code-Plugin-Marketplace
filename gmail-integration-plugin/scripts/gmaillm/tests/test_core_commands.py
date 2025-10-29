"""Additional comprehensive tests for core CLI commands.

This file supplements test_cli.py with more detailed test coverage for
the core commands: verify, status, list, read, send, reply, search, thread.
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from gmaillm.models import (
    EmailAddress,
    EmailSummary,
    EmailFull,
    SearchResult,
    Folder,
    SendEmailResponse,
)


class TestVerifyCommand:
    """Extended tests for verify command."""

    @patch("gmaillm.cli.GmailClient")
    def test_verify_shows_all_info(self, mock_client_class, capsys):
        """Test that verify displays all verification info."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "test@gmail.com",
            "folders": 15,
            "inbox_accessible": True,
            "errors": [],
        }
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "verify"]):
            with patch("sys.exit") as mock_exit:
                from gmaillm.cli import main
                main()
                mock_exit.assert_called_with(0)

    @patch("gmaillm.cli.GmailClient")
    def test_verify_shows_errors(self, mock_client_class):
        """Test that verify displays errors properly."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": False,
            "email_address": None,
            "folders": 0,
            "inbox_accessible": False,
            "errors": ["Authentication failed", "Invalid credentials"],
        }
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "verify"]):
            # Should still exit with 0 even with setup errors (not exceptions)
            with patch("sys.exit") as mock_exit:
                from gmaillm.cli import main
                main()
                mock_exit.assert_called_with(0)


class TestStatusCommand:
    """Extended tests for status command."""

    @patch("gmaillm.cli.GmailClient")
    def test_status_with_unread_emails(self, mock_client_class):
        """Test status command showing unread count."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "test@example.com",
            "folders": 10,
            "inbox_accessible": True,
            "errors": [],
        }

        inbox_folder = Folder(
            id="INBOX",
            name="INBOX",
            type="system",
            message_count=100,
            unread_count=15,
        )

        mock_client.get_folders.return_value = [inbox_folder]

        # Mock most recent email
        recent_email = EmailSummary(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com", name="Test Sender"),
            subject="Test Email",
            date=datetime(2025, 10, 28, 10, 30),
            snippet="This is a test email preview",
            is_unread=True,
        )

        mock_result = SearchResult(
            emails=[recent_email],
            total_count=1,
            query="label:INBOX",
        )
        mock_client.list_emails.return_value = mock_result

        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "status"]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()

    @patch("gmaillm.cli.GmailClient")
    def test_status_all_caught_up(self, mock_client_class):
        """Test status when all emails are read."""
        mock_client = Mock()
        mock_client.verify_setup.return_value = {
            "auth": True,
            "email_address": "test@example.com",
            "folders": 10,
            "inbox_accessible": True,
            "errors": [],
        }

        inbox_folder = Folder(
            id="INBOX",
            name="INBOX",
            type="system",
            message_count=100,
            unread_count=0,
        )

        mock_client.get_folders.return_value = [inbox_folder]
        mock_client.list_emails.return_value = SearchResult(
            emails=[], total_count=0, query="label:INBOX"
        )

        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "status"]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()


class TestListCommand:
    """Extended tests for list command."""

    @patch("gmaillm.cli.GmailClient")
    def test_list_with_query(self, mock_client_class):
        """Test list command with search query."""
        mock_client = Mock()

        emails = [
            EmailSummary(
                message_id=f"msg{i}",
                thread_id=f"thread{i}",
                from_=EmailAddress(
                    email=f"sender{i}@example.com",
                    name=f"Sender {i}"
                ),
                subject=f"Email {i}",
                date=datetime(2025, 10, 28, 10, i),
                snippet=f"Email content {i}",
            )
            for i in range(5)
        ]

        mock_result = SearchResult(
            emails=emails,
            total_count=5,
            query="from:sender@example.com",
        )
        mock_client.list_emails.return_value = mock_result
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "list",
            "--query", "from:sender@example.com",
            "--max", "5"
        ]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()

        mock_client.list_emails.assert_called_once()

    @patch("gmaillm.cli.GmailClient")
    def test_list_json_output(self, mock_client_class):
        """Test list command with JSON output format."""
        mock_client = Mock()

        email = EmailSummary(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com", name="Sender"),
            subject="Test",
            date=datetime(2025, 10, 28, 10, 30),
            snippet="Preview",
        )

        mock_result = SearchResult(
            emails=[email],
            total_count=1,
            query="label:INBOX",
        )
        mock_client.list_emails.return_value = mock_result
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "list",
            "--format", "json"
        ]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()


class TestReadCommand:
    """Extended tests for read command."""

    @patch("gmaillm.cli.GmailClient")
    def test_read_full_format(self, mock_client_class):
        """Test read command with full format."""
        mock_client = Mock()

        email = EmailFull(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com", name="Sender"),
            to=[EmailAddress(email="recipient@example.com", name="Recipient")],
            subject="Test Email",
            date=datetime(2025, 10, 28, 10, 30),
            snippet="Preview text",
            body_plain="Full email body",
            body_html="<p>Full email body</p>",
            labels=["INBOX"],
            has_attachments=False,
            is_unread=False,
        )

        mock_client.read_email.return_value = email
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "read", "msg123", "--full"]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()

        mock_client.read_email.assert_called_once_with("msg123", format="full")

    @patch("gmaillm.cli.GmailClient")
    def test_read_with_attachments(self, mock_client_class):
        """Test reading email with attachments."""
        mock_client = Mock()

        email = EmailFull(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com", name="Sender"),
            to=[EmailAddress(email="me@example.com", name="Me")],
            subject="Email with attachment",
            date=datetime(2025, 10, 28, 10, 30),
            snippet="See attached",
            body_plain="Please see the attached file.",
            labels=["INBOX"],
            has_attachments=True,
            attachment_count=2,
            is_unread=False,
        )

        mock_client.read_email.return_value = email
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "read", "msg123", "--full"]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()


class TestSendCommand:
    """Extended tests for send command."""

    @patch("gmaillm.cli.GmailClient")
    @patch("typer.confirm", return_value=True)
    def test_send_with_cc(self, mock_confirm, mock_client_class):
        """Test send command with CC recipients."""
        mock_client = Mock()
        mock_response = SendEmailResponse(
            success=True,
            message_id="msg123",
            thread_id="thread123",
        )
        mock_client.send_email.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "send",
            "--to", "recipient@example.com",
            "--cc", "cc1@example.com",
            "--cc", "cc2@example.com",
            "--subject", "Test",
            "--body", "Test body"
        ]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()

        # Verify send_email was called
        assert mock_client.send_email.called

    @patch("gmaillm.cli.GmailClient")
    @patch("typer.confirm", return_value=True)
    def test_send_with_attachments(self, mock_confirm, mock_client_class, temp_dir):
        """Test send command with attachments."""
        mock_client = Mock()
        mock_response = SendEmailResponse(
            success=True,
            message_id="msg123",
            thread_id="thread123",
        )
        mock_client.send_email.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Create test attachment file
        attachment = temp_dir / "test.pdf"
        attachment.write_text("test content")

        with patch("sys.argv", [
            "gmail", "send",
            "--to", "recipient@example.com",
            "--subject", "Test",
            "--body", "Test body",
            "--attachment", str(attachment)
        ]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()

        assert mock_client.send_email.called

    @patch("gmaillm.cli.GmailClient")
    @patch("typer.confirm", return_value=True)
    def test_send_to_multiple_recipients(
        self, mock_confirm, mock_client_class
    ):
        """Test send command with multiple recipients."""
        mock_client = Mock()
        mock_response = SendEmailResponse(
            success=True,
            message_id="msg123",
            thread_id="thread123",
        )
        mock_client.send_email.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "send",
            "--to", "alice@example.com",
            "--to", "bob@example.com",
            "--to", "charlie@example.com",
            "--subject", "Team Update",
            "--body", "Hello team"
        ]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()

        # Verify send was called
        assert mock_client.send_email.called
        # Verify multiple recipients were passed
        call_args = mock_client.send_email.call_args
        request = call_args.args[0]
        assert len(request.to) == 3
        assert "alice@example.com" in request.to
        assert "bob@example.com" in request.to
        assert "charlie@example.com" in request.to


class TestReplyCommand:
    """Extended tests for reply command."""

    @patch("gmaillm.cli.GmailClient")
    @patch("typer.confirm", return_value=True)
    def test_reply_all(self, mock_confirm, mock_client_class):
        """Test reply-all functionality."""
        mock_client = Mock()

        # Mock original email
        original = EmailSummary(
            message_id="original123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com", name="Sender"),
            subject="Original Subject",
            date=datetime(2025, 10, 28, 10, 0),
            snippet="Original message",
        )
        mock_client.read_email.return_value = original

        # Mock reply response
        reply_response = SendEmailResponse(
            success=True,
            message_id="reply123",
            thread_id="thread123",
        )
        mock_client.reply_email.return_value = reply_response
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "reply", "original123",
            "--body", "This is my reply",
            "--reply-all"
        ]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()

        # Verify reply_all was set
        call_args = mock_client.reply_email.call_args
        assert call_args.kwargs['reply_all'] is True


class TestSearchCommand:
    """Extended tests for search command."""

    @patch("gmaillm.cli.GmailClient")
    def test_search_complex_query(self, mock_client_class):
        """Test search with complex Gmail query."""
        mock_client = Mock()

        results = [
            EmailSummary(
                message_id="msg1",
                thread_id="thread1",
                from_=EmailAddress(
                    email="important@example.com",
                    name="Important Sender"
                ),
                subject="Urgent: Action Required",
                date=datetime(2025, 10, 28, 10, 30),
                snippet="Please review this urgent matter",
                is_unread=True,
            )
        ]

        mock_result = SearchResult(
            emails=results,
            total_count=1,
            query="from:important@example.com is:unread subject:urgent",
        )
        mock_client.search_emails.return_value = mock_result
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "search",
            "from:important@example.com is:unread subject:urgent"
        ]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()

    @patch("gmaillm.cli.GmailClient")
    def test_search_no_results(self, mock_client_class):
        """Test search returning no results."""
        mock_client = Mock()

        mock_result = SearchResult(
            emails=[],
            total_count=0,
            query="from:nonexistent@example.com",
        )
        mock_client.search_emails.return_value = mock_result
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "search",
            "from:nonexistent@example.com"
        ]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()


class TestThreadCommand:
    """Extended tests for thread command."""

    @patch("gmaillm.cli.GmailClient")
    def test_thread_with_multiple_messages(self, mock_client_class):
        """Test viewing thread with multiple messages."""
        mock_client = Mock()

        # Create thread with 3 messages
        thread_emails = [
            EmailFull(
                message_id=f"msg{i}",
                thread_id="thread123",
                from_=EmailAddress(
                    email=f"user{i}@example.com",
                    name=f"User {i}"
                ),
                to=[EmailAddress(email="me@example.com", name="Me")],
                subject="Thread Subject" if i == 0 else "Re: Thread Subject",
                date=datetime(2025, 10, 28, 10, i),
                snippet=f"Message {i} in thread",
                body_plain=f"This is message {i} in the thread",
                labels=["INBOX"],
                has_attachments=False,
                is_unread=(i == 2),  # Last message unread
            )
            for i in range(3)
        ]

        mock_client.get_thread.return_value = thread_emails
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "thread", "msg0"]):
            with patch("sys.exit"):
                from gmaillm.cli import main
                main()

        mock_client.get_thread.assert_called_once_with("msg0")


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @patch("gmaillm.cli.GmailClient")
    def test_invalid_message_id(self, mock_client_class):
        """Test handling of invalid message ID."""
        mock_client = Mock()
        mock_client.read_email.side_effect = Exception("Message not found")
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "read", "invalid123"]):
            with pytest.raises(SystemExit) as exc_info:
                from gmaillm.cli import main
                main()
            assert exc_info.value.code == 1

    @patch("gmaillm.cli.GmailClient")
    def test_network_error_handling(self, mock_client_class):
        """Test handling of network errors."""
        mock_client = Mock()
        mock_client.list_emails.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_client

        with patch("sys.argv", ["gmail", "list"]):
            with pytest.raises(SystemExit) as exc_info:
                from gmaillm.cli import main
                main()
            assert exc_info.value.code == 1

    @patch("gmaillm.cli.GmailClient")
    @patch("typer.confirm", return_value=True)
    def test_send_with_invalid_attachment_path(
        self, mock_confirm, mock_client_class
    ):
        """Test send with non-existent attachment file."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        with patch("sys.argv", [
            "gmail", "send",
            "--to", "test@example.com",
            "--subject", "Test",
            "--body", "Test",
            "--attachment", "/nonexistent/file.pdf"
        ]):
            with pytest.raises(SystemExit) as exc_info:
                from gmaillm.cli import main
                main()
            assert exc_info.value.code == 1
