"""Tests for formatters module - Rich terminal output formatting."""

from datetime import datetime
from io import StringIO

from rich.console import Console

from gmaillm.formatters import RichFormatter
from gmaillm.models import EmailAddress, EmailSummary


class TestRichFormatterEmailSummary:
    """Test RichFormatter.print_email_summary() method."""

    def test_print_email_summary_method_exists(self):
        """Test that print_email_summary method exists on RichFormatter.

        Regression test for bug where cli.py called formatter.print_email_summary()
        but the method didn't exist, causing AttributeError.
        """
        console = Console()
        formatter = RichFormatter(console)

        # Verify the method exists
        assert hasattr(formatter, 'print_email_summary'), \
            "RichFormatter must have print_email_summary method"
        assert callable(formatter.print_email_summary), \
            "print_email_summary must be callable"

    def test_print_email_summary_renders_basic_email(self):
        """Test that print_email_summary correctly renders an EmailSummary."""
        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True, width=100)
        formatter = RichFormatter(console)

        # Create a realistic EmailSummary
        email = EmailSummary(
            message_id="19a2d480463360ec",
            thread_id="19a2d480463360ec",
            from_=EmailAddress(email="alice@example.com", name="Alice Smith"),
            subject="Project Update - Q4 Planning",
            date=datetime(2025, 11, 6, 14, 30, 0),
            snippet="Here's the latest update on our Q4 planning initiatives...",
            labels=["INBOX", "IMPORTANT"],
            has_attachments=True,
            is_unread=True,
        )

        # Call the method
        formatter.print_email_summary(email)

        # Verify output contains key elements
        output = string_io.getvalue()
        assert "Project Update - Q4 Planning" in output, "Subject should be in output"
        assert "Alice Smith" in output or "alice@example.com" in output, \
            "Sender should be in output"
        assert "2025-11-06" in output, "Date should be in output"
        assert "19a2d4804633" in output, "Message ID should be in output"

    def test_print_email_summary_accepts_email_summary(self):
        """Test that print_email_summary accepts EmailSummary parameter."""
        console = Console()
        formatter = RichFormatter(console)

        email = EmailSummary(
            message_id="test123",
            thread_id="test123",
            from_=EmailAddress(email="test@example.com", name="Tester"),
            subject="Test",
            date=datetime.now(),
            snippet="Test snippet",
            labels=[],
            has_attachments=False,
            is_unread=False,
        )

        # Should not raise any exceptions
        formatter.print_email_summary(email)
