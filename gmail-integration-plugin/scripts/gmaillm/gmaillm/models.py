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

    def to_markdown(self) -> str:
        """Human-friendly markdown format."""
        # Build status indicators without emojis
        status_parts = []
        if self.is_unread:
            status_parts.append("UNREAD")
        if self.has_attachments:
            status_parts.append("HAS ATTACHMENTS")
        status = f" [{', '.join(status_parts)}]" if status_parts else ""

        return (
            f"**{self.subject}**{status}\n"
            f"From: {self.from_}\n"
            f"Date: {self.date.strftime('%Y-%m-%d %H:%M')}\n"
            f"ID: {self.message_id}\n"
            f"\n{self.snippet}\n"
        )


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

    def to_markdown(self) -> str:
        """Human-friendly markdown format."""
        lines = [
            f"# {self.subject}",
            "",
            f"From: {self.from_}",
            f"To: {', '.join(str(addr) for addr in self.to)}",
        ]

        if self.cc:
            lines.append(f"CC: {', '.join(str(addr) for addr in self.cc)}")

        lines.append(f"Date: {self.date.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Message ID: {self.message_id}")

        if self.labels:
            lines.append(f"Labels: {', '.join(self.labels)}")

        if self.attachments:
            lines.append(f"\nAttachments ({len(self.attachments)} files):")
            for att in self.attachments:
                lines.append(f"  • {att.filename} — {att.size_human}, {att.mime_type}")

        lines.append("\n" + "─" * 80 + "\n")

        # Prefer plain text body
        body = self.body_plain if self.body_plain else self.body_html
        if body:
            # Truncate if too long (keep first MAX_BODY_CHARS chars for context efficiency)
            if len(body) > MAX_BODY_CHARS:
                lines.append(body[:MAX_BODY_CHARS])
                lines.append(f"\n\n[Body truncated — {len(body)} total characters]")
            else:
                lines.append(body)

        return "\n".join(lines)


class SearchResult(BaseModel):
    """Paginated search results."""

    emails: List[EmailSummary]
    total_count: int
    next_page_token: Optional[str] = None
    query: str

    def to_markdown(self) -> str:
        """Human-friendly markdown format."""
        lines = [
            f'# Search Results: "{self.query}"',
            "",
            f"Found {self.total_count} emails. Showing {len(self.emails)}.",
            "",
        ]

        for i, email in enumerate(self.emails, 1):
            # Build status indicators
            status_parts = []
            if email.is_unread:
                status_parts.append("UNREAD")
            if email.has_attachments:
                status_parts.append("HAS ATTACHMENTS")
            status = f" [{', '.join(status_parts)}]" if status_parts else ""

            lines.append(f"## {i}. {email.subject}{status}")
            lines.append(f"From: {email.from_}")
            lines.append(f"Date: {email.date.strftime('%Y-%m-%d %H:%M')}")
            lines.append(f"ID: {email.message_id}")
            lines.append(f"\n{email.snippet}\n")

        if self.next_page_token:
            lines.append(f"\nMore results available. Use next_page_token: {self.next_page_token}")

        return "\n".join(lines)


class Folder(BaseModel):
    """Gmail label/folder."""

    id: str
    name: str
    type: str  # system or user
    message_count: Optional[int] = None
    unread_count: Optional[int] = None

    def to_markdown(self) -> str:
        """Human-friendly markdown format."""
        parts = []

        if self.message_count is not None:
            parts.append(f"{self.message_count} messages")

        if self.unread_count:
            parts.append(f"{self.unread_count} unread")

        # Use bullet point (•) and em dash (—) for better formatting
        # Format: "• FOLDER_NAME — 123 messages, 5 unread, ID: `Label_1`"
        if parts:
            details = f" — {', '.join(parts)}, ID: `{self.id}`"
        else:
            details = f" — ID: `{self.id}`"
        return f"• {self.name}{details}"


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

    def to_markdown(self) -> str:
        """Human-friendly markdown format."""
        if self.success:
            return (
                f"Email sent successfully!\n"
                f"Message ID: {self.message_id}\n"
                f"Thread ID: {self.thread_id}"
            )
        else:
            return f"Failed to send email: {self.error}"


class BatchOperationResult(BaseModel):
    """Result of batch operations."""

    successful: List[str] = Field(
        default_factory=list, description="Successfully processed message IDs"
    )
    failed: Dict[str, str] = Field(
        default_factory=dict, description="Failed message IDs with error messages"
    )
    total: int

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return len(self.successful) / self.total if self.total > 0 else 0.0

    def to_markdown(self) -> str:
        """Human-friendly markdown format."""
        success_pct = self.success_rate * 100
        lines = [
            "# Batch Operation Results",
            "",
            f"Successful: {len(self.successful)}/{self.total} ({success_pct:.1f}%)",
        ]

        if self.failed:
            lines.append(f"Failed: {len(self.failed)}")
            lines.append("")
            lines.append("## Failed Operations")
            for msg_id, error in list(self.failed.items())[:MAX_FAILURES_SHOWN]:
                lines.append(f"• {msg_id}: {error}")

            if len(self.failed) > MAX_FAILURES_SHOWN:
                lines.append(f"\n... and {len(self.failed) - MAX_FAILURES_SHOWN} more failures")

        return "\n".join(lines)
