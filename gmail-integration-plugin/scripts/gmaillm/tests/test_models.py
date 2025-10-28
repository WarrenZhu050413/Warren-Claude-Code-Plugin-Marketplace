"""Tests for models.py module."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from gmaillm.models import (
    EmailFormat,
    EmailAddress,
    Attachment,
    EmailSummary,
    EmailFull,
    SearchResult,
    Folder,
    SendEmailRequest,
    SendEmailResponse,
    BatchOperationResult,
)


class TestEmailFormat:
    """Tests for EmailFormat enum."""

    def test_enum_values(self):
        """Test enum values are correct."""
        assert EmailFormat.SUMMARY == "summary"
        assert EmailFormat.HEADERS == "headers"
        assert EmailFormat.FULL == "full"


class TestEmailAddress:
    """Tests for EmailAddress model."""

    def test_create_with_name(self):
        """Test creating email address with name."""
        addr = EmailAddress(email="john@example.com", name="John Doe")
        assert addr.email == "john@example.com"
        assert addr.name == "John Doe"

    def test_create_without_name(self):
        """Test creating email address without name."""
        addr = EmailAddress(email="john@example.com")
        assert addr.email == "john@example.com"
        assert addr.name is None

    def test_str_with_name(self):
        """Test string representation with name."""
        addr = EmailAddress(email="john@example.com", name="John Doe")
        assert str(addr) == "John Doe <john@example.com>"

    def test_str_without_name(self):
        """Test string representation without name."""
        addr = EmailAddress(email="john@example.com")
        assert str(addr) == "john@example.com"


class TestAttachment:
    """Tests for Attachment model."""

    def test_create_attachment(self):
        """Test creating attachment."""
        att = Attachment(
            filename="test.pdf",
            mime_type="application/pdf",
            size=1024,
            attachment_id="att123",
        )
        assert att.filename == "test.pdf"
        assert att.mime_type == "application/pdf"
        assert att.size == 1024
        assert att.attachment_id == "att123"

    def test_size_human_bytes(self):
        """Test human-readable size for bytes."""
        att = Attachment(
            filename="small.txt",
            mime_type="text/plain",
            size=500,
            attachment_id="att1",
        )
        assert att.size_human == "500B"

    def test_size_human_kilobytes(self):
        """Test human-readable size for kilobytes."""
        att = Attachment(
            filename="medium.jpg",
            mime_type="image/jpeg",
            size=5120,  # 5KB
            attachment_id="att2",
        )
        assert att.size_human == "5.0KB"

    def test_size_human_megabytes(self):
        """Test human-readable size for megabytes."""
        att = Attachment(
            filename="large.zip",
            mime_type="application/zip",
            size=2097152,  # 2MB
            attachment_id="att3",
        )
        assert att.size_human == "2.0MB"


class TestEmailSummary:
    """Tests for EmailSummary model."""

    def test_create_summary(self):
        """Test creating email summary."""
        summary = EmailSummary(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com", name="Sender"),
            subject="Test Subject",
            date=datetime(2025, 1, 15, 10, 30),
            snippet="This is a test email...",
            labels=["INBOX", "UNREAD"],
            has_attachments=True,
            is_unread=True,
        )
        assert summary.message_id == "msg123"
        assert summary.subject == "Test Subject"
        assert summary.is_unread is True
        assert summary.has_attachments is True

    def test_create_with_alias(self):
        """Test creating with 'from' alias."""
        summary = EmailSummary(
            **{
                "message_id": "msg123",
                "thread_id": "thread123",
                "from": EmailAddress(email="sender@example.com"),
                "subject": "Test",
                "date": datetime(2025, 1, 15, 10, 30),
                "snippet": "Test",
            }
        )
        assert summary.from_.email == "sender@example.com"

    def test_to_markdown_with_unread_attachment(self):
        """Test markdown formatting with unread and attachment flags."""
        summary = EmailSummary(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com", name="Sender"),
            subject="Important Email",
            date=datetime(2025, 1, 15, 10, 30),
            snippet="Check this out...",
            has_attachments=True,
            is_unread=True,
        )
        markdown = summary.to_markdown()
        assert "🔵" in markdown  # Unread indicator
        assert "📎" in markdown  # Attachment indicator
        assert "**Important Email**" in markdown
        assert "From: Sender <sender@example.com>" in markdown
        assert "2025-01-15 10:30" in markdown
        assert "`msg123`" in markdown
        assert "_Check this out..._" in markdown

    def test_to_markdown_read_no_attachment(self):
        """Test markdown formatting for read email without attachments."""
        summary = EmailSummary(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com"),
            subject="Regular Email",
            date=datetime(2025, 1, 15, 10, 30),
            snippet="Normal email",
            is_unread=False,
            has_attachments=False,
        )
        markdown = summary.to_markdown()
        assert "🔵" not in markdown
        assert "📎" not in markdown


class TestEmailFull:
    """Tests for EmailFull model."""

    def test_create_full_email(self):
        """Test creating full email."""
        email = EmailFull(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com", name="Sender"),
            to=[EmailAddress(email="recipient@example.com", name="Recipient")],
            subject="Test Subject",
            date=datetime(2025, 1, 15, 10, 30),
            body_plain="Plain text body",
            body_html="<p>HTML body</p>",
            labels=["INBOX"],
        )
        assert email.message_id == "msg123"
        assert len(email.to) == 1
        assert email.body_plain == "Plain text body"

    def test_to_markdown_basic(self):
        """Test basic markdown formatting."""
        email = EmailFull(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com", name="Sender"),
            to=[EmailAddress(email="recipient@example.com")],
            subject="Test Email",
            date=datetime(2025, 1, 15, 10, 30, 45),
            body_plain="Email body text",
        )
        markdown = email.to_markdown()
        assert "# Test Email" in markdown
        assert "**From:** Sender <sender@example.com>" in markdown
        assert "**To:** recipient@example.com" in markdown
        assert "2025-01-15 10:30:45" in markdown
        assert "Email body text" in markdown

    def test_to_markdown_with_cc(self):
        """Test markdown with CC recipients."""
        email = EmailFull(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com"),
            to=[EmailAddress(email="to@example.com")],
            cc=[EmailAddress(email="cc@example.com", name="CC Person")],
            subject="Test",
            date=datetime(2025, 1, 15, 10, 30),
            body_plain="Body",
        )
        markdown = email.to_markdown()
        assert "**CC:** CC Person <cc@example.com>" in markdown

    def test_to_markdown_with_attachments(self):
        """Test markdown with attachments."""
        email = EmailFull(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com"),
            to=[EmailAddress(email="to@example.com")],
            subject="Test",
            date=datetime(2025, 1, 15, 10, 30),
            body_plain="Body",
            attachments=[
                Attachment(
                    filename="doc.pdf",
                    mime_type="application/pdf",
                    size=2048,
                    attachment_id="att1",
                ),
            ],
        )
        markdown = email.to_markdown()
        assert "**Attachments:** (1 files)" in markdown
        assert "doc.pdf (2.0KB, application/pdf)" in markdown

    def test_to_markdown_truncates_long_body(self):
        """Test that long email body is truncated."""
        long_body = "x" * 4000
        email = EmailFull(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com"),
            to=[EmailAddress(email="to@example.com")],
            subject="Test",
            date=datetime(2025, 1, 15, 10, 30),
            body_plain=long_body,
        )
        markdown = email.to_markdown()
        assert "[Body truncated - 4000 total characters]" in markdown
        assert markdown.count("x") == 3000  # Only first 3000 chars

    def test_prefers_plain_text_over_html(self):
        """Test that plain text is preferred over HTML."""
        email = EmailFull(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com"),
            to=[EmailAddress(email="to@example.com")],
            subject="Test",
            date=datetime(2025, 1, 15, 10, 30),
            body_plain="Plain text version",
            body_html="<p>HTML version</p>",
        )
        markdown = email.to_markdown()
        assert "Plain text version" in markdown
        assert "<p>HTML version</p>" not in markdown


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_create_search_result(self):
        """Test creating search result."""
        result = SearchResult(
            emails=[],
            total_count=0,
            query="test query",
        )
        assert result.total_count == 0
        assert result.query == "test query"
        assert result.next_page_token is None

    def test_to_markdown_basic(self):
        """Test basic markdown formatting."""
        summary = EmailSummary(
            message_id="msg123",
            thread_id="thread123",
            from_=EmailAddress(email="sender@example.com"),
            subject="Result 1",
            date=datetime(2025, 1, 15, 10, 30),
            snippet="First result",
        )
        result = SearchResult(
            emails=[summary],
            total_count=1,
            query="search term",
        )
        markdown = result.to_markdown()
        assert "# Search Results: \"search term\"" in markdown
        assert "Found 1 emails. Showing 1." in markdown
        assert "## 1. Result 1" in markdown

    def test_to_markdown_with_next_page(self):
        """Test markdown with pagination token."""
        result = SearchResult(
            emails=[],
            total_count=100,
            query="test",
            next_page_token="token123",
        )
        markdown = result.to_markdown()
        assert "More results available" in markdown
        assert "`token123`" in markdown


class TestFolder:
    """Tests for Folder model."""

    def test_create_folder(self):
        """Test creating folder."""
        folder = Folder(
            id="Label_123",
            name="Work",
            type="user",
            message_count=50,
            unread_count=10,
        )
        assert folder.id == "Label_123"
        assert folder.name == "Work"
        assert folder.message_count == 50
        assert folder.unread_count == 10

    def test_to_markdown_with_counts(self):
        """Test markdown with message and unread counts."""
        folder = Folder(
            id="INBOX",
            name="Inbox",
            type="system",
            message_count=100,
            unread_count=5,
        )
        markdown = folder.to_markdown()
        assert "**Inbox**" in markdown
        assert "[100 messages]" in markdown
        assert "(5 unread)" in markdown
        assert "`INBOX`" in markdown

    def test_to_markdown_without_counts(self):
        """Test markdown without counts."""
        folder = Folder(
            id="Label_1",
            name="Custom",
            type="user",
        )
        markdown = folder.to_markdown()
        assert "**Custom**" in markdown
        assert "[" not in markdown  # No message count
        assert "(ID: `Label_1`)" in markdown


class TestSendEmailRequest:
    """Tests for SendEmailRequest model."""

    def test_create_basic_request(self):
        """Test creating basic send request."""
        req = SendEmailRequest(
            to=["recipient@example.com"],
            subject="Test Subject",
            body="Test body",
        )
        assert req.to == ["recipient@example.com"]
        assert req.subject == "Test Subject"
        assert req.body == "Test body"
        assert req.is_html is False

    def test_create_html_request(self):
        """Test creating HTML email request."""
        req = SendEmailRequest(
            to=["recipient@example.com"],
            subject="HTML Email",
            body="<h1>Hello</h1>",
            is_html=True,
        )
        assert req.is_html is True

    def test_create_with_cc_bcc(self):
        """Test creating request with CC and BCC."""
        req = SendEmailRequest(
            to=["to@example.com"],
            subject="Test",
            body="Body",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
        )
        assert req.cc == ["cc@example.com"]
        assert req.bcc == ["bcc@example.com"]

    def test_empty_to_list_raises_error(self):
        """Test that empty 'to' list raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=[],
                subject="Test",
                body="Body",
            )

    def test_empty_subject_raises_error(self):
        """Test that empty subject raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=["recipient@example.com"],
                subject="",
                body="Body",
            )

    def test_invalid_email_raises_error(self):
        """Test that invalid email address raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=["invalid-email"],
                subject="Test",
                body="Body",
            )

    def test_valid_email_formats(self):
        """Test various valid email formats."""
        req = SendEmailRequest(
            to=["user@example.com", "user.name@example.co.uk"],
            subject="Test",
            body="Body",
        )
        assert len(req.to) == 2


class TestSendEmailResponse:
    """Tests for SendEmailResponse model."""

    def test_create_success_response(self):
        """Test creating successful response."""
        resp = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123",
            success=True,
        )
        assert resp.success is True
        assert resp.error is None

    def test_create_error_response(self):
        """Test creating error response."""
        resp = SendEmailResponse(
            message_id="",
            thread_id="",
            success=False,
            error="Failed to send",
        )
        assert resp.success is False
        assert resp.error == "Failed to send"

    def test_to_markdown_success(self):
        """Test markdown for successful send."""
        resp = SendEmailResponse(
            message_id="msg123",
            thread_id="thread123",
            success=True,
        )
        markdown = resp.to_markdown()
        assert "✅ Email sent successfully!" in markdown
        assert "`msg123`" in markdown
        assert "`thread123`" in markdown

    def test_to_markdown_failure(self):
        """Test markdown for failed send."""
        resp = SendEmailResponse(
            message_id="",
            thread_id="",
            success=False,
            error="Network error",
        )
        markdown = resp.to_markdown()
        assert "❌ Failed to send email" in markdown
        assert "Network error" in markdown


class TestBatchOperationResult:
    """Tests for BatchOperationResult model."""

    def test_create_result(self):
        """Test creating batch result."""
        result = BatchOperationResult(
            successful=["msg1", "msg2"],
            failed={"msg3": "Error"},
            total=3,
        )
        assert len(result.successful) == 2
        assert len(result.failed) == 1
        assert result.total == 3

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        result = BatchOperationResult(
            successful=["msg1", "msg2"],
            failed={"msg3": "Error"},
            total=3,
        )
        assert result.success_rate == pytest.approx(2 / 3)

    def test_success_rate_all_success(self):
        """Test success rate with all successful."""
        result = BatchOperationResult(
            successful=["msg1", "msg2", "msg3"],
            failed={},
            total=3,
        )
        assert result.success_rate == 1.0

    def test_success_rate_all_failed(self):
        """Test success rate with all failed."""
        result = BatchOperationResult(
            successful=[],
            failed={"msg1": "Error 1", "msg2": "Error 2"},
            total=2,
        )
        assert result.success_rate == 0.0

    def test_success_rate_zero_total(self):
        """Test success rate with zero total."""
        result = BatchOperationResult(
            successful=[],
            failed={},
            total=0,
        )
        assert result.success_rate == 0.0

    def test_to_markdown_basic(self):
        """Test basic markdown formatting."""
        result = BatchOperationResult(
            successful=["msg1", "msg2"],
            failed={"msg3": "Connection timeout"},
            total=3,
        )
        markdown = result.to_markdown()
        assert "# Batch Operation Results" in markdown
        assert "✅ Successful: 2/3 (66.7%)" in markdown
        assert "❌ Failed: 1" in markdown
        assert "`msg3`: Connection timeout" in markdown

    def test_to_markdown_truncates_failures(self):
        """Test that markdown truncates long failure list."""
        failed = {f"msg{i}": f"Error {i}" for i in range(15)}
        result = BatchOperationResult(
            successful=[],
            failed=failed,
            total=15,
        )
        markdown = result.to_markdown()
        assert "and 5 more failures" in markdown  # 15 - 10 = 5
