"""Pydantic models for email data structures with LLM-friendly formatting."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, Field, field_validator

# Constants
BYTES_PER_KB = 1024
MAX_BODY_CHARS = 3000
MAX_FAILURES_SHOWN = 10


class EmailFormat(str, Enum):
    """Email display format types."""

    SUMMARY = "summary"  # Brief overview: ID, from, subject, date, snippet
    HEADERS = "headers"  # Summary + all headers
    FULL = "full"  # Complete email with body and attachments


class EmailAddress(BaseModel):
    """Email address with optional name."""

    email: str
    name: Optional[str] = None

    def __str__(self) -> str:
        """Return formatted email address with optional name."""
        if self.name:
            return f"{self.name} <{self.email}>"
        return self.email


class Attachment(BaseModel):
    """Email attachment metadata."""

    filename: str
    mime_type: str
    size: int  # in bytes
    attachment_id: str

    @property
    def size_human(self) -> str:
        """Human-readable file size."""
        if self.size < BYTES_PER_KB:
            return f"{self.size}B"
        elif self.size < BYTES_PER_KB * BYTES_PER_KB:
            return f"{self.size / BYTES_PER_KB:.1f}KB"
        else:
            return f"{self.size / (BYTES_PER_KB * BYTES_PER_KB):.1f}MB"


class EmailSummary(BaseModel):
    """Concise email summary for list views - LLM optimized."""

    message_id: str
    thread_id: str
    from_: EmailAddress = Field(alias="from")
    subject: str
    date: datetime
    snippet: str  # First ~100 chars of body
    labels: List[str] = Field(default_factory=list)
    has_attachments: bool = False
    is_unread: bool = False

    model_config = {
        "populate_by_name": True,
    }


class EmailFull(BaseModel):
    """Complete email with body and attachments."""

    message_id: str
    thread_id: str
    from_: EmailAddress = Field(alias="from")
    to: List[EmailAddress] = Field(default_factory=list)
    cc: List[EmailAddress] = Field(default_factory=list)
    bcc: List[EmailAddress] = Field(default_factory=list)
    subject: str
    date: datetime
    body_plain: Optional[str] = None
    body_html: Optional[str] = None
    attachments: List[Attachment] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    headers: Dict[str, str] = Field(default_factory=dict)
    in_reply_to: Optional[str] = None
    references: List[str] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
    }


class SearchResult(BaseModel):
    """Paginated search results."""

    emails: List[EmailSummary]
    total_count: int
    next_page_token: Optional[str] = None
    query: str


class Folder(BaseModel):
    """Gmail label/folder."""

    id: str
    name: str
    type: str  # system or user
    message_count: Optional[int] = None
    unread_count: Optional[int] = None


class SendEmailRequest(BaseModel):
    """Request to send an email."""

    to: List[str] = Field(min_length=1, description="List of recipient email addresses")
    subject: str = Field(min_length=1, description="Email subject")
    body: str = Field(description="Email body (plain text or HTML)")
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    from_: Optional[str] = Field(None, alias="from", description="Sender email (optional)")
    reply_to: Optional[str] = None
    in_reply_to: Optional[str] = Field(None, description="Message ID being replied to")
    attachments: Optional[List[str]] = Field(None, description="List of file paths to attach")
    is_html: bool = Field(False, description="Whether body is HTML")

    model_config = {
        "populate_by_name": True,
    }

    @field_validator("to", "cc", "bcc")
    @classmethod
    def validate_emails(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Ensure email addresses are valid using email-validator library."""
        if v is None:
            return v

        for email in v:
            try:
                # Validate email format without checking DNS deliverability
                validate_email(email, check_deliverability=False)
            except EmailNotValidError as e:
                raise ValueError(f"Invalid email address: {email}") from e
        return v


class SendEmailResponse(BaseModel):
    """Response after sending an email."""

    message_id: str
    thread_id: str
    success: bool = True
    error: Optional[str] = None
