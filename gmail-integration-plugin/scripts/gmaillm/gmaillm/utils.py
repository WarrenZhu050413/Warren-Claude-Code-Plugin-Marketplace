"""Utility functions for pagination, formatting, and helpers."""

import base64
import binascii
import mimetypes
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Constants
BASE64_PADDING_SIZE = 4
MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25MB Gmail limit
DEFAULT_MAX_RESULTS = 10
DEFAULT_TRUNCATE_LENGTH = 100
DEFAULT_TRUNCATE_SUFFIX = "..."

# Email validation pattern
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Base64 valid characters set for O(1) lookup
BASE64_VALID_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise
    """
    return bool(EMAIL_PATTERN.match(email))


def parse_email_address(email_str: str) -> Dict[str, Optional[str]]:
    """Parse 'Name <email@example.com>' format.

    Args:
        email_str: Email string to parse

    Returns:
        Dictionary with 'name' and 'email' keys

    Raises:
        ValueError: If email format is invalid
    """
    match = re.match(r"^(.*?)\s*<(.+?)>$", email_str.strip())
    if match:
        name = match.group(1).strip()
        email = match.group(2).strip()
        if not validate_email(email):
            raise ValueError(f"Invalid email address: {email}")
        return {"name": name, "email": email}

    email = email_str.strip()
    if not validate_email(email):
        raise ValueError(f"Invalid email address: {email}")
    return {"name": None, "email": email}


def format_email_address(email: str, name: Optional[str] = None) -> str:
    """Format email address with optional name.

    Args:
        email: Email address
        name: Optional display name

    Returns:
        Formatted email string

    Raises:
        ValueError: If email format is invalid
    """
    if not validate_email(email):
        raise ValueError(f"Invalid email address: {email}")

    if name:
        return f"{name} <{email}>"
    return email


def truncate_text(text: str, max_length: int = DEFAULT_TRUNCATE_LENGTH, suffix: str = DEFAULT_TRUNCATE_SUFFIX) -> str:
    """Truncate text to max_length, adding suffix if truncated.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def clean_snippet(snippet: str) -> str:
    """Clean email snippet for display.

    Args:
        snippet: Email snippet text

    Returns:
        Cleaned snippet
    """
    # Remove common email artifacts first
    snippet = re.sub(r"\[image:.*?\]", "", snippet)
    # Remove extra whitespace
    snippet = re.sub(r"\s+", " ", snippet.strip())
    return snippet


def _set_message_headers(message: MIMEMultipart, headers: Dict[str, Optional[str]]) -> None:
    """Set email headers from a dict.

    Args:
        message: MIME message to set headers on
        headers: Dictionary of header names and values

    Raises:
        TypeError: If header value is not a string
    """
    for header_name, header_value in headers.items():
        if header_value:
            if not isinstance(header_value, str):
                raise TypeError(f"Header '{header_name}' must be a string, got {type(header_value).__name__}")
            message[header_name] = header_value


def _attach_file(message: MIMEMultipart, file_path: str) -> None:
    """Attach a file to the message.

    Args:
        message: MIME message to attach file to
        file_path: Path to file to attach

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file exceeds size limit or has invalid filename
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Attachment not found: {file_path}")

    # Check file size
    file_size = path.stat().st_size
    if file_size > MAX_ATTACHMENT_SIZE:
        raise ValueError(f"Attachment exceeds 25MB limit: {file_path} ({file_size / 1024 / 1024:.2f}MB)")

    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    # Safe split with defensive None check
    if "/" in mime_type:
        main_type, sub_type = mime_type.split("/", 1)
    else:
        main_type = "application"
        sub_type = "octet-stream"

    # Read file content inside with block
    with open(file_path, "rb") as f:
        content = f.read()

    attachment = MIMEBase(main_type, sub_type)
    attachment.set_payload(content)

    encoders.encode_base64(attachment)

    # Sanitize filename for security
    safe_filename = Path(file_path).name.replace('"', '').replace('\r', '').replace('\n', '')
    attachment.add_header("Content-Disposition", f'attachment; filename="{safe_filename}"')
    message.attach(attachment)


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
) -> Dict[str, str]:
    """Create a MIME message for Gmail API.

    Args:
        to: List of recipient email addresses
        subject: Email subject
        body: Email body content
        from_: Optional sender email
        cc: Optional CC recipients
        bcc: Optional BCC recipients
        reply_to: Optional Reply-To address
        in_reply_to: Optional In-Reply-To message ID
        attachments: Optional list of file paths to attach
        is_html: Whether body is HTML

    Returns:
        Dictionary with 'raw' key containing base64-encoded message

    Raises:
        ValueError: If recipient list is empty or email validation fails
    """
    # Validate empty recipient list
    if not to:
        raise ValueError("At least one recipient required in 'to' field")

    # Create message container
    message = MIMEMultipart()

    # Attach body
    content_type = "html" if is_html else "plain"
    message.attach(MIMEText(body, content_type))

    # Set all headers using data structure (eliminates 6 if statements!)
    headers: Dict[str, Optional[str]] = {
        "To": ", ".join(to),
        "Subject": subject,
        "From": from_,
        "Cc": ", ".join(cc) if cc else None,
        "Bcc": ", ".join(bcc) if bcc else None,
        "Reply-To": reply_to,
        "In-Reply-To": in_reply_to,
        "References": in_reply_to,  # Same as In-Reply-To
    }
    _set_message_headers(message, headers)

    # Attach files
    if attachments:
        for file_path in attachments:
            _attach_file(message, file_path)

    # Encode for Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return {"raw": raw_message}


def decode_base64(data: str) -> str:
    """Decode base64 encoded string.

    Args:
        data: Base64 encoded string

    Returns:
        Decoded string, or empty string if decoding fails
    """
    if not data or not isinstance(data, str):
        return ""

    try:
        # Handle URL-safe base64
        data_to_decode = data.replace("-", "+").replace("_", "/")
        # Add padding if needed
        padding = BASE64_PADDING_SIZE - len(data_to_decode) % BASE64_PADDING_SIZE
        if padding != BASE64_PADDING_SIZE:
            data_to_decode += "=" * padding

        # Validate base64 format - use set for O(1) lookup
        if not all(c in BASE64_VALID_CHARS for c in data_to_decode):
            return ""

        decoded = base64.b64decode(data_to_decode, validate=True)
        return decoded.decode("utf-8", errors="strict")
    except (ValueError, binascii.Error, UnicodeDecodeError):
        return ""


def extract_body(payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Extract plain text and HTML body from Gmail API payload.

    Args:
        payload: Gmail API message payload

    Returns:
        Tuple of (plain_text_body, html_body), either may be None
    """
    plain_body = None
    html_body = None

    def extract_from_part(part: Dict[str, Any]) -> None:
        nonlocal plain_body, html_body

        mime_type = part.get("mimeType", "")
        body = part.get("body", {})
        data = body.get("data", "")

        if mime_type == "text/plain" and data:
            plain_body = decode_base64(data)
        elif mime_type == "text/html" and data:
            html_body = decode_base64(data)

        # Recurse into parts
        if "parts" in part:
            for subpart in part["parts"]:
                extract_from_part(subpart)

    # Start extraction
    if "parts" in payload:
        for part in payload["parts"]:
            extract_from_part(part)
    else:
        # Single part message
        extract_from_part(payload)

    return plain_body, html_body


def get_header(headers: List[Dict[str, str]], name: str) -> Optional[str]:
    """Get header value by name (case-insensitive).

    Args:
        headers: List of header dictionaries with 'name' and 'value' keys
        name: Header name to search for

    Returns:
        Header value if found, None otherwise
    """
    name_lower = name.lower()
    for header in headers:
        if header.get("name", "").lower() == name_lower:
            return header.get("value")
    return None


def parse_label_ids(label_ids: List[str]) -> Dict[str, bool]:
    """Parse Gmail label IDs into useful flags.

    Args:
        label_ids: List of Gmail label IDs

    Returns:
        Dictionary of boolean flags for common labels
    """
    return {
        "is_unread": "UNREAD" in label_ids,
        "is_important": "IMPORTANT" in label_ids,
        "is_starred": "STARRED" in label_ids,
        "is_inbox": "INBOX" in label_ids,
        "is_sent": "SENT" in label_ids,
        "is_draft": "DRAFT" in label_ids,
        "is_trash": "TRASH" in label_ids,
        "is_spam": "SPAM" in label_ids,
    }


def validate_pagination_params(max_results: int, max_allowed: int = 50) -> int:
    """Validate and clamp pagination parameters.

    Args:
        max_results: Requested maximum results
        max_allowed: Maximum allowed results

    Returns:
        Validated max_results value
    """
    if max_results < 1:
        return DEFAULT_MAX_RESULTS
    return min(max_results, max_allowed)
