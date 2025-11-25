"""gmaillm - LLM-friendly Gmail API wrapper.

A Python library that provides Gmail functionality with progressive disclosure,
pagination, and LLM-optimized output formatting.

Note: You may see an INFO message: "file_cache is only supported with oauth2client<4.0.0"
This is harmless and comes from the Google API client library. It can be safely ignored.
"""

from .gmail_client import GmailClient
from .models import (
    EmailFormat,
    EmailFull,
    EmailSummary,
    Folder,
    SearchResult,
    SendEmailRequest,
)

__version__ = "1.0.0"
__all__ = [
    "GmailClient",
    "EmailSummary",
    "EmailFull",
    "EmailFormat",
    "SearchResult",
    "Folder",
    "SendEmailRequest",
]
