"""Comprehensive tests for GmailClient error handling.

This test module covers:
- Authentication errors (missing/corrupted credentials, expired tokens)
- API errors (HttpError, rate limiting, quota exceeded)
- File I/O errors (permissions, missing files)
- Validation errors (invalid queries, label names, email formats)
- Network errors and timeouts
- Edge cases in error recovery
"""

import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock, mock_open
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

from gmaillm.gmail_client import GmailClient


# Fixtures
@pytest.fixture
def temp_credentials_file(tmp_path):
    """Create temporary credentials file."""
    creds_file = tmp_path / "credentials.json"
    creds_data = {
        "token": "test_token",
        "refresh_token": "test_refresh",
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/gmail.modify"],
    }
    creds_file.write_text(json.dumps(creds_data))
    return str(creds_file)


@pytest.fixture
def temp_oauth_keys_file(tmp_path):
    """Create temporary OAuth keys file."""
    oauth_file = tmp_path / "oauth-keys.json"
    oauth_data = {
        "installed": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
        }
    }
    oauth_file.write_text(json.dumps(oauth_data))
    return str(oauth_file)


@pytest.fixture
def mock_service():
    """Mock Gmail service."""
    service = MagicMock()
    return service


# Test Classes

class TestAuthenticationErrors:
    """Test authentication error handling."""

    def test_missing_credentials_file(self, temp_oauth_keys_file):
        """Test error when credentials file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Credentials file not found"):
            GmailClient(
                credentials_file="/nonexistent/credentials.json",
                oauth_keys_file=temp_oauth_keys_file,
            )

    def test_missing_oauth_keys_file(self, temp_credentials_file):
        """Test error when OAuth keys file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="OAuth keys file not found"):
            GmailClient(
                credentials_file=temp_credentials_file,
                oauth_keys_file="/nonexistent/oauth-keys.json",
            )

    def test_empty_credentials_file(self, tmp_path, temp_oauth_keys_file):
        """Test error when credentials file is empty."""
        empty_creds = tmp_path / "empty_creds.json"
        empty_creds.write_text("")

        with pytest.raises(RuntimeError, match="Credentials file is empty"):
            GmailClient(
                credentials_file=str(empty_creds),
                oauth_keys_file=temp_oauth_keys_file,
            )

    def test_empty_oauth_keys_file(self, tmp_path, temp_credentials_file):
        """Test error when OAuth keys file is empty."""
        empty_oauth = tmp_path / "empty_oauth.json"
        empty_oauth.write_text("")

        with pytest.raises(RuntimeError, match="OAuth keys file is empty"):
            GmailClient(
                credentials_file=temp_credentials_file,
                oauth_keys_file=str(empty_oauth),
            )

    def test_corrupted_credentials_json(self, tmp_path, temp_oauth_keys_file):
        """Test error when credentials file has invalid JSON."""
        corrupted_creds = tmp_path / "corrupted_creds.json"
        corrupted_creds.write_text("{ invalid json }")

        with pytest.raises(RuntimeError, match="Invalid JSON in Credentials file"):
            GmailClient(
                credentials_file=str(corrupted_creds),
                oauth_keys_file=temp_oauth_keys_file,
            )

    def test_corrupted_oauth_keys_json(self, tmp_path, temp_credentials_file):
        """Test error when OAuth keys file has invalid JSON."""
        corrupted_oauth = tmp_path / "corrupted_oauth.json"
        corrupted_oauth.write_text("{ invalid json }")

        with pytest.raises(RuntimeError, match="Invalid JSON in OAuth keys file"):
            GmailClient(
                credentials_file=temp_credentials_file,
                oauth_keys_file=str(corrupted_oauth),
            )

    def test_missing_client_id_in_oauth_keys(self, tmp_path, temp_credentials_file):
        """Test error when OAuth keys missing client_id."""
        bad_oauth = tmp_path / "bad_oauth.json"
        bad_oauth.write_text(json.dumps({"installed": {"client_secret": "secret"}}))

        with pytest.raises(KeyError, match="Missing required OAuth field"):
            GmailClient(
                credentials_file=temp_credentials_file,
                oauth_keys_file=str(bad_oauth),
            )

    def test_missing_client_secret_in_oauth_keys(self, tmp_path, temp_credentials_file):
        """Test error when OAuth keys missing client_secret."""
        bad_oauth = tmp_path / "bad_oauth.json"
        bad_oauth.write_text(json.dumps({"installed": {"client_id": "id"}}))

        with pytest.raises(KeyError, match="Missing required OAuth field"):
            GmailClient(
                credentials_file=temp_credentials_file,
                oauth_keys_file=str(bad_oauth),
            )

    def test_credentials_file_permission_error(self, temp_oauth_keys_file):
        """Test error when credentials file has permission issues."""
        with patch("os.path.exists", return_value=True):
            with patch("os.path.getsize", side_effect=PermissionError("Access denied")):
                with pytest.raises(RuntimeError, match="Cannot access Credentials file"):
                    GmailClient(
                        credentials_file="/protected/credentials.json",
                        oauth_keys_file=temp_oauth_keys_file,
                    )


class TestAPIErrors:
    """Test Gmail API error handling."""

    def test_list_emails_http_error(self):
        """Test list_emails with HttpError."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Simulate HttpError
            mock_error = Mock(spec=HttpError)
            mock_error.__str__ = Mock(return_value="API Error 400: Bad Request")
            client.service.users().messages().list().execute.side_effect = mock_error

            with pytest.raises(RuntimeError, match="Failed to list emails"):
                client.list_emails()

    def test_read_email_http_error(self):
        """Test read_email with HttpError."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Simulate HttpError
            mock_error = Mock(spec=HttpError)
            mock_error.__str__ = Mock(return_value="API Error 404: Not Found")
            client.service.users().messages().get().execute.side_effect = mock_error

            with pytest.raises(RuntimeError, match="Failed to read email"):
                client.read_email("msg001")

    def test_get_folders_http_error(self):
        """Test get_folders with HttpError."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Simulate HttpError
            mock_error = Mock(spec=HttpError)
            mock_error.__str__ = Mock(return_value="API Error 403: Forbidden")
            client.service.users().labels().list().execute.side_effect = mock_error

            with pytest.raises(RuntimeError, match="Failed to get folders"):
                client.get_folders()

    def test_create_label_http_error(self):
        """Test create_label with HttpError."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Simulate HttpError
            mock_error = Mock(spec=HttpError)
            mock_error.__str__ = Mock(return_value="API Error 409: Label already exists")
            client.service.users().labels().create().execute.side_effect = mock_error

            with pytest.raises(RuntimeError, match="Failed to create label"):
                client.create_label("TestLabel")

    def test_get_thread_http_error(self):
        """Test get_thread with HttpError."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # First call succeeds to get message
            client.service.users().messages().get().execute.return_value = {
                "id": "msg001",
                "threadId": "thread001",
            }

            # Second call for thread fails
            mock_error = Mock(spec=HttpError)
            mock_error.__str__ = Mock(return_value="API Error 500: Internal Server Error")
            client.service.users().threads().get().execute.side_effect = mock_error

            with pytest.raises(RuntimeError, match="Failed to get thread"):
                client.get_thread("msg001")

    def test_modify_labels_http_error(self):
        """Test modify_labels with HttpError."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Simulate HttpError
            mock_error = Mock(spec=HttpError)
            mock_error.__str__ = Mock(return_value="API Error 400: Invalid label")
            client.service.users().messages().modify().execute.side_effect = mock_error

            with pytest.raises(RuntimeError, match="Failed to modify labels"):
                client.modify_labels("msg001", add_labels=["INVALID_LABEL"])

    def test_delete_email_http_error(self):
        """Test delete_email with HttpError."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Simulate HttpError
            mock_error = Mock(spec=HttpError)
            mock_error.__str__ = Mock(return_value="API Error 404: Message not found")
            client.service.users().messages().trash().execute.side_effect = mock_error

            with pytest.raises(RuntimeError, match="Failed to delete email"):
                client.delete_email("msg001")


class TestSendEmailErrors:
    """Test send_email error handling."""

    def test_send_email_http_error(self):
        """Test send_email with HttpError - returns response with error."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Simulate HttpError
            mock_error = Mock(spec=HttpError)
            mock_error.__str__ = Mock(return_value="API Error 400: Invalid recipient")
            client.service.users().messages().send().execute.side_effect = mock_error

            from gmaillm.models import SendEmailRequest

            request = SendEmailRequest(
                to=["invalid@"],
                subject="Test",
                body="Test body",
            )

            response = client.send_email(request)

            # Should return SendEmailResponse with success=False
            assert response.success is False
            assert "Gmail API error" in response.error

    def test_send_email_file_error(self):
        """Test send_email with file I/O error (attachment)."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Mock create_mime_message to raise IOError
            with patch("gmaillm.gmail_client.create_mime_message", side_effect=IOError("File not found")):
                from gmaillm.models import SendEmailRequest

                request = SendEmailRequest(
                    to=["test@example.com"],
                    subject="Test",
                    body="Test body",
                    attachments=["nonexistent.txt"],
                )

                response = client.send_email(request)

                # Should return SendEmailResponse with success=False
                assert response.success is False
                assert "File access error" in response.error

    def test_send_email_unexpected_error(self):
        """Test send_email with unexpected error."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Simulate unexpected error
            client.service.users().messages().send().execute.side_effect = ValueError("Unexpected")

            from gmaillm.models import SendEmailRequest

            request = SendEmailRequest(
                to=["test@example.com"],
                subject="Test",
                body="Test body",
            )

            response = client.send_email(request)

            # Should return SendEmailResponse with success=False
            assert response.success is False
            assert "Unexpected error" in response.error


class TestReplyEmailErrors:
    """Test reply_email error handling."""

    def test_reply_email_original_not_found(self):
        """Test reply_email when original message not found."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Simulate HttpError when fetching original
            mock_error = Mock(spec=HttpError)
            mock_error.__str__ = Mock(return_value="API Error 404: Not Found")
            client.service.users().messages().get().execute.side_effect = mock_error

            response = client.reply_email("msg001", "Reply body")

            # Should return SendEmailResponse with success=False
            assert response.success is False
            assert "Gmail API error" in response.error

    def test_reply_email_send_fails(self):
        """Test reply_email when sending fails."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Mock read_email to succeed
            from gmaillm.models import EmailFull, EmailAddress
            from datetime import datetime

            original = EmailFull(
                message_id="msg001",
                thread_id="thread001",
                **{"from": EmailAddress(email="sender@example.com", name="Sender")},
                to=[EmailAddress(email="me@example.com", name="Me")],
                cc=[],
                bcc=[],
                subject="Original Subject",
                date=datetime.now(),
                body_plain="Original body",
                body_html=None,
                attachments=[],
                labels=["INBOX"],
                headers={},
                in_reply_to=None,
                references=[],
            )

            with patch.object(client, "read_email", return_value=original):
                # Mock send_email to fail
                mock_error = Mock(spec=HttpError)
                mock_error.__str__ = Mock(return_value="API Error 500")
                client.service.users().messages().send().execute.side_effect = mock_error

                response = client.reply_email("msg001", "Reply body")

                # Should return SendEmailResponse with success=False
                assert response.success is False


class TestValidationErrors:
    """Test input validation errors."""

    def test_validate_query_too_long(self):
        """Test query validation - too long."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()

            # Create query longer than 1000 chars
            long_query = "a" * 1001

            with pytest.raises(ValueError, match="Query too long"):
                client._validate_query(long_query)

    def test_validate_query_with_null_bytes(self):
        """Test query validation - null bytes."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()

            with pytest.raises(ValueError, match="invalid control characters"):
                client._validate_query("test\x00query")

    def test_validate_query_with_control_characters(self):
        """Test query validation - control characters."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()

            with pytest.raises(ValueError, match="invalid control characters"):
                client._validate_query("test\x01query")

    def test_validate_label_name_empty(self):
        """Test label name validation - empty."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()

            with pytest.raises(ValueError, match="Label name cannot be empty"):
                client._validate_label_name("")

    def test_validate_label_name_too_long(self):
        """Test label name validation - too long."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()

            with pytest.raises(ValueError, match="Label name too long"):
                client._validate_label_name("a" * 101)

    def test_validate_label_name_invalid_characters(self):
        """Test label name validation - invalid characters."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()

            with pytest.raises(ValueError, match="invalid characters"):
                client._validate_label_name("label@#$%")

    def test_validate_label_ids_invalid(self):
        """Test label ID validation - invalid IDs."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()

            with pytest.raises(ValueError, match="Invalid label ID"):
                client._validate_label_ids([""])

            with pytest.raises(ValueError, match="Invalid label ID"):
                client._validate_label_ids([None])

            with pytest.raises(ValueError, match="invalid characters"):
                client._validate_label_ids(["Label@Invalid"])


class TestVerifySetupErrors:
    """Test verify_setup error handling."""

    def test_verify_setup_with_api_error(self):
        """Test verify_setup captures API errors."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Simulate HttpError
            mock_error = Mock(spec=HttpError)
            mock_error.__str__ = Mock(return_value="API Error 401: Unauthorized")
            client.service.users().getProfile().execute.side_effect = mock_error

            result = client.verify_setup()

            # Should return result with errors
            assert result["auth"] is False
            assert len(result["errors"]) > 0
            assert "Gmail API error" in result["errors"][0]

    def test_verify_setup_with_file_error(self):
        """Test verify_setup captures file errors."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Profile succeeds
            client.service.users().getProfile().execute.return_value = {
                "emailAddress": "test@example.com"
            }

            # get_folders raises IOError
            with patch.object(client, "get_folders", side_effect=IOError("Permission denied")):
                result = client.verify_setup()

                # Should capture error
                assert len(result["errors"]) > 0
                assert "File access error" in result["errors"][0]

    def test_verify_setup_with_unexpected_error(self):
        """Test verify_setup captures unexpected errors."""
        with patch.object(GmailClient, "_authenticate"):
            client = GmailClient()
            client.service = MagicMock()

            # Simulate unexpected error
            client.service.users().getProfile().execute.side_effect = ValueError("Unexpected")

            result = client.verify_setup()

            # Should capture error
            assert result["auth"] is False
            assert len(result["errors"]) > 0
            assert "Unexpected error" in result["errors"][0]


class TestCredentialRefreshErrors:
    """Test credential refresh error handling."""

    def test_refresh_credentials_with_network_error(self, temp_credentials_file, temp_oauth_keys_file):
        """Test refresh credentials with network error."""
        with patch("google.oauth2.credentials.Credentials.from_authorized_user_info") as mock_creds:
            # Create mock credentials that are expired
            mock_cred_obj = MagicMock()
            mock_cred_obj.expired = True
            mock_cred_obj.refresh_token = "refresh_token"
            mock_cred_obj.refresh.side_effect = RefreshError("Network error")
            mock_creds.return_value = mock_cred_obj

            with pytest.raises(RuntimeError, match="Failed to refresh credentials"):
                GmailClient(
                    credentials_file=temp_credentials_file,
                    oauth_keys_file=temp_oauth_keys_file,
                )

    def test_refresh_credentials_save_error(self, temp_credentials_file, temp_oauth_keys_file):
        """Test refresh credentials with file save error."""
        with patch("google.oauth2.credentials.Credentials.from_authorized_user_info") as mock_creds:
            # Create mock credentials that are expired
            mock_cred_obj = MagicMock()
            mock_cred_obj.expired = True
            mock_cred_obj.refresh_token = "refresh_token"
            mock_cred_obj.to_json.return_value = '{"token": "new_token"}'
            mock_creds.return_value = mock_cred_obj

            # Mock file write to raise PermissionError
            with patch("builtins.open", side_effect=PermissionError("Access denied")):
                with pytest.raises(RuntimeError, match="Failed to save refreshed credentials"):
                    GmailClient(
                        credentials_file=temp_credentials_file,
                        oauth_keys_file=temp_oauth_keys_file,
                    )
