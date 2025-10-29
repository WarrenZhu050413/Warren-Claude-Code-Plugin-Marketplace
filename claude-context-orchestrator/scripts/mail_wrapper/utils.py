"""
Utility functions for pagination, formatting, and helpers
"""

import base64
import re
from typing import Optional, Dict, Any, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
from pathlib import Path


def parse_email_address(email_str: str) -> Dict[str, Optional[str]]:
    """Parse 'Name <email@example.com>' format"""
    match = re.match(r'^(.*?)\s*<(.+?)>$', email_str.strip())
    if match:
        return {"name": match.group(1).strip(), "email": match.group(2).strip()}
    return {"name": None, "email": email_str.strip()}


def format_email_address(email: str, name: Optional[str] = None) -> str:
    """Format email address with optional name"""
    if name:
        return f"{name} <{email}>"
    return email


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max_length, adding suffix if truncated"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_snippet(snippet: str) -> str:
    """Clean email snippet for display"""
    # Remove extra whitespace
    snippet = re.sub(r'\s+', ' ', snippet.strip())
    # Remove common email artifacts
    snippet = re.sub(r'\[image:.*?\]', '', snippet)
    return snippet


def create_mime_message(
    to: List[str],
    subject: str,
    body: str,
    from_: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    reply_to: Optional[str] = None,
    in_reply_to: Optional[str] = None,
    attachments: Optional[List[str]] = None,
    is_html: bool = False,
) -> dict:
    """Create a MIME message for Gmail API"""

    # Create message container
    if attachments:
        message = MIMEMultipart()
    else:
        message = MIMEText(body, 'html' if is_html else 'plain')
        message = MIMEMultipart()
        message.attach(MIMEText(body, 'html' if is_html else 'plain'))

    # Set headers
    message['To'] = ', '.join(to)
    message['Subject'] = subject

    if from_:
        message['From'] = from_

    if cc:
        message['Cc'] = ', '.join(cc)

    if bcc:
        message['Bcc'] = ', '.join(bcc)

    if reply_to:
        message['Reply-To'] = reply_to

    if in_reply_to:
        message['In-Reply-To'] = in_reply_to
        message['References'] = in_reply_to

    # Attach body if we have attachments
    if attachments:
        message.attach(MIMEText(body, 'html' if is_html else 'plain'))

        # Add attachments
        for file_path in attachments:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Attachment not found: {file_path}")

            # Guess mime type
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'

            main_type, sub_type = mime_type.split('/', 1)

            with open(file_path, 'rb') as f:
                attachment = MIMEBase(main_type, sub_type)
                attachment.set_payload(f.read())

            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename={path.name}'
            )
            message.attach(attachment)

    # Encode for Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}


def decode_base64(data: str) -> str:
    """Decode base64 encoded string"""
    try:
        # Handle URL-safe base64
        data = data.replace('-', '+').replace('_', '/')
        # Add padding if needed
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except Exception:
        return ""


def extract_body(payload: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    """Extract plain text and HTML body from Gmail API payload"""
    plain_body = None
    html_body = None

    def extract_from_part(part: Dict[str, Any]):
        nonlocal plain_body, html_body

        mime_type = part.get('mimeType', '')
        body = part.get('body', {})
        data = body.get('data', '')

        if mime_type == 'text/plain' and data:
            plain_body = decode_base64(data)
        elif mime_type == 'text/html' and data:
            html_body = decode_base64(data)

        # Recurse into parts
        if 'parts' in part:
            for subpart in part['parts']:
                extract_from_part(subpart)

    # Start extraction
    if 'parts' in payload:
        for part in payload['parts']:
            extract_from_part(part)
    else:
        # Single part message
        extract_from_part(payload)

    return plain_body, html_body


def get_header(headers: List[Dict[str, str]], name: str) -> Optional[str]:
    """Get header value by name (case-insensitive)"""
    name_lower = name.lower()
    for header in headers:
        if header.get('name', '').lower() == name_lower:
            return header.get('value')
    return None


def parse_label_ids(label_ids: List[str]) -> Dict[str, Any]:
    """Parse Gmail label IDs into useful flags"""
    return {
        'is_unread': 'UNREAD' in label_ids,
        'is_important': 'IMPORTANT' in label_ids,
        'is_starred': 'STARRED' in label_ids,
        'is_inbox': 'INBOX' in label_ids,
        'is_sent': 'SENT' in label_ids,
        'is_draft': 'DRAFT' in label_ids,
        'is_trash': 'TRASH' in label_ids,
        'is_spam': 'SPAM' in label_ids,
    }


def validate_pagination_params(max_results: int, max_allowed: int = 50) -> int:
    """Validate and clamp pagination parameters"""
    if max_results < 1:
        return 10  # default
    return min(max_results, max_allowed)
