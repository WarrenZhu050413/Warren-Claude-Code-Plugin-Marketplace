"""Tests for utils.py module."""

import base64

import pytest

from gmaillm.utils import (
    clean_snippet,
    create_mime_message,
    decode_base64,
    extract_body,
    format_email_address,
    get_header,
    parse_email_address,
    parse_label_ids,
    truncate_text,
    validate_pagination_params,
)


class TestParseEmailAddress:
    """Tests for parse_email_address function."""

    def test_parse_with_name(self):
        """Test parsing email with name in angle brackets."""
        result = parse_email_address("John Doe <john@example.com>")
        assert result == {"name": "John Doe", "email": "john@example.com"}

    def test_parse_without_name(self):
        """Test parsing plain email address."""
        result = parse_email_address("john@example.com")
        assert result == {"name": None, "email": "john@example.com"}

    def test_parse_with_extra_whitespace(self):
        """Test parsing with extra whitespace."""
        result = parse_email_address("  John Doe  <  john@example.com  >  ")
        assert result == {"name": "John Doe", "email": "john@example.com"}

    def test_parse_empty_name(self):
        """Test parsing with empty name."""
        result = parse_email_address("<john@example.com>")
        assert result == {"name": "", "email": "john@example.com"}


class TestFormatEmailAddress:
    """Tests for format_email_address function."""

    def test_format_with_name(self):
        """Test formatting email with name."""
        result = format_email_address("john@example.com", "John Doe")
        assert result == "John Doe <john@example.com>"

    def test_format_without_name(self):
        """Test formatting email without name."""
        result = format_email_address("john@example.com")
        assert result == "john@example.com"

    def test_format_with_none_name(self):
        """Test formatting with None as name."""
        result = format_email_address("john@example.com", None)
        assert result == "john@example.com"


class TestTruncateText:
    """Tests for truncate_text function."""

    def test_no_truncation_needed(self):
        """Test text shorter than max_length."""
        text = "Short text"
        result = truncate_text(text, max_length=100)
        assert result == "Short text"

    def test_truncation_with_default_suffix(self):
        """Test truncation with default ellipsis."""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, max_length=20)
        assert result == "This is a very lo..."
        assert len(result) == 20

    def test_truncation_with_custom_suffix(self):
        """Test truncation with custom suffix."""
        text = "This is a very long text"
        result = truncate_text(text, max_length=15, suffix=">>")
        assert result == "This is a ver>>"
        assert len(result) == 15

    def test_exact_length(self):
        """Test text exactly at max_length."""
        text = "Exactly20Characters!"
        result = truncate_text(text, max_length=20)
        assert result == "Exactly20Characters!"


class TestCleanSnippet:
    """Tests for clean_snippet function."""

    def test_remove_extra_whitespace(self):
        """Test removing multiple spaces and newlines."""
        snippet = "This   has    extra\n\nwhitespace"
        result = clean_snippet(snippet)
        assert result == "This has extra whitespace"

    def test_remove_image_tags(self):
        """Test removing image tags."""
        snippet = "Check this image [image: photo.jpg] out"
        result = clean_snippet(snippet)
        assert result == "Check this image out"

    def test_strip_leading_trailing_space(self):
        """Test stripping leading/trailing whitespace."""
        snippet = "  text with spaces  "
        result = clean_snippet(snippet)
        assert result == "text with spaces"

    def test_combined_cleaning(self):
        """Test multiple cleaning operations."""
        snippet = "  Hello   [image: pic.png]  world  \n\n  test  "
        result = clean_snippet(snippet)
        assert result == "Hello world test"


class TestCreateMimeMessage:
    """Tests for create_mime_message function."""

    def test_simple_message(self):
        """Test creating simple text message."""
        result = create_mime_message(
            to=["recipient@example.com"],
            subject="Test Subject",
            body="Test body",
        )
        assert "raw" in result
        # Decode and verify
        decoded = base64.urlsafe_b64decode(result["raw"]).decode("utf-8")
        assert "Test Subject" in decoded
        assert "Test body" in decoded
        assert "recipient@example.com" in decoded

    def test_html_message(self):
        """Test creating HTML message."""
        result = create_mime_message(
            to=["recipient@example.com"],
            subject="HTML Test",
            body="<h1>Hello</h1>",
            is_html=True,
        )
        decoded = base64.urlsafe_b64decode(result["raw"]).decode("utf-8")
        assert "text/html" in decoded
        assert "<h1>Hello</h1>" in decoded

    def test_message_with_cc_bcc(self):
        """Test message with CC and BCC recipients."""
        result = create_mime_message(
            to=["to@example.com"],
            subject="Test",
            body="Body",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
        )
        decoded = base64.urlsafe_b64decode(result["raw"]).decode("utf-8")
        assert "to@example.com" in decoded
        assert "cc@example.com" in decoded
        assert "bcc@example.com" in decoded

    def test_message_with_reply_to(self):
        """Test message with Reply-To header."""
        result = create_mime_message(
            to=["recipient@example.com"],
            subject="Test",
            body="Body",
            reply_to="reply@example.com",
        )
        decoded = base64.urlsafe_b64decode(result["raw"]).decode("utf-8")
        assert "reply@example.com" in decoded
        assert "Reply-To" in decoded

    def test_message_with_in_reply_to(self):
        """Test message with In-Reply-To header."""
        result = create_mime_message(
            to=["recipient@example.com"],
            subject="Re: Test",
            body="Reply body",
            in_reply_to="<original-msg-id@example.com>",
        )
        decoded = base64.urlsafe_b64decode(result["raw"]).decode("utf-8")
        assert "In-Reply-To" in decoded
        assert "References" in decoded
        assert "original-msg-id@example.com" in decoded

    def test_message_with_attachment(self, tmp_path):
        """Test message with attachment."""
        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test attachment content")

        result = create_mime_message(
            to=["recipient@example.com"],
            subject="Test with attachment",
            body="See attachment",
            attachments=[str(test_file)],
        )
        decoded = base64.urlsafe_b64decode(result["raw"]).decode("utf-8")
        assert "test.txt" in decoded
        assert "Content-Disposition" in decoded

    def test_message_with_nonexistent_attachment(self):
        """Test that nonexistent attachment raises error."""
        with pytest.raises(FileNotFoundError):
            create_mime_message(
                to=["recipient@example.com"],
                subject="Test",
                body="Body",
                attachments=["/nonexistent/file.txt"],
            )

    def test_multiple_recipients(self):
        """Test message with multiple TO recipients."""
        result = create_mime_message(
            to=["user1@example.com", "user2@example.com", "user3@example.com"],
            subject="Test",
            body="Body",
        )
        decoded = base64.urlsafe_b64decode(result["raw"]).decode("utf-8")
        assert "user1@example.com" in decoded
        assert "user2@example.com" in decoded
        assert "user3@example.com" in decoded


class TestDecodeBase64:
    """Tests for decode_base64 function."""

    def test_decode_standard_base64(self):
        """Test decoding standard base64."""
        text = "Hello, World!"
        encoded = base64.b64encode(text.encode()).decode()
        result = decode_base64(encoded)
        assert result == text

    def test_decode_url_safe_base64(self):
        """Test decoding URL-safe base64."""
        text = "Hello, World!"
        encoded = base64.urlsafe_b64encode(text.encode()).decode()
        # Gmail uses URL-safe base64 with - and _
        result = decode_base64(encoded)
        assert result == text

    def test_decode_with_missing_padding(self):
        """Test decoding base64 with missing padding."""
        # Create base64 without padding
        text = "Test"
        encoded = base64.b64encode(text.encode()).decode().rstrip("=")
        result = decode_base64(encoded)
        assert result == text

    def test_decode_invalid_base64(self):
        """Test decoding invalid base64 returns empty string."""
        result = decode_base64("not-valid-base64!!!")
        assert result == ""

    def test_decode_empty_string(self):
        """Test decoding empty string."""
        result = decode_base64("")
        assert result == ""


class TestExtractBody:
    """Tests for extract_body function."""

    def test_extract_plain_text(self):
        """Test extracting plain text body."""
        text = "Hello, World!"
        encoded = base64.urlsafe_b64encode(text.encode()).decode()
        payload = {
            "mimeType": "text/plain",
            "body": {"data": encoded},
        }
        plain, html = extract_body(payload)
        assert plain == text
        assert html is None

    def test_extract_html(self):
        """Test extracting HTML body."""
        html_text = "<h1>Hello</h1>"
        encoded = base64.urlsafe_b64encode(html_text.encode()).decode()
        payload = {
            "mimeType": "text/html",
            "body": {"data": encoded},
        }
        plain, html = extract_body(payload)
        assert plain is None
        assert html == html_text

    def test_extract_multipart(self):
        """Test extracting from multipart message."""
        plain_text = "Plain version"
        html_text = "<h1>HTML version</h1>"
        plain_encoded = base64.urlsafe_b64encode(plain_text.encode()).decode()
        html_encoded = base64.urlsafe_b64encode(html_text.encode()).decode()

        payload = {
            "mimeType": "multipart/alternative",
            "parts": [
                {"mimeType": "text/plain", "body": {"data": plain_encoded}},
                {"mimeType": "text/html", "body": {"data": html_encoded}},
            ],
        }
        plain, html = extract_body(payload)
        assert plain == plain_text
        assert html == html_text

    def test_extract_nested_multipart(self):
        """Test extracting from nested multipart structure."""
        text = "Nested text"
        encoded = base64.urlsafe_b64encode(text.encode()).decode()

        payload = {
            "mimeType": "multipart/mixed",
            "parts": [
                {
                    "mimeType": "multipart/alternative",
                    "parts": [
                        {"mimeType": "text/plain", "body": {"data": encoded}},
                    ],
                },
            ],
        }
        plain, html = extract_body(payload)
        assert plain == text
        assert html is None

    def test_extract_empty_body(self):
        """Test extracting from message with no body data."""
        payload = {
            "mimeType": "text/plain",
            "body": {},
        }
        plain, html = extract_body(payload)
        assert plain is None
        assert html is None


class TestGetHeader:
    """Tests for get_header function."""

    def test_get_existing_header(self):
        """Test getting existing header."""
        headers = [
            {"name": "Subject", "value": "Test Subject"},
            {"name": "From", "value": "sender@example.com"},
        ]
        result = get_header(headers, "Subject")
        assert result == "Test Subject"

    def test_get_header_case_insensitive(self):
        """Test header lookup is case-insensitive."""
        headers = [
            {"name": "Content-Type", "value": "text/html"},
        ]
        result = get_header(headers, "content-type")
        assert result == "text/html"

    def test_get_nonexistent_header(self):
        """Test getting header that doesn't exist."""
        headers = [
            {"name": "Subject", "value": "Test"},
        ]
        result = get_header(headers, "From")
        assert result is None

    def test_get_header_empty_list(self):
        """Test getting header from empty list."""
        result = get_header([], "Subject")
        assert result is None


class TestParseLabelIds:
    """Tests for parse_label_ids function."""

    def test_parse_unread_inbox(self):
        """Test parsing UNREAD and INBOX labels."""
        labels = ["UNREAD", "INBOX"]
        result = parse_label_ids(labels)
        assert result["is_unread"] is True
        assert result["is_inbox"] is True
        assert result["is_sent"] is False
        assert result["is_starred"] is False

    def test_parse_sent_important(self):
        """Test parsing SENT and IMPORTANT labels."""
        labels = ["SENT", "IMPORTANT"]
        result = parse_label_ids(labels)
        assert result["is_sent"] is True
        assert result["is_important"] is True
        assert result["is_unread"] is False

    def test_parse_starred_draft(self):
        """Test parsing STARRED and DRAFT labels."""
        labels = ["STARRED", "DRAFT"]
        result = parse_label_ids(labels)
        assert result["is_starred"] is True
        assert result["is_draft"] is True

    def test_parse_trash_spam(self):
        """Test parsing TRASH and SPAM labels."""
        labels = ["TRASH", "SPAM"]
        result = parse_label_ids(labels)
        assert result["is_trash"] is True
        assert result["is_spam"] is True

    def test_parse_empty_labels(self):
        """Test parsing empty label list."""
        result = parse_label_ids([])
        assert all(value is False for value in result.values())

    def test_parse_custom_labels(self):
        """Test that custom labels don't affect flags."""
        labels = ["Label_123", "Custom_Label", "INBOX"]
        result = parse_label_ids(labels)
        assert result["is_inbox"] is True
        # Other flags should be False
        assert result["is_unread"] is False


class TestValidatePaginationParams:
    """Tests for validate_pagination_params function."""

    def test_validate_normal_value(self):
        """Test validation of normal value."""
        result = validate_pagination_params(25)
        assert result == 25

    def test_validate_exceeds_max(self):
        """Test clamping to max value."""
        result = validate_pagination_params(100, max_allowed=50)
        assert result == 50

    def test_validate_negative_value(self):
        """Test negative value returns default."""
        result = validate_pagination_params(-10)
        assert result == 10

    def test_validate_zero(self):
        """Test zero returns default."""
        result = validate_pagination_params(0)
        assert result == 10

    def test_validate_custom_max(self):
        """Test with custom max_allowed."""
        result = validate_pagination_params(75, max_allowed=100)
        assert result == 75

    def test_validate_at_max(self):
        """Test value exactly at max."""
        result = validate_pagination_params(50, max_allowed=50)
        assert result == 50
