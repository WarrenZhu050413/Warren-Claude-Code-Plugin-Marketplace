"""Tests for models.py module."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from gmaillm.models import (
    Attachment,
    EmailAddress,
    EmailFormat,
    EmailFull,
    EmailSummary,
    Folder,
    SearchResult,
    SendEmailRequest,
    SendEmailResponse,
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

    # to_markdown methods have been removed - formatting is now handled by RichFormatter


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

    # to_markdown methods have been removed - formatting is now handled by RichFormatter


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

    # to_markdown methods have been removed - formatting is now handled by RichFormatter


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

    # to_markdown methods have been removed - formatting is now handled by RichFormatter


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

    def test_invalid_email_empty_local_part(self):
        """Test that email with empty local part raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=["@domain.com"],
                subject="Test",
                body="Body",
            )

    def test_invalid_email_domain_starts_with_dot(self):
        """Test that email with domain starting with dot raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=["user@.com"],
                subject="Test",
                body="Body",
            )

    def test_invalid_email_domain_ends_with_dot(self):
        """Test that email with domain ending with dot raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=["user@domain."],
                subject="Test",
                body="Body",
            )

    def test_invalid_email_double_at(self):
        """Test that email with double @ raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=["user@@domain.com"],
                subject="Test",
                body="Body",
            )

    def test_invalid_email_no_domain(self):
        """Test that email without domain raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=["user@"],
                subject="Test",
                body="Body",
            )

    def test_invalid_email_no_tld(self):
        """Test that email without TLD raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=["user@domain"],
                subject="Test",
                body="Body",
            )

    def test_invalid_email_consecutive_dots(self):
        """Test that email with consecutive dots raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=["user..name@domain.com"],
                subject="Test",
                body="Body",
            )

    def test_invalid_email_in_cc(self):
        """Test that invalid email in CC field raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=["valid@example.com"],
                cc=["@invalid.com"],
                subject="Test",
                body="Body",
            )

    def test_invalid_email_in_bcc(self):
        """Test that invalid email in BCC field raises validation error."""
        with pytest.raises(ValidationError):
            SendEmailRequest(
                to=["valid@example.com"],
                bcc=["user@.com"],
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

    def test_valid_email_with_plus(self):
        """Test that email with plus sign is accepted."""
        req = SendEmailRequest(
            to=["user+tag@example.com"],
            subject="Test",
            body="Body",
        )
        assert req.to == ["user+tag@example.com"]

    def test_valid_email_with_subdomain(self):
        """Test that email with subdomain is accepted."""
        req = SendEmailRequest(
            to=["user@mail.example.com"],
            subject="Test",
            body="Body",
        )
        assert req.to == ["user@mail.example.com"]

    def test_valid_email_with_hyphen(self):
        """Test that email with hyphen in domain is accepted."""
        req = SendEmailRequest(
            to=["user@my-domain.com"],
            subject="Test",
            body="Body",
        )
        assert req.to == ["user@my-domain.com"]


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

    # to_markdown methods have been removed - formatting is now handled by RichFormatter


