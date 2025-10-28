"""
Gmail API client with LLM-friendly interface
"""

import os
import json
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import (
    EmailSummary,
    EmailFull,
    EmailFormat,
    EmailAddress,
    Attachment,
    SearchResult,
    Folder,
    SendEmailRequest,
    SendEmailResponse,
    BatchOperationResult,
)
from .utils import (
    parse_email_address,
    clean_snippet,
    create_mime_message,
    extract_body,
    get_header,
    parse_label_ids,
    validate_pagination_params,
)


class GmailClient:
    """
    LLM-friendly Gmail API client with progressive disclosure and pagination
    """

    def __init__(
        self,
        credentials_file: str = "/Users/wz/.gmail-mcp/credentials.json",
        oauth_keys_file: str = "/Users/wz/Desktop/OAuth2/gcp-oauth.keys.json",
    ):
        """
        Initialize Gmail client with OAuth2 credentials

        Args:
            credentials_file: Path to saved OAuth2 credentials
            oauth_keys_file: Path to OAuth2 client secrets
        """
        self.credentials_file = credentials_file
        self.oauth_keys_file = oauth_keys_file
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using existing credentials"""
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_file}\n"
                f"Please ensure Gmail MCP is set up and authenticated."
            )

        if not os.path.exists(self.oauth_keys_file):
            raise FileNotFoundError(
                f"OAuth keys file not found: {self.oauth_keys_file}\n"
                f"Please ensure OAuth2 client secrets are available."
            )

        # Load OAuth keys
        with open(self.oauth_keys_file, 'r') as f:
            oauth_keys = json.load(f)
            if 'installed' in oauth_keys:
                oauth_keys = oauth_keys['installed']

        # Load saved credentials
        with open(self.credentials_file, 'r') as f:
            creds_data = json.load(f)

        # Merge OAuth keys with credentials
        creds_data['client_id'] = oauth_keys['client_id']
        creds_data['client_secret'] = oauth_keys['client_secret']

        creds = Credentials.from_authorized_user_info(creds_data)

        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed credentials
                with open(self.credentials_file, 'w') as f:
                    f.write(creds.to_json())
            except Exception as e:
                raise RuntimeError(
                    f"Failed to refresh credentials: {e}\n"
                    f"You may need to re-authenticate with Gmail MCP."
                )

        self.service = build('gmail', 'v1', credentials=creds)

    def _parse_message_to_summary(self, msg_data: Dict[str, Any]) -> EmailSummary:
        """Parse Gmail API message into EmailSummary"""
        msg_id = msg_data['id']
        thread_id = msg_data['threadId']
        snippet = clean_snippet(msg_data.get('snippet', ''))

        payload = msg_data.get('payload', {})
        headers = payload.get('headers', [])

        # Extract headers
        from_header = get_header(headers, 'From') or ''
        subject = get_header(headers, 'Subject') or '(No subject)'
        date_str = get_header(headers, 'Date') or ''

        # Parse date
        try:
            from email.utils import parsedate_to_datetime
            date = parsedate_to_datetime(date_str)
        except:
            date = datetime.now()

        # Parse from address
        from_parsed = parse_email_address(from_header)

        # Get labels and flags
        label_ids = msg_data.get('labelIds', [])
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
            is_unread=flags['is_unread'],
        )

    def _parse_message_to_full(self, msg_data: Dict[str, Any]) -> EmailFull:
        """Parse Gmail API message into EmailFull"""
        msg_id = msg_data['id']
        thread_id = msg_data['threadId']

        payload = msg_data.get('payload', {})
        headers = payload.get('headers', [])

        # Extract all headers into dict
        headers_dict = {h['name']: h['value'] for h in headers}

        # Extract key headers
        from_header = get_header(headers, 'From') or ''
        to_header = get_header(headers, 'To') or ''
        cc_header = get_header(headers, 'Cc') or ''
        bcc_header = get_header(headers, 'Bcc') or ''
        subject = get_header(headers, 'Subject') or '(No subject)'
        date_str = get_header(headers, 'Date') or ''
        in_reply_to = get_header(headers, 'In-Reply-To')
        references = get_header(headers, 'References') or ''

        # Parse date
        try:
            from email.utils import parsedate_to_datetime
            date = parsedate_to_datetime(date_str)
        except:
            date = datetime.now()

        # Parse email addresses
        from_parsed = parse_email_address(from_header)
        to_list = [EmailAddress(**parse_email_address(addr.strip()))
                   for addr in to_header.split(',') if addr.strip()]
        cc_list = [EmailAddress(**parse_email_address(addr.strip()))
                   for addr in cc_header.split(',') if addr.strip()]
        bcc_list = [EmailAddress(**parse_email_address(addr.strip()))
                    for addr in bcc_header.split(',') if addr.strip()]

        # Extract body
        plain_body, html_body = extract_body(payload)

        # Extract attachments
        attachments = self._extract_attachments(payload)

        # Get labels
        label_ids = msg_data.get('labelIds', [])

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
        """Check if message has attachments"""
        def check_part(part: Dict[str, Any]) -> bool:
            if part.get('filename') and part.get('body', {}).get('attachmentId'):
                return True
            if 'parts' in part:
                return any(check_part(p) for p in part['parts'])
            return False

        return check_part(payload)

    def _extract_attachments(self, payload: Dict[str, Any]) -> List[Attachment]:
        """Extract attachment metadata from payload"""
        attachments = []

        def extract_from_part(part: Dict[str, Any]):
            filename = part.get('filename', '')
            body = part.get('body', {})
            attachment_id = body.get('attachmentId')

            if filename and attachment_id:
                attachments.append(Attachment(
                    filename=filename,
                    mime_type=part.get('mimeType', 'application/octet-stream'),
                    size=body.get('size', 0),
                    attachment_id=attachment_id,
                ))

            # Recurse into parts
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_from_part(subpart)

        if 'parts' in payload:
            for part in payload['parts']:
                extract_from_part(part)

        return attachments

    def list_emails(
        self,
        folder: str = 'INBOX',
        max_results: int = 10,
        page_token: Optional[str] = None,
        query: Optional[str] = None,
    ) -> SearchResult:
        """
        List emails from a folder with pagination

        Args:
            folder: Gmail label/folder (default: INBOX)
            max_results: Maximum results per page (1-50, default: 10)
            page_token: Token for next page of results
            query: Gmail search query (optional)

        Returns:
            SearchResult with email summaries and pagination info
        """
        max_results = validate_pagination_params(max_results)

        # Build query
        search_query = f"label:{folder}"
        if query:
            search_query = f"{search_query} {query}"

        try:
            # List messages
            result = self.service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_results,
                pageToken=page_token,
            ).execute()

            messages = result.get('messages', [])
            next_page = result.get('nextPageToken')
            total_estimate = result.get('resultSizeEstimate', len(messages))

            # Fetch full message data for summaries
            summaries = []
            for msg in messages:
                try:
                    msg_data = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full',
                    ).execute()
                    summaries.append(self._parse_message_to_summary(msg_data))
                except HttpError:
                    continue  # Skip messages that can't be fetched

            return SearchResult(
                emails=summaries,
                total_count=total_estimate,
                next_page_token=next_page,
                query=search_query,
            )

        except HttpError as e:
            raise RuntimeError(f"Failed to list emails: {e}")

    def read_email(
        self,
        message_id: str,
        format: Literal["summary", "headers", "full"] = "summary",
    ) -> EmailSummary | EmailFull:
        """
        Read an email with progressive disclosure

        Args:
            message_id: Gmail message ID
            format: Output format - "summary" (brief), "headers" (summary + headers), "full" (complete)

        Returns:
            EmailSummary or EmailFull depending on format
        """
        try:
            msg_data = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full',
            ).execute()

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
        folder: str = 'INBOX',
        max_results: int = 10,
        page_token: Optional[str] = None,
    ) -> SearchResult:
        """
        Search emails using Gmail search syntax

        Args:
            query: Gmail search query (e.g., "from:[email protected]", "has:attachment")
            folder: Gmail label/folder to search in (default: INBOX)
            max_results: Maximum results per page (1-50, default: 10)
            page_token: Token for next page of results

        Returns:
            SearchResult with matching email summaries
        """
        return self.list_emails(
            folder=folder,
            max_results=max_results,
            page_token=page_token,
            query=query,
        )

    def get_folders(self) -> List[Folder]:
        """
        Get list of all Gmail labels/folders

        Returns:
            List of Folder objects with metadata
        """
        try:
            result = self.service.users().labels().list(userId='me').execute()
            labels = result.get('labels', [])

            folders = []
            for label in labels:
                folder = Folder(
                    id=label['id'],
                    name=label['name'],
                    type=label['type'].lower(),
                    message_count=label.get('messagesTotal'),
                    unread_count=label.get('messagesUnread'),
                )
                folders.append(folder)

            return folders

        except HttpError as e:
            raise RuntimeError(f"Failed to get folders: {e}")

    def verify_setup(self) -> Dict[str, Any]:
        """
        Verify authentication and basic Gmail API functionality

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
        results = {
            'auth': False,
            'email_address': None,
            'folders': 0,
            'inbox_accessible': False,
            'errors': []
        }

        try:
            # Test authentication by getting user profile
            profile = self.service.users().getProfile(userId='me').execute()
            results['auth'] = True
            results['email_address'] = profile.get('emailAddress')

            # Test folder access
            folders = self.get_folders()
            results['folders'] = len(folders)

            # Test inbox read access
            inbox = self.list_emails(folder='INBOX', max_results=1)
            results['inbox_accessible'] = True

        except Exception as e:
            results['errors'].append(str(e))

        return results

    def get_thread(self, message_id: str) -> List[EmailSummary]:
        """
        Get all emails in a thread

        Args:
            message_id: ID of any message in the thread

        Returns:
            List of EmailSummary objects in chronological order
        """
        try:
            # First get the message to find its thread_id
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='minimal'
            ).execute()

            thread_id = msg['threadId']

            # Get the full thread
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()

            # Parse all messages in thread
            messages = []
            for msg_data in thread.get('messages', []):
                email_summary = self._parse_message_to_summary(msg_data)
                messages.append(email_summary)

            # Sort by date (should already be sorted, but ensure it)
            messages.sort(key=lambda x: x.date)

            return messages

        except HttpError as e:
            raise RuntimeError(f"Failed to get thread: {e}")

    def send_email(self, request: SendEmailRequest) -> SendEmailResponse:
        """
        Send an email

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
            result = self.service.users().messages().send(
                userId='me',
                body=mime_message,
            ).execute()

            return SendEmailResponse(
                message_id=result['id'],
                thread_id=result['threadId'],
                success=True,
            )

        except Exception as e:
            return SendEmailResponse(
                message_id='',
                thread_id='',
                success=False,
                error=str(e),
            )

    def draft_email(self, request: SendEmailRequest) -> SendEmailResponse:
        """
        Create an email draft

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
            draft_body = {'message': mime_message}
            result = self.service.users().drafts().create(
                userId='me',
                body=draft_body,
            ).execute()

            return SendEmailResponse(
                message_id=result['message']['id'],
                thread_id=result['message']['threadId'],
                success=True,
            )

        except Exception as e:
            return SendEmailResponse(
                message_id='',
                thread_id='',
                success=False,
                error=str(e),
            )

    def reply_email(
        self,
        message_id: str,
        body: str,
        reply_all: bool = False,
        is_html: bool = False,
    ) -> SendEmailResponse:
        """
        Reply to an email

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
            cc = None

            if reply_all:
                # Add all original recipients except ourselves
                cc = [addr.email for addr in original.to + original.cc
                      if addr.email != original.from_.email]
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

        except Exception as e:
            return SendEmailResponse(
                message_id='',
                thread_id='',
                success=False,
                error=str(e),
            )

    def modify_labels(
        self,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> bool:
        """
        Modify labels on a message

        Args:
            message_id: Gmail message ID
            add_labels: List of label IDs to add
            remove_labels: List of label IDs to remove

        Returns:
            True if successful
        """
        try:
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels

            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=body,
            ).execute()

            return True

        except HttpError as e:
            raise RuntimeError(f"Failed to modify labels for {message_id}: {e}")

    def delete_email(self, message_id: str, permanent: bool = False) -> bool:
        """
        Delete an email

        Args:
            message_id: Gmail message ID
            permanent: If True, permanently delete. If False, move to trash (default)

        Returns:
            True if successful
        """
        try:
            if permanent:
                self.service.users().messages().delete(
                    userId='me',
                    id=message_id,
                ).execute()
            else:
                self.service.users().messages().trash(
                    userId='me',
                    id=message_id,
                ).execute()

            return True

        except HttpError as e:
            raise RuntimeError(f"Failed to delete email {message_id}: {e}")

    def batch_modify_labels(
        self,
        message_ids: List[str],
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> BatchOperationResult:
        """
        Modify labels on multiple messages in batch

        Args:
            message_ids: List of Gmail message IDs
            add_labels: List of label IDs to add
            remove_labels: List of label IDs to remove

        Returns:
            BatchOperationResult with success/failure counts
        """
        result = BatchOperationResult(total=len(message_ids))

        for msg_id in message_ids:
            try:
                self.modify_labels(msg_id, add_labels, remove_labels)
                result.successful.append(msg_id)
            except Exception as e:
                result.failed[msg_id] = str(e)

        return result

    def batch_delete(
        self,
        message_ids: List[str],
        permanent: bool = False,
    ) -> BatchOperationResult:
        """
        Delete multiple messages in batch

        Args:
            message_ids: List of Gmail message IDs
            permanent: If True, permanently delete. If False, move to trash

        Returns:
            BatchOperationResult with success/failure counts
        """
        result = BatchOperationResult(total=len(message_ids))

        for msg_id in message_ids:
            try:
                self.delete_email(msg_id, permanent)
                result.successful.append(msg_id)
            except Exception as e:
                result.failed[msg_id] = str(e)

        return result
