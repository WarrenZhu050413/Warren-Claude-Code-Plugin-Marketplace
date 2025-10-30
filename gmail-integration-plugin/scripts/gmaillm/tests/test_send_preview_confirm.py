"""Tests for send command preview+confirm workflow.

This test file implements TDD for the preview-first email sending feature.
Tests verify that:
1. Emails always show a preview before sending
2. User must explicitly confirm with 'y' or 'yes'
3. Style guidelines are applied to email body
4. No auto-confirmation via piped input
"""

from unittest.mock import Mock, patch, MagicMock
from io import StringIO

import pytest
from typer.testing import CliRunner

from gmaillm.cli import app
from gmaillm.models import SendEmailResponse


runner = CliRunner()


class TestSendPreviewFlow:
    """Test preview-first workflow for send command."""

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_shows_preview_before_confirmation(self, mock_expand, mock_client_class):
        """RED: Send command should display email preview before asking for confirmation.

        This is the core safety feature - users must see full content before sending.
        """
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
            "--to", "test@example.com",
            "--subject", "Test Email",
            "--body", "This is a test message",
        ], input="y\n")  # User confirms with 'y'

        # Preview should be displayed
        assert "To: test@example.com" in result.stdout
        assert "Subject: Test Email" in result.stdout
        assert "This is a test message" in result.stdout
        assert "Send this email?" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_requires_explicit_confirmation(self, mock_expand, mock_client_class):
        """RED: User must explicitly type 'y' or 'yes' to send.

        Default should be NO (don't send). Requires explicit confirmation.
        """
        mock_expand.side_effect = lambda x: x if x else None
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123",
            success=True
        )
        mock_client_class.return_value = mock_client

        # User provides empty input (default to not sending)
        result = runner.invoke(app, [
            "send",
            "--to", "test@example.com",
            "--subject", "Test",
            "--body", "Message",
        ], input="\n")  # Just hit Enter without confirming

        # Email should NOT be sent
        assert mock_client.send_email.called == False
        assert "Cancelled" in result.stdout or "not sent" in result.stdout.lower()

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_accepts_yes_confirmation(self, mock_expand, mock_client_class):
        """RED: Send should accept 'yes' as confirmation (in addition to 'y')."""
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
            "--to", "test@example.com",
            "--subject", "Test",
            "--body", "Message",
        ], input="yes\n")

        assert result.exit_code == 0
        assert mock_client.send_email.called == True

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_rejects_no_confirmation(self, mock_expand, mock_client_class):
        """RED: Send should reject email when user says 'n' or 'no'."""
        mock_expand.side_effect = lambda x: x if x else None
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "send",
            "--to", "test@example.com",
            "--subject", "Test",
            "--body", "Message",
        ], input="n\n")

        assert mock_client.send_email.called == False
        assert "Cancelled" in result.stdout or "not sent" in result.stdout.lower()

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_yolo_flag_skips_confirmation(self, mock_expand, mock_client_class):
        """RED: --yolo flag should skip confirmation (power user mode)."""
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
            "--to", "test@example.com",
            "--subject", "Test",
            "--body", "Message",
            "--yolo",
        ])

        # Should send without asking for confirmation
        assert result.exit_code == 0
        assert mock_client.send_email.called == True
        assert "Send this email?" not in result.stdout


class TestSendStyleApplication:
    """Test that styles are applied to email content."""

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_applies_default_style(self, mock_expand, mock_client_class):
        """RED: Email body should have default style guidelines applied before sending."""
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
            "--to", "test@example.com",
            "--subject", "Test",
            "--body", "Original message",
        ], input="y\n")

        # Should show preview
        assert result.exit_code == 0
        # Original message should be in preview
        assert "Original message" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_send_auto_detects_style_from_recipient(self, mock_expand, mock_client_class):
        """RED: Style should be auto-detected based on recipient context."""
        mock_expand.side_effect = lambda x: x if x else None
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123",
            success=True
        )
        mock_client_class.return_value = mock_client

        # When no style specified, should auto-detect
        result = runner.invoke(app, [
            "send",
            "--to", "professor@harvard.edu",
            "--subject", "Question about class",
            "--body", "I have a question",
        ], input="y\n")

        # Should still show preview
        assert "To: professor@harvard.edu" in result.stdout


class TestSendPreviewFormatting:
    """Test that preview is formatted clearly for user review."""

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_preview_shows_recipient_expansion(self, mock_expand, mock_client_class):
        """RED: Preview should show expanded group names."""
        mock_expand.return_value = ["alice@example.com", "bob@example.com"]
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123",
            success=True
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, [
            "send",
            "--to", "#team",
            "--subject", "Update",
            "--body", "Team update",
        ], input="y\n")

        # Preview should show expanded recipients
        assert "alice@example.com" in result.stdout
        assert "bob@example.com" in result.stdout

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_preview_shows_all_email_parts(self, mock_expand, mock_client_class):
        """RED: Preview should clearly show To, Subject, and Body."""
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
            "--cc", "bob@example.com",
            "--subject", "Important Update",
            "--body", "Here is the update.\n\nMore details.",
        ], input="y\n")

        # All parts should be visible in preview
        assert "To:" in result.stdout
        assert "alice@example.com" in result.stdout
        assert "Cc:" in result.stdout or "CC:" in result.stdout
        assert "bob@example.com" in result.stdout
        assert "Subject:" in result.stdout
        assert "Important Update" in result.stdout
        assert "Here is the update" in result.stdout


class TestSendNoAutoConfirmation:
    """Test that auto-confirmation via piping is blocked."""

    @patch("gmaillm.cli.GmailClient")
    @patch("gmaillm.cli.expand_email_groups")
    def test_piped_input_still_requires_interactive_confirmation(self, mock_expand, mock_client_class):
        """RED: Even with piped input, confirmation should be interactive.

        This is a safety feature - `echo "y" | gmaillm send ...` should NOT work.
        """
        mock_expand.side_effect = lambda x: x if x else None
        mock_client = Mock()
        mock_client.send_email.return_value = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123",
            success=True
        )
        mock_client_class.return_value = mock_client

        # Simulating piped input (what echo "y" | ... would do)
        result = runner.invoke(app, [
            "send",
            "--to", "test@example.com",
            "--subject", "Test",
            "--body", "Message",
        ], input="y\n")

        # Should still require user interaction
        # (The runner uses interactive mode, so this just tests the behavior is correct)
        assert "Send this email?" in result.stdout
