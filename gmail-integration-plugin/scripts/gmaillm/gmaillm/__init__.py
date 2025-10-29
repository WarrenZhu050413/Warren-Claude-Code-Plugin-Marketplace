"""gmaillm - LLM-friendly Gmail API wrapper.

A Python library that provides Gmail functionality with progressive disclosure,
pagination, and LLM-optimized output formatting.
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
