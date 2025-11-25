"""Extended tests for send and reply CLI commands."""

from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest
from typer.testing import CliRunner

from gmaillm.cli import app
from gmaillm.models import EmailSummary, EmailAddress, SendEmailResponse

runner = CliRunner()


# ============ SEND COMMAND TESTS ============

class TestSendWithBCC:
    """Test send command with BCC functionality."""

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_with_single_bcc(self, mock_expand, mock_client_class):
        """Test sending email with single BCC recipient."""
        mock_expand.side_effect = lambda x: x if x else None
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123",
            success=True
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "send",
            "--to", "alice@example.com",
            "--subject", "Test",
            "--body", "Message",
            "--bcc", "secret@example.com",
            "--yolo"
        ])

        assert result.exit_code == 0
        assert "Email sent" in result.stdout
        # Verify BCC was included in request
        call_args = mock_client.send_email.call_args[0][0]
        assert call_args.bcc == ["secret@example.com"]

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_with_multiple_bcc(self, mock_expand, mock_client_class):
        """Test sending with multiple BCC recipients."""
        mock_expand.side_effect = lambda x: x if x else None
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "send",
            "--to", "alice@example.com",
            "--subject", "Test",
            "--body", "Message",
            "--bcc", "secret1@example.com",
            "--bcc", "secret2@example.com",
            "--yolo"
        ])

        assert result.exit_code == 0
        call_args = mock_client.send_email.call_args[0][0]
        assert len(call_args.bcc) == 2
        assert "secret1@example.com" in call_args.bcc
        assert "secret2@example.com" in call_args.bcc

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_with_bcc_group_expansion(self, mock_expand, mock_client_class):
        """Test BCC with group expansion."""
        def expand_side_effect(emails):
            if not emails:
                return None
            if "#confidential" in emails:
                return ["secret1@example.com", "secret2@example.com"]
            return emails

        mock_expand.side_effect = expand_side_effect
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "send",
            "--to", "alice@example.com",
            "--subject", "Test",
            "--body", "Message",
            "--bcc", "#confidential",
            "--yolo"
        ])

        assert result.exit_code == 0
        # Verify group was expanded
        assert mock_expand.called


class TestSendComplexScenarios:
    """Test send command with complex email scenarios."""

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_to_cc_bcc_all_at_once(self, mock_expand, mock_client_class):
        """Test sending with TO, CC, and BCC simultaneously."""
        mock_expand.side_effect = lambda x: x if x else None
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "send",
            "--to", "alice@example.com",
            "--to", "bob@example.com",
            "--cc", "manager@example.com",
            "--bcc", "audit@example.com",
            "--subject", "Team Update",
            "--body", "Important message",
            "--yolo"
        ])

        assert result.exit_code == 0
        call_args = mock_client.send_email.call_args[0][0]
        assert len(call_args.to) == 2
        assert call_args.cc == ["manager@example.com"]
        assert call_args.bcc == ["audit@example.com"]

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_with_multiple_attachments(self, mock_expand, mock_client_class):
        """Test sending with multiple attachments."""
        mock_expand.side_effect = lambda x: x if x else None
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        with patch("gmaillm.cli.validate_attachment_paths") as mock_validate:
            mock_validate.return_value = ["/path/file1.pdf", "/path/file2.doc"]

            result = runner.invoke(app, [
                "send",
                "--to", "alice@example.com",
                "--subject", "Documents",
                "--body", "See attached",
                "--attachment", "/path/file1.pdf",
                "--attachment", "/path/file2.doc",
                "--yolo"
            ])

            assert result.exit_code == 0
            assert "2 file(s)" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_send_with_invalid_attachment(self, mock_client_class):
        """Test sending with invalid attachment path."""
        with patch("gmaillm.cli.validate_attachment_paths") as mock_validate:
            mock_validate.side_effect = ValueError("File not found: /nonexistent.pdf")

            result = runner.invoke(app, [
                "send",
                "--to", "alice@example.com",
                "--subject", "Test",
                "--body", "Message",
                "--attachment", "/nonexistent.pdf",
                "--yolo"
            ])

            assert result.exit_code == 1
            assert "Error" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_cancelled_at_confirmation(self, mock_expand, mock_client_class):
        """Test cancelling send at confirmation prompt."""
        mock_expand.side_effect = lambda x: x if x else None
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "send",
            "--to", "alice@example.com",
            "--subject", "Test",
            "--body", "Message"
        ], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout
        mock_client.send_email.assert_not_called()

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_confirmed_at_prompt(self, mock_expand, mock_client_class):
        """Test confirming send at prompt."""
        mock_expand.side_effect = lambda x: x if x else None
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "send",
            "--to", "alice@example.com",
            "--subject", "Test",
            "--body", "Message"
        ], input="y\n")

        assert result.exit_code == 0
        assert "Email sent" in result.stdout
        mock_client.send_email.assert_called_once()


class TestSendJSONInput:
    """Test send command with JSON input."""

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.load_and_validate_json")
    def test_send_from_json_file(self, mock_load_json, mock_client_class):
        """Test sending email from JSON file."""
        mock_load_json.return_value = {
            "to": ["alice@example.com"],
            "subject": "Test",
            "body": "Message from JSON"
        }
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "send",
            "--json-input-path", "email.json",
            "--yolo"
        ])

        assert result.exit_code == 0
        assert "Sending email from JSON" in result.stdout
        assert "Email sent" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.load_and_validate_json")
    def test_send_from_json_with_cc_bcc(self, mock_load_json, mock_client_class):
        """Test JSON input with CC and BCC."""
        mock_load_json.return_value = {
            "to": ["alice@example.com"],
            "subject": "Test",
            "body": "Message",
            "cc": ["manager@example.com"],
            "bcc": ["audit@example.com"],
            "attachments": ["/path/file.pdf"]
        }
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        with patch("gmaillm.cli.validate_attachment_paths") as mock_validate:
            mock_validate.return_value = ["/path/file.pdf"]

            result = runner.invoke(app, [
                "send",
                "--json-input-path", "email.json",
                "--yolo"
            ])

            assert result.exit_code == 0
            call_args = mock_client.send_email.call_args[0][0]
            assert call_args.cc == ["manager@example.com"]
            assert call_args.bcc == ["audit@example.com"]

    @patch("gmaillm.cli.load_and_validate_json")
    def test_send_from_invalid_json_file(self, mock_load_json):
        """Test error handling for invalid JSON."""
        mock_load_json.side_effect = ValueError("Invalid JSON format")

        result = runner.invoke(app, [
            "send",
            "--json-input-path", "bad.json",
            "--yolo"
        ])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("gmaillm.cli.load_and_validate_json")
    def test_send_from_nonexistent_json_file(self, mock_load_json):
        """Test error when JSON file doesn't exist."""
        mock_load_json.side_effect = FileNotFoundError("File not found")

        result = runner.invoke(app, [
            "send",
            "--json-input-path", "nonexistent.json",
            "--yolo"
        ])

        assert result.exit_code == 1


class TestSendSchemaDisplay:
    """Test send command schema display."""

    @patch("gmaillm.cli.display_schema_and_exit")
    def test_send_schema_flag(self, mock_display):
        """Test --schema flag displays schema."""
        mock_display.side_effect = SystemExit(0)

        result = runner.invoke(app, ["send", "--schema"])

        mock_display.assert_called_once()


class TestSendErrorHandling:
    """Test error scenarios in send command."""

    def test_send_missing_required_args(self):
        """Test error when required args are missing."""
        result = runner.invoke(app, ["send"])

        assert result.exit_code == 1
        assert "Required" in result.stdout

    def test_send_missing_to(self):
        """Test error when --to is missing."""
        result = runner.invoke(app, [
            "send",
            "--subject", "Test",
            "--body", "Message"
        ])

        assert result.exit_code == 1

    def test_send_missing_subject(self):
        """Test error when --subject is missing."""
        result = runner.invoke(app, [
            "send",
            "--to", "alice@example.com",
            "--body", "Message"
        ])

        assert result.exit_code == 1

    def test_send_missing_body(self):
        """Test error when --body is missing."""
        result = runner.invoke(app, [
            "send",
            "--to", "alice@example.com",
            "--subject", "Test"
        ])

        assert result.exit_code == 1

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_with_invalid_email_in_to(self, mock_expand, mock_client_class):
        """Test error with invalid email in TO field."""
        mock_expand.side_effect = lambda x: x if x else None

        with patch("gmaillm.cli.validate_email_list") as mock_validate:
            mock_validate.side_effect = ValueError("Invalid email")

            result = runner.invoke(app, [
                "send",
                "--to", "invalid-email",
                "--subject", "Test",
                "--body", "Message",
                "--yolo"
            ])

            assert result.exit_code == 1

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_api_error(self, mock_expand, mock_client_class):
        """Test handling of API errors during send."""
        mock_expand.side_effect = lambda x: x if x else None
        mock_client = Mock()
        mock_client.send_email.side_effect = Exception("API error: quota exceeded")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "send",
            "--to", "alice@example.com",
            "--subject", "Test",
            "--body", "Message",
            "--yolo"
        ])

        assert result.exit_code == 1
        assert "Error" in result.stdout


# ============ REPLY COMMAND TESTS ============

class TestReplyCommand:
    """Test reply command."""

    @patch("gmaillm.cli.GmailClient")
    def test_reply_basic(self, mock_client_class):
        """Test basic reply."""
        mock_client = Mock()
        mock_client.read_email.return_value = EmailSummary(
            message_id="original123",
            thread_id="thread123",
            **{"from": EmailAddress(email="sender@example.com", name="Sender")},
            subject="Original Subject",
            date="2025-01-01T00:00:00Z",
            snippet="Original message"
        )
        mock_client.reply_email.return_value = SendEmailResponse(
            message_id="reply123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "reply",
            "original123",
            "--body", "Thanks for your message!"
        ], input="y\n")

        assert result.exit_code == 0
        assert "Reply sent" in result.stdout
        mock_client.reply_email.assert_called_once()

    @patch("gmaillm.cli.GmailClient")
    def test_reply_all(self, mock_client_class):
        """Test reply all."""
        mock_client = Mock()
        mock_client.read_email.return_value = EmailSummary(
            message_id="original123",
            thread_id="thread123",
            **{"from": EmailAddress(email="sender@example.com")},
            subject="Group Discussion",
            date="2025-01-01T00:00:00Z",
            snippet="Original"
        )
        mock_client.reply_email.return_value = SendEmailResponse(
            message_id="reply123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "reply",
            "original123",
            "--body", "Reply to all",
            "--reply-all"
        ], input="y\n")

        assert result.exit_code == 0
        assert "(Reply All mode)" in result.stdout
        # Verify reply_all=True was passed
        call_args = mock_client.reply_email.call_args
        assert call_args[1]["reply_all"] is True

    @patch("gmaillm.cli.GmailClient")
    def test_reply_cancelled(self, mock_client_class):
        """Test cancelling reply."""
        mock_client = Mock()
        mock_client.read_email.return_value = EmailSummary(
            message_id="original123",
            thread_id="thread123",
            **{"from": EmailAddress(email="sender@example.com")},
            subject="Test",
            date="2025-01-01T00:00:00Z",
            snippet="Test"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "reply",
            "original123",
            "--body", "Reply text"
        ], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout
        mock_client.reply_email.assert_not_called()


class TestReplyJSONInput:
    """Test reply with JSON input."""

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.load_and_validate_json")
    def test_reply_from_json(self, mock_load_json, mock_client_class):
        """Test replying from JSON file."""
        mock_load_json.return_value = {
            "body": "Reply from JSON",
            "reply_all": False
        }
        mock_client = Mock()
        mock_client.read_email.return_value = EmailSummary(
            message_id="original123",
            thread_id="thread123",
            **{"from": EmailAddress(email="sender@example.com")},
            subject="Test",
            date="2025-01-01T00:00:00Z",
            snippet="Test"
        )
        mock_client.reply_email.return_value = SendEmailResponse(
            message_id="reply123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "reply",
            "original123",
            "--json-input-path", "reply.json"
        ], input="y\n")

        assert result.exit_code == 0
        assert "Sending reply from JSON" in result.stdout
        assert "Reply sent" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.load_and_validate_json")
    def test_reply_from_json_reply_all(self, mock_load_json, mock_client_class):
        """Test reply all from JSON."""
        mock_load_json.return_value = {
            "body": "Reply to everyone",
            "reply_all": True
        }
        mock_client = Mock()
        mock_client.read_email.return_value = EmailSummary(
            message_id="original123",
            thread_id="thread123",
            **{"from": EmailAddress(email="sender@example.com")},
            subject="Test",
            date="2025-01-01T00:00:00Z",
            snippet="Test"
        )
        mock_client.reply_email.return_value = SendEmailResponse(
            message_id="reply123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "reply",
            "original123",
            "--json-input-path", "reply.json"
        ], input="y\n")

        assert result.exit_code == 0
        assert "(Reply All mode)" in result.stdout


class TestReplySchemaDisplay:
    """Test reply schema display."""

    @patch("gmaillm.cli.display_schema_and_exit")
    def test_reply_schema_flag(self, mock_display):
        """Test --schema flag for reply."""
        mock_display.side_effect = SystemExit(0)

        result = runner.invoke(app, ["reply", "msg123", "--schema"])

        mock_display.assert_called_once()


class TestReplyErrorHandling:
    """Test error scenarios in reply."""

    def test_reply_missing_body(self):
        """Test error when body is missing."""
        result = runner.invoke(app, ["reply", "msg123"])

        assert result.exit_code == 1
        assert "Required" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_reply_nonexistent_message(self, mock_client_class):
        """Test replying to nonexistent message."""
        mock_client = Mock()
        mock_client.read_email.side_effect = Exception("Message not found")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "reply",
            "nonexistent",
            "--body", "Reply"
        ])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    def test_reply_api_error(self, mock_client_class):
        """Test API error during reply."""
        mock_client = Mock()
        mock_client.read_email.return_value = EmailSummary(
            message_id="original123",
            thread_id="thread123",
            **{"from": EmailAddress(email="sender@example.com")},
            subject="Test",
            date="2025-01-01T00:00:00Z",
            snippet="Test"
        )
        mock_client.reply_email.side_effect = Exception("API error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "reply",
            "original123",
            "--body", "Reply"
        ], input="y\n")

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("gmaillm.cli.load_and_validate_json")
    def test_reply_invalid_json(self, mock_load_json):
        """Test invalid JSON file for reply."""
        mock_load_json.side_effect = ValueError("Invalid JSON")

        result = runner.invoke(app, [
            "reply",
            "msg123",
            "--json-input-path", "bad.json"
        ])

        assert result.exit_code != 0  # Accept any non-zero exit code for error


class TestReplyPreview:
    """Test reply preview display."""

    @patch("gmaillm.cli.GmailClient")
    def test_reply_shows_preview(self, mock_client_class):
        """Test that reply shows preview before sending."""
        mock_client = Mock()
        mock_client.read_email.return_value = EmailSummary(
            message_id="original123",
            thread_id="thread123",
            **{"from": EmailAddress(email="alice@example.com", name="Alice")},
            subject="Meeting Tomorrow",
            date="2025-01-01T00:00:00Z",
            snippet="Can we meet?"
        )
        mock_client.reply_email.return_value = SendEmailResponse(
            message_id="reply123",
            thread_id="thread123"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "reply",
            "original123",
            "--body", "Yes, 2pm works for me"
        ], input="y\n")

        assert result.exit_code == 0
        assert "Reply Preview" in result.stdout
        assert "To: alice@example.com" in result.stdout
        assert "Re: Meeting Tomorrow" in result.stdout
        assert "Yes, 2pm works for me" in result.stdout
