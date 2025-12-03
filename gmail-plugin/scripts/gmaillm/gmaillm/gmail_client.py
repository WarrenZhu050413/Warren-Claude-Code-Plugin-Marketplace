"""Gmail API client with LLM-friendly interface."""

import fcntl
import json
import logging
import os
import re
from datetime import datetime
from email.utils import getaddresses
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union, overload

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import get_credentials_file, get_oauth_keys_file
from .models import (
    Attachment,
    EmailAddress,
    EmailFull,
    EmailSummary,
    Folder,
    SearchResult,
    SendEmailRequest,
    SendEmailResponse,
)
from .utils import (
    clean_snippet,
    create_mime_message,
    extract_body,
    get_header,
    parse_email_address,
    parse_label_ids,
    validate_pagination_params,
)

# Get logger for this module (don't call basicConfig - let application configure it)
logger = logging.getLogger(__name__)

# Constants
MAX_LABEL_NAME_LENGTH = 100
VALID_LABEL_CHARS_PATTERN = re.compile(r"^[\w\-. /]+$")
MAX_QUERY_LENGTH = 1000


class GmailClient:
    """LLM-friendly Gmail API client with progressive disclosure and pagination."""

    def __init__(
        self,
        credentials_file: Optional[str] = None,
        oauth_keys_file: Optional[str] = None,
    ) -> None:
        """Initialize Gmail client with OAuth2 credentials.

        Args:
            credentials_file: Path to saved OAuth2 credentials (default: ~/.gmaillm/credentials.json)
            oauth_keys_file: Path to OAuth2 client secrets (default: ~/.gmaillm/oauth-keys.json)

        """
        # Use config module defaults if not provided
        self.credentials_file = credentials_file or str(get_credentials_file())
        self.oauth_keys_file = oauth_keys_file or str(get_oauth_keys_file())
        self.service = None
        self._authenticate()

    def _validate_file_exists_and_nonempty(self, file_path: str, file_type: str) -> None:
        """Validate file exists and is not empty.

        Args:
            file_path: Path to file to validate
            file_type: Human-readable file type for error messages

        Raises:
            FileNotFoundError: If file does not exist
            RuntimeError: If file cannot be accessed or is empty

        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_type} file not found: {file_path}")

        try:
            file_size = os.path.getsize(file_path)
        except (OSError, PermissionError) as e:
            raise RuntimeError(f"Cannot access {file_type} file: {file_path}\nError: {e}")

        if file_size == 0:
            error_msg = f"{file_type} file is empty: {file_path}\n\n"
            if file_type == "Credentials":
                error_msg += (
                    "You need to authenticate first. Run this command:\n"
                    "  gmail setup-auth\n\n"
                    "This will guide you through the OAuth2 authentication process."
                )
            else:
                error_msg += (
                    "Please ensure OAuth2 client secrets are available.\n"
                    "Follow the Gmail MCP setup instructions."
                )
            raise RuntimeError(error_msg)

    def _load_json_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Load and parse JSON file with error handling.

        Args:
            file_path: Path to JSON file
            file_type: Human-readable file type for error messages

        Returns:
            Parsed JSON data as dictionary

        Raises:
            RuntimeError: If file cannot be read or parsed

        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            error_msg = (
                f"Invalid JSON in {file_type} file: {file_path}\n"
                f"The file may be corrupted. Error: {e}\n\n"
            )
            if file_type == "Credentials":
                error_msg += "Try re-authenticating with: gmail setup-auth"
            else:
                error_msg += "Please ensure the file contains valid JSON."
            raise RuntimeError(error_msg)
        except (OSError, PermissionError) as e:
            raise RuntimeError(f"Error reading {file_type} file: {file_path}\nError: {e}")

    def _load_oauth_keys(self) -> Dict[str, Any]:
        """Load OAuth keys from file.

        Returns:
            OAuth keys dictionary

        Raises:
            RuntimeError: If file validation or loading fails

        """
        self._validate_file_exists_and_nonempty(self.oauth_keys_file, "OAuth keys")
        oauth_keys = self._load_json_file(self.oauth_keys_file, "OAuth keys")

        # Unwrap if nested under "installed"
        if "installed" in oauth_keys:
            return oauth_keys["installed"]
        return oauth_keys

    def _load_credentials(self) -> Dict[str, Any]:
        """Load credentials from file.

        Returns:
            Credentials dictionary

        Raises:
            RuntimeError: If file validation or loading fails

        """
        self._validate_file_exists_and_nonempty(self.credentials_file, "Credentials")
        return self._load_json_file(self.credentials_file, "Credentials")

    def _refresh_credentials_if_needed(self, creds: Credentials) -> None:
        """Refresh credentials if expired.

        Args:
            creds: Google OAuth2 credentials object

        Raises:
            RuntimeError: If credential refresh fails

        """
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())

                # Use file locking to prevent race conditions
                lock_path = f"{self.credentials_file}.lock"
                Path(lock_path).touch(exist_ok=True)

                try:
                    with open(lock_path, "w", encoding="utf-8") as lock_file:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                        try:
                            with open(self.credentials_file, "w", encoding="utf-8") as f:
                                f.write(creds.to_json())
                        finally:
                            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                finally:
                    # Clean up lock file
                    try:
                        os.unlink(lock_path)
                    except OSError:
                        pass

            except (OSError, PermissionError) as e:
                raise RuntimeError(
                    f"Failed to save refreshed credentials: {e}\n"
                    f"Check file permissions for {self.credentials_file}"
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to refresh credentials: {e}\n"
                    f"You may need to re-authenticate with Gmail MCP."
                )

    def _authenticate(self) -> None:
        """Authenticate with Gmail API using existing credentials.

        Raises:
            RuntimeError: If authentication fails
            KeyError: If required OAuth fields are missing

        """
        # Load OAuth keys and credentials
        oauth_keys = self._load_oauth_keys()
        creds_data = self._load_credentials()

        # Validate required OAuth fields exist
        try:
            client_id = oauth_keys["client_id"]
            client_secret = oauth_keys["client_secret"]
        except KeyError as e:
            raise KeyError(
                f"Missing required OAuth field: {e}\n"
                f"Please ensure your OAuth keys file contains 'client_id' and 'client_secret'"
            )

        # Merge OAuth keys with credentials
        creds_data["client_id"] = client_id
        creds_data["client_secret"] = client_secret

        # Create credentials object
        creds = Credentials.from_authorized_user_info(creds_data)

        # Refresh if needed
        self._refresh_credentials_if_needed(creds)

        # Build service
        self.service = build("gmail", "v1", credentials=creds)

    def _parse_message_to_summary(self, msg_data: Dict[str, Any]) -> EmailSummary:
        """Parse Gmail API message into EmailSummary.

        Args:
            msg_data: Raw message data from Gmail API

        Returns:
            EmailSummary object

        """
        msg_id = msg_data["id"]
        thread_id = msg_data["threadId"]
        snippet = clean_snippet(msg_data.get("snippet", ""))

        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])

        # Extract headers
        from_header = get_header(headers, "From") or ""
        subject = get_header(headers, "Subject") or "(No subject)"
        date_str = get_header(headers, "Date") or ""

        # Parse date with proper fallback
        date: Optional[datetime] = None
        if date_str:
            try:
                from email.utils import parsedate_to_datetime

                date = parsedate_to_datetime(date_str)
            except (ValueError, TypeError, OverflowError) as e:
                logger.warning(f"Failed to parse date '{date_str}' for message {msg_id}: {e}")

        # If date parsing failed, use None or current time as last resort
        if date is None:
            logger.warning(f"No valid date for message {msg_id}, using current time")
            date = datetime.now()

        # Parse from address
        from_parsed = parse_email_address(from_header)

        # Get labels and flags
        label_ids = msg_data.get("labelIds", [])
        flags = parse_label_ids(label_ids)

        # Check for attachments
        has_attachments = self._has_attachments(payload)

        return EmailSummary(
            message_id=msg_id,
            thread_id=thread_id,
            **{"from": EmailAddress(**from_parsed)},
            subject=subject,
            date=date,
            snippet=snippet,
            labels=label_ids,
            has_attachments=has_attachments,
            is_unread=flags["is_unread"],
        )

    def _parse_message_to_full(self, msg_data: Dict[str, Any]) -> EmailFull:
        """Parse Gmail API message into EmailFull.

        Args:
            msg_data: Raw message data from Gmail API

        Returns:
            EmailFull object

        """
        msg_id = msg_data["id"]
        thread_id = msg_data["threadId"]

        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])

        # Extract all headers into dict
        headers_dict = {h["name"]: h["value"] for h in headers}

        # Extract key headers
        from_header = get_header(headers, "From") or ""
        to_header = get_header(headers, "To") or ""
        cc_header = get_header(headers, "Cc") or ""
        bcc_header = get_header(headers, "Bcc") or ""
        subject = get_header(headers, "Subject") or "(No subject)"
        date_str = get_header(headers, "Date") or ""
        in_reply_to = get_header(headers, "In-Reply-To")
        references = get_header(headers, "References") or ""

        # Parse date with proper fallback
        date: Optional[datetime] = None
        if date_str:
            try:
                from email.utils import parsedate_to_datetime

                date = parsedate_to_datetime(date_str)
            except (ValueError, TypeError, OverflowError) as e:
                logger.warning(f"Failed to parse date '{date_str}' for message {msg_id}: {e}")

        # If date parsing failed, use None or current time as last resort
        if date is None:
            logger.warning(f"No valid date for message {msg_id}, using current time")
            date = datetime.now()

        # Parse email addresses
        # Use email.utils.getaddresses to properly handle commas in quoted names
        from_parsed = parse_email_address(from_header)

        # Parse To addresses
        to_addresses = getaddresses([to_header]) if to_header else []
        to_list = [
            EmailAddress(
                email=email.strip(),
                name=name.strip() if name else None
            )
            for name, email in to_addresses
            if email.strip()
        ]

        # Parse CC addresses
        cc_addresses = getaddresses([cc_header]) if cc_header else []
        cc_list = [
            EmailAddress(
                email=email.strip(),
                name=name.strip() if name else None
            )
            for name, email in cc_addresses
            if email.strip()
        ]

        # Parse BCC addresses
        bcc_addresses = getaddresses([bcc_header]) if bcc_header else []
        bcc_list = [
            EmailAddress(
                email=email.strip(),
                name=name.strip() if name else None
            )
            for name, email in bcc_addresses
            if email.strip()
        ]

        # Extract body
        plain_body, html_body = extract_body(payload)

        # Extract attachments
        attachments = self._extract_attachments(payload)

        # Get labels
        label_ids = msg_data.get("labelIds", [])

        # Parse references
        ref_list = [ref.strip() for ref in references.split() if ref.strip()]

        return EmailFull(
            message_id=msg_id,
            thread_id=thread_id,
            **{"from": EmailAddress(**from_parsed)},
            to=to_list,
            cc=cc_list,
            bcc=bcc_list,
            subject=subject,
            date=date,
            body_plain=plain_body,
            body_html=html_body,
            attachments=attachments,
            labels=label_ids,
            headers=headers_dict,
            in_reply_to=in_reply_to,
            references=ref_list,
        )

    def _has_attachments(self, payload: Dict[str, Any]) -> bool:
        """Check if message has attachments.

        Args:
            payload: Gmail API message payload

        Returns:
            True if message has attachments, False otherwise

        """

        def check_part(part: Dict[str, Any]) -> bool:
            if part.get("filename") and part.get("body", {}).get("attachmentId"):
                return True
            if "parts" in part:
                return any(check_part(p) for p in part["parts"])
            return False

        return check_part(payload)

    def _extract_attachments(self, payload: Dict[str, Any]) -> List[Attachment]:
        """Extract attachment metadata from payload.

        Args:
            payload: Gmail API message payload

        Returns:
            List of Attachment objects

        """
        attachments: List[Attachment] = []

        def extract_from_part(part: Dict[str, Any]) -> None:
            filename = part.get("filename", "")
            body = part.get("body", {})
            attachment_id = body.get("attachmentId")

            if filename and attachment_id:
                attachments.append(
                    Attachment(
                        filename=filename,
                        mime_type=part.get("mimeType", "application/octet-stream"),
                        size=body.get("size", 0),
                        attachment_id=attachment_id,
                    )
                )

            # Recurse into parts
            if "parts" in part:
                for subpart in part["parts"]:
                    extract_from_part(subpart)

        if "parts" in payload:
            for part in payload["parts"]:
                extract_from_part(part)

        return attachments

    def _validate_query(self, query: str) -> None:
        """Validate Gmail search query for safety.

        Args:
            query: Gmail search query string

        Raises:
            ValueError: If query is invalid or potentially malicious

        """
        if not query:
            return

        if len(query) > MAX_QUERY_LENGTH:
            raise ValueError(f"Query too long: {len(query)} chars (max {MAX_QUERY_LENGTH})")

        # Check for suspicious characters that could indicate injection attempts
        suspicious_patterns = [
            r"\x00",  # null bytes
            r"[\x01-\x08\x0b\x0c\x0e-\x1f]",  # control characters
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, query):
                raise ValueError("Query contains invalid control characters")

    def _validate_label_name(self, name: str) -> None:
        """Validate label name for Gmail API requirements.

        Args:
            name: Label name to validate

        Raises:
            ValueError: If label name is invalid

        """
        if not name:
            raise ValueError("Label name cannot be empty")

        if len(name) > MAX_LABEL_NAME_LENGTH:
            raise ValueError(
                f"Label name too long: {len(name)} chars (max {MAX_LABEL_NAME_LENGTH})"
            )

        # Gmail label names can contain letters, numbers, spaces, dashes, underscores, dots, slashes
        if not VALID_LABEL_CHARS_PATTERN.match(name):
            raise ValueError(
                "Label name contains invalid characters. "
                "Allowed: letters, numbers, spaces, dashes, underscores, dots, slashes"
            )

    def _validate_label_ids(self, label_ids: List[str]) -> None:
        """Validate label IDs.

        Args:
            label_ids: List of label IDs to validate

        Raises:
            ValueError: If any label ID is invalid

        """
        if not label_ids:
            return

        for label_id in label_ids:
            if not label_id or not isinstance(label_id, str):
                raise ValueError(f"Invalid label ID: {label_id}")

            # Label IDs should be alphanumeric or Gmail system labels (all caps)
            if not re.match(r"^[A-Za-z0-9_-]+$", label_id):
                raise ValueError(f"Label ID contains invalid characters: {label_id}")

    def list_emails(
        self,
        folder: str = "INBOX",
        max_results: int = 10,
        page_token: Optional[str] = None,
        query: Optional[str] = None,
    ) -> SearchResult:
        """List emails from a folder with pagination.

        Args:
            folder: Gmail label/folder (default: INBOX)
            max_results: Maximum results per page (1-50, default: 10)
            page_token: Token for next page of results
            query: Gmail search query (optional)

        Returns:
            SearchResult with email summaries and pagination info

        Raises:
            ValueError: If query is invalid
            RuntimeError: If API request fails

        """
        max_results = validate_pagination_params(max_results)

        # Validate query if provided
        if query:
            self._validate_query(query)

        # Build query
        search_query = f"label:{folder}"
        if query:
            search_query = f"{search_query} {query}"

        try:
            # List messages
            result = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    q=search_query,
                    maxResults=max_results,
                    pageToken=page_token,
                )
                .execute()
            )

            messages = result.get("messages", [])
            next_page = result.get("nextPageToken")
            total_estimate = result.get("resultSizeEstimate", len(messages))

            # Fetch full message data for summaries using batch API
            summaries: List[EmailSummary] = []

            if not messages:
                # No messages to fetch
                pass
            else:
                # Use batch request to fetch all messages at once
                batch = self.service.new_batch_http_request()

                # Track results and errors
                batch_results: Dict[str, Any] = {}

                def make_callback(msg_id: str) -> Any:
                    """Create callback for this specific message."""
                    def callback(request_id: str, response: Any, exception: Exception) -> None:
                        if exception:
                            logger.warning(f"Failed to fetch message {msg_id}: {exception}")
                        else:
                            batch_results[msg_id] = response
                    return callback

                # Add all message fetch requests to batch
                for msg in messages:
                    msg_id = msg["id"]
                    batch.add(
                        self.service.users()
                        .messages()
                        .get(
                            userId="me",
                            id=msg_id,
                            format="metadata",
                            metadataHeaders=["From", "To", "Cc", "Subject", "Date"],
                        ),
                        callback=make_callback(msg_id),
                    )

                # Execute all requests in one batch
                batch.execute()

                # Parse results in original order
                for msg in messages:
                    msg_id = msg["id"]
                    if msg_id in batch_results:
                        summaries.append(self._parse_message_to_summary(batch_results[msg_id]))

            return SearchResult(
                emails=summaries,
                total_count=total_estimate,
                next_page_token=next_page,
                query=search_query,
            )

        except HttpError as e:
            raise RuntimeError(f"Failed to list emails: {e}")

    @overload
    def read_email(
        self,
        message_id: str,
        format: Literal["summary"] = "summary",
    ) -> EmailSummary: ...

    @overload
    def read_email(
        self,
        message_id: str,
        format: Literal["headers"],
    ) -> EmailFull: ...

    @overload
    def read_email(
        self,
        message_id: str,
        format: Literal["full"],
    ) -> EmailFull: ...

    def read_email(
        self,
        message_id: str,
        format: Literal["summary", "headers", "full"] = "summary",
    ) -> Union[EmailSummary, EmailFull]:
        """Read an email with progressive disclosure.

        Args:
            message_id: Gmail message ID
            format: Output format - "summary" (brief), "headers" (summary + headers), "full" (complete)

        Returns:
            EmailSummary or EmailFull depending on format

        Raises:
            ValueError: If format is invalid
            RuntimeError: If API request fails

        """
        try:
            msg_data = (
                self.service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="full",
                )
                .execute()
            )

            if format == "summary":
                return self._parse_message_to_summary(msg_data)
            elif format in ("headers", "full"):
                return self._parse_message_to_full(msg_data)
            else:
                raise ValueError(f"Invalid format: {format}")

        except HttpError as e:
            raise RuntimeError(f"Failed to read email {message_id}: {e}")

    def search_emails(
        self,
        query: str,
        folder: str = "INBOX",
        max_results: int = 10,
        page_token: Optional[str] = None,
    ) -> SearchResult:
        """Search emails using Gmail search syntax.

        Args:
            query: Gmail search query (e.g., "from:[email protected]", "has:attachment")
            folder: Gmail label/folder to search in (default: INBOX)
            max_results: Maximum results per page (1-50, default: 10)
            page_token: Token for next page of results

        Returns:
            SearchResult with matching email summaries

        Raises:
            ValueError: If query is invalid
            RuntimeError: If API request fails

        """
        return self.list_emails(
            folder=folder,
            max_results=max_results,
            page_token=page_token,
            query=query,
        )

    def get_folders(self) -> List[Folder]:
        """Get list of all Gmail labels/folders.

        Returns:
            List of Folder objects with metadata

        Raises:
            RuntimeError: If API request fails

        """
        try:
            # First, get the list of all labels
            result = self.service.users().labels().list(userId="me").execute()
            labels = result.get("labels", [])

            folders: List[Folder] = []

            if not labels:
                # No labels to fetch
                pass
            else:
                # Use batch request to fetch all label details at once
                # Note: labels.list() does NOT return messagesTotal/messagesUnread
                # We need to call labels.get() for each label to get counts
                batch = self.service.new_batch_http_request()

                # Track results
                batch_results: Dict[str, Any] = {}

                def make_callback(label_id: str, label_name: str, label_type: str) -> Any:
                    """Create callback for this specific label."""
                    def callback(request_id: str, response: Any, exception: Exception) -> None:
                        if exception:
                            logger.warning(f"Failed to get details for label {label_name}: {exception}")
                            # Store fallback data
                            batch_results[label_id] = {
                                "id": label_id,
                                "name": label_name,
                                "type": label_type,
                                "messagesTotal": None,
                                "messagesUnread": None,
                            }
                        else:
                            batch_results[label_id] = response
                    return callback

                # Add all label fetch requests to batch
                for label in labels:
                    label_id = label["id"]
                    batch.add(
                        self.service.users().labels().get(userId="me", id=label_id),
                        callback=make_callback(label_id, label.get("name", "unknown"), label.get("type", "user")),
                    )

                # Execute all requests in one batch
                batch.execute()

                # Parse results in original order
                for label in labels:
                    label_id = label["id"]
                    if label_id in batch_results:
                        full_label = batch_results[label_id]
                        folder = Folder(
                            id=full_label["id"],
                            name=full_label["name"],
                            type=full_label["type"].lower(),
                            message_count=full_label.get("messagesTotal"),
                            unread_count=full_label.get("messagesUnread"),
                        )
                        folders.append(folder)

            return folders

        except HttpError as e:
            raise RuntimeError(f"Failed to get folders: {e}")

    def create_label(self, name: str, visibility: str = "labelShow") -> Folder:
        """Create a new Gmail label/folder.

        Args:
            name: Name of the label to create
            visibility: Label visibility ('labelShow', 'labelShowIfUnread', 'labelHide')

        Returns:
            Folder object for the newly created label

        Raises:
            ValueError: If label name is invalid
            RuntimeError: If API request fails

        """
        # Validate label name
        self._validate_label_name(name)

        try:
            label_object = {
                "name": name,
                "labelListVisibility": visibility,
                "messageListVisibility": "show",
            }

            result = self.service.users().labels().create(userId="me", body=label_object).execute()

            return Folder(
                id=result["id"],
                name=result["name"],
                type=result["type"].lower(),
                message_count=result.get("messagesTotal"),
                unread_count=result.get("messagesUnread"),
            )

        except HttpError as e:
            raise RuntimeError(f"Failed to create label '{name}': {e}")

    def verify_setup(self) -> Dict[str, Any]:
        """Verify authentication and basic Gmail API functionality.

        Returns:
            Dictionary with setup status:
            {
                'auth': bool,
                'email_address': str,
                'folders': int,
                'inbox_accessible': bool,
                'errors': List[str]
            }

        """
        results: Dict[str, Any] = {
            "auth": False,
            "email_address": None,
            "folders": 0,
            "inbox_accessible": False,
            "errors": [],
        }

        try:
            # Test authentication by getting user profile
            profile = self.service.users().getProfile(userId="me").execute()
            results["auth"] = True
            results["email_address"] = profile.get("emailAddress")

            # Test folder access
            folders = self.get_folders()
            results["folders"] = len(folders)

            # Test inbox read access
            self.list_emails(folder="INBOX", max_results=1)
            results["inbox_accessible"] = True

        except HttpError as e:
            results["errors"].append(f"Gmail API error: {str(e)}")
        except (OSError, PermissionError) as e:
            results["errors"].append(f"File access error: {str(e)}")
        except Exception as e:
            results["errors"].append(f"Unexpected error: {str(e)}")

        return results

    def get_thread(self, message_id: str) -> List[EmailSummary]:
        """Get all emails in a thread.

        Args:
            message_id: ID of any message in the thread

        Returns:
            List of EmailSummary objects in chronological order

        Raises:
            RuntimeError: If API request fails

        """
        try:
            # First get the message to find its thread_id
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="minimal")
                .execute()
            )

            thread_id = msg["threadId"]

            # Get the full thread
            thread = self.service.users().threads().get(userId="me", id=thread_id).execute()

            # Parse all messages in thread
            messages: List[EmailSummary] = []
            for msg_data in thread.get("messages", []):
                email_summary = self._parse_message_to_summary(msg_data)
                messages.append(email_summary)

            # Sort by date (should already be sorted, but ensure it)
            messages.sort(key=lambda x: x.date)

            return messages

        except HttpError as e:
            raise RuntimeError(f"Failed to get thread: {e}")

    def get_thread_full(self, message_id: str) -> List[EmailFull]:
        """Get all emails in a thread with full details.

        Args:
            message_id: ID of any message in the thread

        Returns:
            List of EmailFull objects in chronological order

        Raises:
            RuntimeError: If API request fails

        """
        try:
            # First get the message to find its thread_id
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="minimal")
                .execute()
            )

            thread_id = msg["threadId"]

            # Get the full thread
            thread = self.service.users().threads().get(userId="me", id=thread_id).execute()

            # Parse all messages in thread with full details
            messages: List[EmailFull] = []
            for msg_data in thread.get("messages", []):
                email_full = self._parse_message_to_full(msg_data)
                messages.append(email_full)

            # Sort by date (should already be sorted, but ensure it)
            messages.sort(key=lambda x: x.date)

            return messages

        except HttpError as e:
            raise RuntimeError(f"Failed to get thread: {e}")

    def send_email(self, request: SendEmailRequest) -> SendEmailResponse:
        """Send an email.

        Args:
            request: SendEmailRequest with email details

        Returns:
            SendEmailResponse with message ID and status

        """
        try:
            # Create MIME message
            mime_message = create_mime_message(
                to=request.to,
                subject=request.subject,
                body=request.body,
                from_=request.from_,
                cc=request.cc,
                bcc=request.bcc,
                reply_to=request.reply_to,
                in_reply_to=request.in_reply_to,
                attachments=request.attachments,
                is_html=request.is_html,
            )

            # Send via Gmail API
            result = (
                self.service.users()
                .messages()
                .send(
                    userId="me",
                    body=mime_message,
                )
                .execute()
            )

            return SendEmailResponse(
                message_id=result["id"],
                thread_id=result["threadId"],
                success=True,
            )

        except HttpError as e:
            return SendEmailResponse(
                message_id="",
                thread_id="",
                success=False,
                error=f"Gmail API error: {str(e)}",
            )
        except OSError as e:
            return SendEmailResponse(
                message_id="",
                thread_id="",
                success=False,
                error=f"File access error (attachment?): {str(e)}",
            )
        except Exception as e:
            return SendEmailResponse(
                message_id="",
                thread_id="",
                success=False,
                error=f"Unexpected error: {str(e)}",
            )

    def draft_email(self, request: SendEmailRequest) -> SendEmailResponse:
        """Create an email draft.

        Args:
            request: SendEmailRequest with email details

        Returns:
            SendEmailResponse with draft ID and status

        """
        try:
            # Create MIME message
            mime_message = create_mime_message(
                to=request.to,
                subject=request.subject,
                body=request.body,
                from_=request.from_,
                cc=request.cc,
                bcc=request.bcc,
                reply_to=request.reply_to,
                in_reply_to=request.in_reply_to,
                attachments=request.attachments,
                is_html=request.is_html,
            )

            # Create draft via Gmail API
            draft_body = {"message": mime_message}
            result = (
                self.service.users()
                .drafts()
                .create(
                    userId="me",
                    body=draft_body,
                )
                .execute()
            )

            return SendEmailResponse(
                message_id=result["message"]["id"],
                thread_id=result["message"]["threadId"],
                success=True,
            )

        except HttpError as e:
            return SendEmailResponse(
                message_id="",
                thread_id="",
                success=False,
                error=f"Gmail API error: {str(e)}",
            )
        except OSError as e:
            return SendEmailResponse(
                message_id="",
                thread_id="",
                success=False,
                error=f"File access error (attachment?): {str(e)}",
            )
        except Exception as e:
            return SendEmailResponse(
                message_id="",
                thread_id="",
                success=False,
                error=f"Unexpected error: {str(e)}",
            )

    def reply_email(
        self,
        message_id: str,
        body: str,
        reply_all: bool = False,
        is_html: bool = False,
    ) -> SendEmailResponse:
        """Reply to an email.

        Args:
            message_id: ID of message to reply to
            body: Reply body text
            reply_all: Whether to reply to all recipients (default: False)
            is_html: Whether body is HTML (default: False)

        Returns:
            SendEmailResponse with sent message ID

        """
        try:
            # Get original message
            original = self.read_email(message_id, format="full")
            if not isinstance(original, EmailFull):
                raise ValueError("Failed to fetch original message")

            # Build recipient list
            to = [original.from_.email]
            cc: Optional[List[str]] = None

            if reply_all:
                # Add all original recipients except ourselves
                cc = [
                    addr.email
                    for addr in original.to + original.cc
                    if addr.email != original.from_.email
                ]
                if not cc:
                    cc = None

            # Create reply request
            request = SendEmailRequest(
                to=to,
                cc=cc,
                subject=f"Re: {original.subject}",
                body=body,
                in_reply_to=original.message_id,
                is_html=is_html,
            )

            return self.send_email(request)

        except HttpError as e:
            return SendEmailResponse(
                message_id="",
                thread_id="",
                success=False,
                error=f"Gmail API error: {str(e)}",
            )
        except ValueError as e:
            return SendEmailResponse(
                message_id="",
                thread_id="",
                success=False,
                error=f"Invalid request: {str(e)}",
            )
        except Exception as e:
            return SendEmailResponse(
                message_id="",
                thread_id="",
                success=False,
                error=f"Unexpected error: {str(e)}",
            )

    def modify_labels(
        self,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> bool:
        """Modify labels on a message.

        Args:
            message_id: Gmail message ID
            add_labels: List of label IDs to add
            remove_labels: List of label IDs to remove

        Returns:
            True if successful

        Raises:
            ValueError: If label IDs are invalid
            RuntimeError: If API request fails

        """
        # Validate label IDs
        if add_labels:
            self._validate_label_ids(add_labels)
        if remove_labels:
            self._validate_label_ids(remove_labels)

        try:
            body: Dict[str, List[str]] = {}
            if add_labels:
                body["addLabelIds"] = add_labels
            if remove_labels:
                body["removeLabelIds"] = remove_labels

            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body=body,
            ).execute()

            return True

        except HttpError as e:
            raise RuntimeError(f"Failed to modify labels for {message_id}: {e}")

    def delete_email(self, message_id: str, permanent: bool = False) -> bool:
        """Delete an email.

        Args:
            message_id: Gmail message ID
            permanent: If True, permanently delete. If False, move to trash (default)

        Returns:
            True if successful

        Raises:
            RuntimeError: If API request fails

        """
        try:
            if permanent:
                self.service.users().messages().delete(
                    userId="me",
                    id=message_id,
                ).execute()
            else:
                self.service.users().messages().trash(
                    userId="me",
                    id=message_id,
                ).execute()

            return True

        except HttpError as e:
            raise RuntimeError(f"Failed to delete email {message_id}: {e}")
