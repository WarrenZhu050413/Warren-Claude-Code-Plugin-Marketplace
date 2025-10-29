"""Extended tests for utils.py to cover edge cases and error paths."""

import base64
import pytest
from pathlib import Path
from email.mime.multipart import MIMEMultipart

from gmaillm.utils import (
    parse_email_address,
    format_email_address,
    create_mime_message,
    decode_base64,
    _set_message_headers,
    _attach_file,
)


class TestParseEmailAddress:
    """Test parse_email_address edge cases."""

    def test_invalid_email_with_name_format(self):
        """Test parsing fails when email in name format is invalid."""
        with pytest.raises(ValueError, match="Invalid email address"):
            parse_email_address("John Doe <invalid-email>")

    def test_invalid_plain_email(self):
        """Test parsing fails when plain email is invalid."""
        with pytest.raises(ValueError, match="Invalid email address"):
            parse_email_address("not-an-email")


class TestFormatEmailAddress:
    """Test format_email_address edge cases."""

    def test_invalid_email_raises_error(self):
        """Test formatting fails when email is invalid."""
        with pytest.raises(ValueError, match="Invalid email address"):
            format_email_address("invalid-email", "John Doe")


class TestSetMessageHeaders:
    """Test _set_message_headers edge cases."""

    def test_non_string_header_raises_error(self):
        """Test error when header value is not a string."""
        message = MIMEMultipart()
        headers = {"Subject": 123}  # Integer instead of string

        with pytest.raises(TypeError, match="Header 'Subject' must be a string"):
            _set_message_headers(message, headers)

    def test_none_header_values_skipped(self):
        """Test that None header values are skipped."""
        message = MIMEMultipart()
        headers = {
            "Subject": "Test",
            "Cc": None,  # Should be skipped
            "Bcc": None  # Should be skipped
        }

        _set_message_headers(message, headers)

        assert message["Subject"] == "Test"
        assert message.get("Cc") is None
        assert message.get("Bcc") is None


class TestAttachFile:
    """Test _attach_file edge cases."""

    def test_file_exceeds_size_limit(self, tmp_path):
        """Test error when file exceeds 25MB limit."""
        message = MIMEMultipart()
        large_file = tmp_path / "large.bin"

        # Create a file larger than 25MB (simulated by mock)
        large_file.write_bytes(b"x" * 100)  # Small file for test

        # Mock stat to report size > 25MB
        import os
        original_stat = os.stat

        def mock_stat(path):
            result = original_stat(path)
            if str(path) == str(large_file):
                # Create mock stat result with size > 25MB
                class MockStat:
                    st_size = 26 * 1024 * 1024  # 26MB

                return MockStat()
            return result

        import gmaillm.utils
        original_path_stat = Path.stat

        def mock_path_stat(self):
            if str(self) == str(large_file):
                class MockStat:
                    st_size = 26 * 1024 * 1024

                return MockStat()
            return original_path_stat(self)

        Path.stat = mock_path_stat

        try:
            with pytest.raises(ValueError, match="exceeds 25MB limit"):
                _attach_file(message, str(large_file))
        finally:
            Path.stat = original_path_stat

    def test_unknown_mime_type(self, tmp_path):
        """Test handling file with unknown MIME type."""
        message = MIMEMultipart()
        unknown_file = tmp_path / "file.unknownext"
        unknown_file.write_bytes(b"content")

        # Should use application/octet-stream for unknown types
        _attach_file(message, str(unknown_file))

        # Verify attachment was added
        assert len(message.get_payload()) > 0

    def test_mime_type_without_slash(self, tmp_path, monkeypatch):
        """Test handling MIME type without slash separator."""
        message = MIMEMultipart()
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")

        # Mock mimetypes.guess_type to return invalid MIME type
        import mimetypes

        def mock_guess_type(path):
            return ("invalidmimetype", None)  # No slash in MIME type

        monkeypatch.setattr(mimetypes, "guess_type", mock_guess_type)

        # Should handle gracefully with default application/octet-stream
        _attach_file(message, str(file_path))

        # Verify attachment was added
        assert len(message.get_payload()) > 0


class TestCreateMimeMessage:
    """Test create_mime_message edge cases."""

    def test_empty_recipient_list_raises_error(self):
        """Test error when recipient list is empty."""
        with pytest.raises(ValueError, match="At least one recipient required"):
            create_mime_message(
                to=[],  # Empty list
                subject="Test",
                body="Test body"
            )


class TestDecodeBase64:
    """Test decode_base64 edge cases."""

    def test_invalid_base64_characters(self):
        """Test decoding fails gracefully with invalid characters."""
        result = decode_base64("invalid!@#$%^&*()")
        assert result == ""

    def test_decode_error_returns_empty_string(self):
        """Test that decoding errors return empty string."""
        # Invalid base64 that passes character check but fails decode
        result = decode_base64("A===")
        assert result == ""

    def test_empty_string_returns_empty(self):
        """Test empty input returns empty string."""
        result = decode_base64("")
        assert result == ""

    def test_none_input_returns_empty(self):
        """Test None input returns empty string."""
        result = decode_base64(None)
        assert result == ""

    def test_non_string_input_returns_empty(self):
        """Test non-string input returns empty string."""
        result = decode_base64(123)
        assert result == ""

    def test_unicode_decode_error_returns_empty(self):
        """Test that unicode decode errors return empty string."""
        # Create invalid UTF-8 sequence
        invalid_utf8 = base64.b64encode(b"\xff\xfe").decode()
        result = decode_base64(invalid_utf8)
        assert result == ""

    def test_valid_base64_decodes_correctly(self):
        """Test valid base64 decodes correctly."""
        original = "Hello, World!"
        encoded = base64.b64encode(original.encode()).decode()
        result = decode_base64(encoded)
        assert result == original

    def test_url_safe_base64_decodes(self):
        """Test URL-safe base64 characters are handled."""
        # URL-safe base64 uses - and _ instead of + and /
        original = "Test data with special chars"
        encoded = base64.urlsafe_b64encode(original.encode()).decode()
        result = decode_base64(encoded)
        assert result == original
