"""Tests for gmail_client.py module."""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from datetime import datetime
from pathlib import Path
import json

from gmaillm.gmail_client import GmailClient
from gmaillm.models import (
    EmailFormat,
    EmailAddress,
    SendEmailRequest,
    SendEmailResponse,
)


@pytest.fixture
def mock_credentials():
    """Mock OAuth2 credentials."""
    creds = Mock()
    creds.valid = True
    creds.expired = False
    creds.refresh_token = "refresh_token"
    return creds


@pytest.fixture
def mock_gmail_service():
    """Mock Gmail API service."""
    service = Mock()
    return service


@pytest.fixture
def gmail_client(mock_credentials, mock_gmail_service):
    """Create GmailClient with mocked dependencies."""
    mock_oauth_keys = {
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
    }

    mock_creds_data = {
        "token": "mock_token",
        "refresh_token": "mock_refresh_token",
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
    }

    with patch("gmaillm.gmail_client.os.path.exists") as mock_exists, \
         patch("gmaillm.gmail_client.os.path.getsize") as mock_getsize, \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_creds_data))) as mock_file, \
         patch("gmaillm.gmail_client.Credentials") as mock_creds_class, \
         patch("gmaillm.gmail_client.build") as mock_build:

        # Mock file existence checks
        mock_exists.return_value = True
        mock_getsize.return_value = len(json.dumps(mock_creds_data))

        # Mock credentials loading
        mock_creds_class.from_authorized_user_info.return_value = mock_credentials
        mock_credentials.expired = False

        # Mock Gmail service
        mock_build.return_value = mock_gmail_service

        client = GmailClient()
        return client


class TestGmailClientInit:
    """Tests for GmailClient initialization."""

    @patch("gmaillm.gmail_client.Credentials")
    @patch("gmaillm.gmail_client.build")
    @patch("pathlib.Path.exists")
    def test_init_with_valid_credentials(self, mock_exists, mock_build, mock_creds):
        """Test initialization with valid credentials."""
        mock_exists.return_value = True
        mock_creds.from_authorized_user_file.return_value = Mock(valid=True)
        mock_build.return_value = Mock()

        client = GmailClient()
        assert client.service is not None

    @patch("pathlib.Path.exists")
    def test_init_without_credentials_file(self, mock_exists):
        """Test initialization fails without credentials file."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            GmailClient()


class TestVerifySetup:
    """Tests for verify_setup method."""

    def test_verify_setup_success(self, gmail_client, mock_gmail_service):
        """Test successful setup verification."""
        # Mock getProfile response
        mock_gmail_service.users().getProfile().execute.return_value = {
            "emailAddress": "user@gmail.com",
            "messagesTotal": 1000,
            "threadsTotal": 500,
        }

        result = gmail_client.verify_setup()
        assert result["success"] is True
        assert result["email"] == "user@gmail.com"
        assert result["total_messages"] == 1000
        assert result["total_threads"] == 500

    def test_verify_setup_failure(self, gmail_client, mock_gmail_service):
        """Test setup verification with API error."""
        mock_gmail_service.users().getProfile().execute.side_effect = Exception("API Error")

        result = gmail_client.verify_setup()
        assert result["success"] is False
        assert "API Error" in result["error"]


class TestListEmails:
    """Tests for list_emails method."""

    def test_list_emails_basic(self, gmail_client, mock_gmail_service):
        """Test basic email listing."""
        # Mock API response
        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [
                {"id": "msg1", "threadId": "thread1"},
                {"id": "msg2", "threadId": "thread2"},
            ],
            "resultSizeEstimate": 2,
        }

        # Mock message details
        def mock_get_message(userId, id, format):
            return Mock(execute=lambda: {
                "id": id,
                "threadId": f"thread_{id}",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "sender@example.com"},
                        {"name": "Subject", "value": f"Email {id}"},
                        {"name": "Date", "value": "Mon, 15 Jan 2025 10:30:00 +0000"},
                    ],
                },
                "snippet": f"Snippet for {id}",
                "labelIds": ["INBOX"],
            })

        mock_gmail_service.users().messages().get.side_effect = mock_get_message

        emails = gmail_client.list_emails(folder="INBOX", max_results=10)

        assert len(emails) == 2
        assert emails[0].message_id == "msg1"
        assert emails[1].message_id == "msg2"

    def test_list_emails_with_pagination(self, gmail_client, mock_gmail_service):
        """Test email listing with pagination token."""
        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg1", "threadId": "thread1"}],
            "nextPageToken": "token123",
        }

        # Mock message get
        mock_gmail_service.users().messages().get().execute.return_value = {
            "id": "msg1",
            "threadId": "thread1",
            "payload": {
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Subject", "value": "Test"},
                    {"name": "Date", "value": "Mon, 15 Jan 2025 10:30:00 +0000"},
                ],
            },
            "snippet": "Test",
            "labelIds": ["INBOX"],
        }

        emails = gmail_client.list_emails(page_token="token123")

        # Verify page token was used
        call_args = mock_gmail_service.users().messages().list.call_args
        assert "pageToken" in call_args[1] or call_args[0][0] == "token123"


class TestReadEmail:
    """Tests for read_email method."""

    def test_read_email_summary(self, gmail_client, mock_gmail_service):
        """Test reading email in SUMMARY format."""
        mock_gmail_service.users().messages().get().execute.return_value = {
            "id": "msg123",
            "threadId": "thread123",
            "payload": {
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Subject", "value": "Test Email"},
                    {"name": "Date", "value": "Mon, 15 Jan 2025 10:30:00 +0000"},
                ],
            },
            "snippet": "Email snippet...",
            "labelIds": ["INBOX", "UNREAD"],
        }

        email = gmail_client.read_email("msg123", format=EmailFormat.SUMMARY)

        assert email.message_id == "msg123"
        assert email.subject == "Test Email"
        assert email.is_unread is True

    def test_read_email_full(self, gmail_client, mock_gmail_service):
        """Test reading email in FULL format."""
        import base64
        body_text = "Email body content"
        encoded_body = base64.urlsafe_b64encode(body_text.encode()).decode()

        mock_gmail_service.users().messages().get().execute.return_value = {
            "id": "msg123",
            "threadId": "thread123",
            "payload": {
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Subject", "value": "Test Email"},
                    {"name": "Date", "value": "Mon, 15 Jan 2025 10:30:00 +0000"},
                ],
                "mimeType": "text/plain",
                "body": {"data": encoded_body},
            },
            "snippet": "Email snippet...",
            "labelIds": ["INBOX"],
        }

        email = gmail_client.read_email("msg123", format=EmailFormat.FULL)

        assert email.message_id == "msg123"
        assert email.body_plain == body_text
        assert len(email.to) == 1
        assert email.to[0].email == "recipient@example.com"


class TestSearchEmails:
    """Tests for search_emails method."""

    def test_search_emails_basic(self, gmail_client, mock_gmail_service):
        """Test basic email search."""
        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg1", "threadId": "thread1"}],
            "resultSizeEstimate": 1,
        }

        mock_gmail_service.users().messages().get().execute.return_value = {
            "id": "msg1",
            "threadId": "thread1",
            "payload": {
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Subject", "value": "Search Result"},
                    {"name": "Date", "value": "Mon, 15 Jan 2025 10:30:00 +0000"},
                ],
            },
            "snippet": "Matching content",
            "labelIds": ["INBOX"],
        }

        result = gmail_client.search_emails("test query")

        assert result.query == "test query"
        assert result.total_count == 1
        assert len(result.emails) == 1


class TestSendEmail:
    """Tests for send_email method."""

    def test_send_email_basic(self, gmail_client, mock_gmail_service):
        """Test sending basic email."""
        mock_gmail_service.users().messages().send().execute.return_value = {
            "id": "msg123",
            "threadId": "thread123",
            "labelIds": ["SENT"],
        }

        request = SendEmailRequest(
            to=["recipient@example.com"],
            subject="Test Email",
            body="Test body",
        )

        response = gmail_client.send_email(request)

        assert response.success is True
        assert response.message_id == "msg123"
        assert response.thread_id == "thread123"

    def test_send_email_with_attachments(self, gmail_client, mock_gmail_service, tmp_path):
        """Test sending email with attachments."""
        # Create temporary file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test attachment")

        mock_gmail_service.users().messages().send().execute.return_value = {
            "id": "msg123",
            "threadId": "thread123",
            "labelIds": ["SENT"],
        }

        request = SendEmailRequest(
            to=["recipient@example.com"],
            subject="Email with attachment",
            body="See attached",
            attachments=[str(test_file)],
        )

        response = gmail_client.send_email(request)

        assert response.success is True

    def test_send_email_error(self, gmail_client, mock_gmail_service):
        """Test send email with API error."""
        mock_gmail_service.users().messages().send().execute.side_effect = Exception("Send failed")

        request = SendEmailRequest(
            to=["recipient@example.com"],
            subject="Test",
            body="Body",
        )

        response = gmail_client.send_email(request)

        assert response.success is False
        assert "Send failed" in response.error


class TestReplyEmail:
    """Tests for reply_email method."""

    def test_reply_email_basic(self, gmail_client, mock_gmail_service):
        """Test replying to email."""
        # Mock original message
        mock_gmail_service.users().messages().get().execute.return_value = {
            "id": "msg123",
            "threadId": "thread123",
            "payload": {
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "me@gmail.com"},
                    {"name": "Subject", "value": "Original Subject"},
                    {"name": "Message-ID", "value": "<original@example.com>"},
                ],
            },
        }

        # Mock send response
        mock_gmail_service.users().messages().send().execute.return_value = {
            "id": "reply123",
            "threadId": "thread123",
        }

        response = gmail_client.reply_email(
            message_id="msg123",
            body="Reply body",
        )

        assert response.success is True
        assert response.thread_id == "thread123"


class TestGetThread:
    """Tests for get_thread method."""

    def test_get_thread(self, gmail_client, mock_gmail_service):
        """Test retrieving email thread."""
        import base64
        body1 = base64.urlsafe_b64encode(b"First message").decode()
        body2 = base64.urlsafe_b64encode(b"Second message").decode()

        mock_gmail_service.users().threads().get().execute.return_value = {
            "id": "thread123",
            "messages": [
                {
                    "id": "msg1",
                    "threadId": "thread123",
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "sender1@example.com"},
                            {"name": "To", "value": "recipient@example.com"},
                            {"name": "Subject", "value": "Thread Subject"},
                            {"name": "Date", "value": "Mon, 15 Jan 2025 10:30:00 +0000"},
                        ],
                        "mimeType": "text/plain",
                        "body": {"data": body1},
                    },
                    "labelIds": ["INBOX"],
                },
                {
                    "id": "msg2",
                    "threadId": "thread123",
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "sender2@example.com"},
                            {"name": "To", "value": "recipient@example.com"},
                            {"name": "Subject", "value": "Re: Thread Subject"},
                            {"name": "Date", "value": "Mon, 15 Jan 2025 11:00:00 +0000"},
                        ],
                        "mimeType": "text/plain",
                        "body": {"data": body2},
                    },
                    "labelIds": ["INBOX"],
                },
            ],
        }

        emails = gmail_client.get_thread("thread123")

        assert len(emails) == 2
        assert emails[0].message_id == "msg1"
        assert emails[1].message_id == "msg2"
        assert emails[0].body_plain == "First message"
        assert emails[1].body_plain == "Second message"


class TestModifyLabels:
    """Tests for modify_labels method."""

    def test_add_labels(self, gmail_client, mock_gmail_service):
        """Test adding labels."""
        mock_gmail_service.users().messages().modify().execute.return_value = {
            "id": "msg123",
            "labelIds": ["INBOX", "Label_1"],
        }

        result = gmail_client.modify_labels(
            message_id="msg123",
            add_labels=["Label_1"],
        )

        assert result is True

    def test_remove_labels(self, gmail_client, mock_gmail_service):
        """Test removing labels."""
        mock_gmail_service.users().messages().modify().execute.return_value = {
            "id": "msg123",
            "labelIds": ["INBOX"],
        }

        result = gmail_client.modify_labels(
            message_id="msg123",
            remove_labels=["UNREAD"],
        )

        assert result is True

    def test_modify_labels_error(self, gmail_client, mock_gmail_service):
        """Test label modification with error."""
        mock_gmail_service.users().messages().modify().execute.side_effect = Exception("Modify failed")

        result = gmail_client.modify_labels(
            message_id="msg123",
            add_labels=["Label_1"],
        )

        assert result is False


class TestDeleteEmail:
    """Tests for delete_email method."""

    def test_delete_email_trash(self, gmail_client, mock_gmail_service):
        """Test moving email to trash."""
        mock_gmail_service.users().messages().trash().execute.return_value = {
            "id": "msg123",
            "labelIds": ["TRASH"],
        }

        result = gmail_client.delete_email("msg123", permanent=False)

        assert result is True

    def test_delete_email_permanent(self, gmail_client, mock_gmail_service):
        """Test permanent email deletion."""
        mock_gmail_service.users().messages().delete().execute.return_value = None

        result = gmail_client.delete_email("msg123", permanent=True)

        assert result is True


class TestGetFolders:
    """Tests for get_folders method."""

    def test_get_folders(self, gmail_client, mock_gmail_service):
        """Test retrieving folders/labels."""
        mock_gmail_service.users().labels().list().execute.return_value = {
            "labels": [
                {
                    "id": "INBOX",
                    "name": "INBOX",
                    "type": "system",
                    "messagesTotal": 100,
                    "messagesUnread": 5,
                },
                {
                    "id": "Label_1",
                    "name": "Work",
                    "type": "user",
                    "messagesTotal": 50,
                    "messagesUnread": 2,
                },
            ],
        }

        folders = gmail_client.get_folders()

        assert len(folders) == 2
        assert folders[0].id == "INBOX"
        assert folders[0].message_count == 100
        assert folders[1].name == "Work"


class TestBatchOperations:
    """Tests for batch operations."""

    def test_batch_modify_labels_success(self, gmail_client, mock_gmail_service):
        """Test successful batch label modification."""
        mock_gmail_service.users().messages().batchModify().execute.return_value = None

        result = gmail_client.batch_modify_labels(
            message_ids=["msg1", "msg2", "msg3"],
            add_labels=["Label_1"],
        )

        assert len(result.successful) == 3
        assert len(result.failed) == 0

    def test_batch_delete_success(self, gmail_client, mock_gmail_service):
        """Test successful batch delete."""
        mock_gmail_service.users().messages().batchDelete().execute.return_value = None

        result = gmail_client.batch_delete(["msg1", "msg2"])

        assert len(result.successful) == 2
        assert len(result.failed) == 0
