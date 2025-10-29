"""Comprehensive tests for GmailClient batch operations and pagination.

This test module covers:
- Batch API operations in list_emails()
- Batch API operations in get_folders()
- Pagination with page tokens
- Large result sets
- Edge cases (empty pages, single results, last page)
- Batch request error handling
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from gmaillm.gmail_client import GmailClient


# Fixtures
@pytest.fixture
def mock_service():
    """Mock Gmail service."""
    service = MagicMock()
    return service


@pytest.fixture
def mock_client(mock_service):
    """Mock GmailClient with mocked service."""
    with patch.object(GmailClient, "_authenticate"):
        client = GmailClient()
        client.service = mock_service
        return client


# Test Classes

class TestListEmailsBatchAPI:
    """Test list_emails() batch API operations."""

    def test_list_emails_with_batch_single_result(self, mock_client, mock_service):
        """Test list_emails with batch API - single result."""
        # Mock messages.list() response
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg001"}],
            "resultSizeEstimate": 1,
        }

        # Mock batch request
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        # Simulate batch callback
        def execute_batch():
            # Find the callback that was registered
            add_call = batch_mock.add.call_args
            callback = add_call[1]["callback"]
            # Invoke callback with mock data
            callback(
                "request_id",
                {
                    "id": "msg001",
                    "threadId": "thread001",
                    "snippet": "Hello world",
                    "labelIds": ["INBOX", "UNREAD"],
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "Alice <alice@example.com>"},
                            {"name": "Subject", "value": "Test Subject"},
                            {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"},
                        ]
                    },
                },
                None,
            )

        batch_mock.execute.side_effect = execute_batch

        # Execute
        result = mock_client.list_emails(max_results=1)

        # Verify batch was used
        mock_service.new_batch_http_request.assert_called_once()
        batch_mock.add.assert_called_once()
        batch_mock.execute.assert_called_once()

        # Verify result
        assert len(result.emails) == 1
        assert result.emails[0].message_id == "msg001"
        assert result.emails[0].subject == "Test Subject"

    def test_list_emails_with_batch_multiple_results(self, mock_client, mock_service):
        """Test list_emails with batch API - multiple results."""
        # Mock messages.list() response
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": f"msg{i:03d}"} for i in range(10)],
            "resultSizeEstimate": 10,
        }

        # Mock batch request
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        batch_responses = {}

        def add_to_batch(request, callback):
            """Simulate batch.add()."""
            # Extract message ID from request
            msg_id = request._uri.split("/")[-1].split("?")[0]
            batch_responses[msg_id] = callback

        def execute_batch():
            """Simulate batch.execute() - call all callbacks."""
            for i, (msg_id, callback) in enumerate(batch_responses.items()):
                callback(
                    f"request_{i}",
                    {
                        "id": msg_id,
                        "threadId": f"thread{i:03d}",
                        "snippet": f"Message {i}",
                        "labelIds": ["INBOX"],
                        "payload": {
                            "headers": [
                                {"name": "From", "value": f"user{i}@example.com"},
                                {"name": "Subject", "value": f"Subject {i}"},
                                {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"},
                            ]
                        },
                    },
                    None,
                )

        batch_mock.add.side_effect = add_to_batch
        batch_mock.execute.side_effect = execute_batch

        # Execute
        result = mock_client.list_emails(max_results=10)

        # Verify batch was used
        assert batch_mock.add.call_count == 10
        assert batch_mock.execute.call_count == 1

        # Verify results
        assert len(result.emails) == 10
        assert result.emails[0].message_id == "msg000"
        assert result.emails[9].message_id == "msg009"

    def test_list_emails_with_batch_max_results_50(self, mock_client, mock_service):
        """Test list_emails with batch API - max_results=50 (API limit)."""
        # Mock messages.list() response
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": f"msg{i:03d}"} for i in range(50)],
            "resultSizeEstimate": 100,
            "nextPageToken": "token_page2",
        }

        # Mock batch request
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        batch_responses = {}

        def add_to_batch(request, callback):
            msg_id = request._uri.split("/")[-1].split("?")[0]
            batch_responses[msg_id] = callback

        def execute_batch():
            for i, (msg_id, callback) in enumerate(batch_responses.items()):
                callback(
                    f"request_{i}",
                    {
                        "id": msg_id,
                        "threadId": f"thread{i:03d}",
                        "snippet": f"Message {i}",
                        "labelIds": ["INBOX"],
                        "payload": {
                            "headers": [
                                {"name": "From", "value": f"user{i}@example.com"},
                                {"name": "Subject", "value": f"Subject {i}"},
                                {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"},
                            ]
                        },
                    },
                    None,
                )

        batch_mock.add.side_effect = add_to_batch
        batch_mock.execute.side_effect = execute_batch

        # Execute
        result = mock_client.list_emails(max_results=50)

        # Verify
        assert len(result.emails) == 50
        assert result.next_page_token == "token_page2"
        assert result.total_count == 100

    def test_list_emails_with_batch_empty_folder(self, mock_client, mock_service):
        """Test list_emails with batch API - empty folder."""
        # Mock messages.list() response
        mock_service.users().messages().list().execute.return_value = {
            "messages": [],
            "resultSizeEstimate": 0,
        }

        # Mock batch request (should not be used)
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        # Execute
        result = mock_client.list_emails()

        # Verify batch was NOT used for empty result
        mock_service.new_batch_http_request.assert_not_called()
        batch_mock.add.assert_not_called()
        batch_mock.execute.assert_not_called()

        # Verify result
        assert len(result.emails) == 0
        assert result.total_count == 0

    def test_list_emails_with_batch_partial_failures(self, mock_client, mock_service):
        """Test list_emails with batch API - some requests fail."""
        # Mock messages.list() response
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": f"msg{i:03d}"} for i in range(5)],
            "resultSizeEstimate": 5,
        }

        # Mock batch request
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        batch_responses = {}

        def add_to_batch(request, callback):
            msg_id = request._uri.split("/")[-1].split("?")[0]
            batch_responses[msg_id] = callback

        def execute_batch():
            """Simulate batch with failures on msg001 and msg003."""
            for i, (msg_id, callback) in enumerate(batch_responses.items()):
                if msg_id in ["msg001", "msg003"]:
                    # Simulate failure
                    callback(f"request_{i}", None, Exception("API Error"))
                else:
                    # Success
                    callback(
                        f"request_{i}",
                        {
                            "id": msg_id,
                            "threadId": f"thread{i:03d}",
                            "snippet": f"Message {i}",
                            "labelIds": ["INBOX"],
                            "payload": {
                                "headers": [
                                    {"name": "From", "value": f"user{i}@example.com"},
                                    {"name": "Subject", "value": f"Subject {i}"},
                                    {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"},
                                ]
                            },
                        },
                        None,
                    )

        batch_mock.add.side_effect = add_to_batch
        batch_mock.execute.side_effect = execute_batch

        # Execute
        result = mock_client.list_emails(max_results=5)

        # Verify only successful messages are returned
        assert len(result.emails) == 3  # 5 total - 2 failures
        assert result.emails[0].message_id == "msg000"
        assert result.emails[1].message_id == "msg002"
        assert result.emails[2].message_id == "msg004"


class TestListEmailsPagination:
    """Test list_emails() pagination."""

    def test_list_emails_with_page_token(self, mock_client, mock_service):
        """Test list_emails with page_token for pagination."""
        # Mock messages.list() response for page 2
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg010"}, {"id": "msg011"}],
            "resultSizeEstimate": 20,
            "nextPageToken": "token_page3",
        }

        # Mock batch
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        def execute_batch():
            add_call = batch_mock.add.call_args_list[0]
            callback = add_call[1]["callback"]
            callback(
                "req0",
                {
                    "id": "msg010",
                    "threadId": "thread010",
                    "snippet": "Page 2 msg 1",
                    "labelIds": ["INBOX"],
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "user@example.com"},
                            {"name": "Subject", "value": "Subject 10"},
                            {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"},
                        ]
                    },
                },
                None,
            )
            add_call = batch_mock.add.call_args_list[1]
            callback = add_call[1]["callback"]
            callback(
                "req1",
                {
                    "id": "msg011",
                    "threadId": "thread011",
                    "snippet": "Page 2 msg 2",
                    "labelIds": ["INBOX"],
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "user@example.com"},
                            {"name": "Subject", "value": "Subject 11"},
                            {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"},
                        ]
                    },
                },
                None,
            )

        batch_mock.execute.side_effect = execute_batch

        # Execute with page token
        result = mock_client.list_emails(page_token="token_page2")

        # Verify page token was passed
        call_kwargs = mock_service.users().messages().list.call_args[1]
        assert call_kwargs["pageToken"] == "token_page2"

        # Verify results
        assert len(result.emails) == 2
        assert result.next_page_token == "token_page3"

    def test_list_emails_last_page_no_next_token(self, mock_client, mock_service):
        """Test list_emails on last page - no next_page_token."""
        # Mock messages.list() response
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg099"}],
            "resultSizeEstimate": 100,
            # No nextPageToken - this is the last page
        }

        # Mock batch
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        def execute_batch():
            add_call = batch_mock.add.call_args
            callback = add_call[1]["callback"]
            callback(
                "req",
                {
                    "id": "msg099",
                    "threadId": "thread099",
                    "snippet": "Last message",
                    "labelIds": ["INBOX"],
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "user@example.com"},
                            {"name": "Subject", "value": "Last Subject"},
                            {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"},
                        ]
                    },
                },
                None,
            )

        batch_mock.execute.side_effect = execute_batch

        # Execute
        result = mock_client.list_emails()

        # Verify no next page token
        assert result.next_page_token is None
        assert len(result.emails) == 1


class TestGetFoldersBatchAPI:
    """Test get_folders() batch API operations."""

    def test_get_folders_with_batch(self, mock_client, mock_service):
        """Test get_folders with batch API."""
        # Mock labels.list() response
        mock_service.users().labels().list().execute.return_value = {
            "labels": [
                {"id": "INBOX", "name": "INBOX", "type": "system"},
                {"id": "SENT", "name": "SENT", "type": "system"},
                {"id": "Label_1", "name": "Work", "type": "user"},
            ]
        }

        # Mock batch request
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        batch_responses = {}

        def add_to_batch(request, callback):
            """Simulate batch.add()."""
            # Extract label ID from request
            label_id = request._uri.split("/")[-1]
            batch_responses[label_id] = callback

        def execute_batch():
            """Simulate batch.execute() - call all callbacks."""
            label_data = {
                "INBOX": {"id": "INBOX", "name": "INBOX", "type": "system", "messagesTotal": 50, "messagesUnread": 5},
                "SENT": {"id": "SENT", "name": "SENT", "type": "system", "messagesTotal": 30, "messagesUnread": 0},
                "Label_1": {"id": "Label_1", "name": "Work", "type": "user", "messagesTotal": 10, "messagesUnread": 2},
            }
            for label_id, callback in batch_responses.items():
                callback("req", label_data[label_id], None)

        batch_mock.add.side_effect = add_to_batch
        batch_mock.execute.side_effect = execute_batch

        # Execute
        folders = mock_client.get_folders()

        # Verify batch was used
        assert batch_mock.add.call_count == 3
        assert batch_mock.execute.call_count == 1

        # Verify results
        assert len(folders) == 3
        assert folders[0].id == "INBOX"
        assert folders[0].message_count == 50
        assert folders[0].unread_count == 5
        assert folders[2].name == "Work"

    def test_get_folders_with_batch_partial_failures(self, mock_client, mock_service):
        """Test get_folders with batch API - some requests fail."""
        # Mock labels.list() response
        mock_service.users().labels().list().execute.return_value = {
            "labels": [
                {"id": "INBOX", "name": "INBOX", "type": "system"},
                {"id": "SENT", "name": "SENT", "type": "system"},
                {"id": "Label_1", "name": "Work", "type": "user"},
            ]
        }

        # Mock batch request
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        batch_responses = {}

        def add_to_batch(request, callback):
            label_id = request._uri.split("/")[-1]
            batch_responses[label_id] = callback

        def execute_batch():
            """Simulate batch with failure on SENT."""
            for label_id, callback in batch_responses.items():
                if label_id == "SENT":
                    # Simulate failure - callback should create fallback data
                    callback("req", None, Exception("API Error"))
                else:
                    # Success
                    label_data = {
                        "INBOX": {"id": "INBOX", "name": "INBOX", "type": "system", "messagesTotal": 50, "messagesUnread": 5},
                        "Label_1": {"id": "Label_1", "name": "Work", "type": "user", "messagesTotal": 10, "messagesUnread": 2},
                    }
                    callback("req", label_data[label_id], None)

        batch_mock.add.side_effect = add_to_batch
        batch_mock.execute.side_effect = execute_batch

        # Execute
        folders = mock_client.get_folders()

        # Verify all folders returned (including failed one with fallback data)
        assert len(folders) == 3

        # INBOX and Work should have full data
        inbox = next(f for f in folders if f.id == "INBOX")
        assert inbox.message_count == 50

        work = next(f for f in folders if f.id == "Label_1")
        assert work.message_count == 10

        # SENT should have fallback data (None counts)
        sent = next(f for f in folders if f.id == "SENT")
        assert sent.message_count is None
        assert sent.unread_count is None

    def test_get_folders_empty_labels_list(self, mock_client, mock_service):
        """Test get_folders with empty labels list."""
        # Mock labels.list() response
        mock_service.users().labels().list().execute.return_value = {"labels": []}

        # Mock batch request (should not be used)
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        # Execute
        folders = mock_client.get_folders()

        # Verify batch was NOT used for empty result
        mock_service.new_batch_http_request.assert_not_called()

        # Verify result
        assert len(folders) == 0


class TestBatchAPIEdgeCases:
    """Test batch API edge cases."""

    def test_list_emails_batch_with_malformed_response(self, mock_client, mock_service):
        """Test list_emails batch API with malformed response."""
        # Mock messages.list() response
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg001"}],
            "resultSizeEstimate": 1,
        }

        # Mock batch request
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        def execute_batch():
            add_call = batch_mock.add.call_args
            callback = add_call[1]["callback"]
            # Return malformed response (missing required fields)
            callback(
                "req",
                {
                    "id": "msg001",
                    "threadId": "thread001",
                    # Missing snippet, labelIds, payload
                },
                None,
            )

        batch_mock.execute.side_effect = execute_batch

        # Execute - should handle gracefully
        result = mock_client.list_emails(max_results=1)

        # Should still return result (with defaults for missing fields)
        assert len(result.emails) == 1

    def test_get_folders_batch_with_missing_counts(self, mock_client, mock_service):
        """Test get_folders batch API with missing message counts."""
        # Mock labels.list() response
        mock_service.users().labels().list().execute.return_value = {
            "labels": [{"id": "INBOX", "name": "INBOX", "type": "system"}]
        }

        # Mock batch request
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        def add_to_batch(request, callback):
            batch_responses = {}
            label_id = request._uri.split("/")[-1]
            batch_responses[label_id] = callback

        def execute_batch():
            add_call = batch_mock.add.call_args
            callback = add_call[1]["callback"]
            # Return response without messagesTotal/messagesUnread
            callback(
                "req",
                {
                    "id": "INBOX",
                    "name": "INBOX",
                    "type": "system",
                    # Missing messagesTotal and messagesUnread
                },
                None,
            )

        batch_mock.add.side_effect = add_to_batch
        batch_mock.execute.side_effect = execute_batch

        # Execute
        folders = mock_client.get_folders()

        # Should handle missing counts gracefully
        assert len(folders) == 1
        assert folders[0].message_count is None
        assert folders[0].unread_count is None


class TestPaginationValidation:
    """Test pagination parameter validation."""

    def test_list_emails_invalid_max_results_zero(self, mock_client):
        """Test list_emails with max_results=0."""
        with pytest.raises(ValueError, match="max_results must be between 1 and 50"):
            mock_client.list_emails(max_results=0)

    def test_list_emails_invalid_max_results_negative(self, mock_client):
        """Test list_emails with negative max_results."""
        with pytest.raises(ValueError, match="max_results must be between 1 and 50"):
            mock_client.list_emails(max_results=-1)

    def test_list_emails_invalid_max_results_too_large(self, mock_client):
        """Test list_emails with max_results > 50."""
        with pytest.raises(ValueError, match="max_results must be between 1 and 50"):
            mock_client.list_emails(max_results=51)

    def test_list_emails_valid_max_results_boundary(self, mock_client, mock_service):
        """Test list_emails with max_results at valid boundaries (1 and 50)."""
        # Test max_results=1
        mock_service.users().messages().list().execute.return_value = {
            "messages": [],
            "resultSizeEstimate": 0,
        }
        result = mock_client.list_emails(max_results=1)
        assert result is not None

        # Test max_results=50
        result = mock_client.list_emails(max_results=50)
        assert result is not None


class TestSearchWithBatch:
    """Test search_emails() with batch API."""

    def test_search_emails_uses_list_emails_batch(self, mock_client, mock_service):
        """Test search_emails delegates to list_emails and uses batch API."""
        # Mock messages.list() response
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg001"}],
            "resultSizeEstimate": 1,
        }

        # Mock batch
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        def execute_batch():
            add_call = batch_mock.add.call_args
            callback = add_call[1]["callback"]
            callback(
                "req",
                {
                    "id": "msg001",
                    "threadId": "thread001",
                    "snippet": "Search result",
                    "labelIds": ["INBOX"],
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "alice@example.com"},
                            {"name": "Subject", "value": "Urgent"},
                            {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"},
                        ]
                    },
                },
                None,
            )

        batch_mock.execute.side_effect = execute_batch

        # Execute search
        result = mock_client.search_emails(query="is:urgent")

        # Verify batch was used
        batch_mock.execute.assert_called_once()

        # Verify result
        assert len(result.emails) == 1
        assert result.emails[0].message_id == "msg001"
