"""
Pydantic models for email data structures with LLM-friendly formatting
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from enum import Enum


class EmailFormat(str, Enum):
    """Email display format types"""
    SUMMARY = "summary"  # Brief overview: ID, from, subject, date, snippet
    HEADERS = "headers"  # Summary + all headers
    FULL = "full"        # Complete email with body and attachments


class EmailAddress(BaseModel):
    """Email address with optional name"""
    email: str
    name: Optional[str] = None

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} <{self.email}>"
        return self.email


class Attachment(BaseModel):
    """Email attachment metadata"""
    filename: str
    mime_type: str
    size: int  # in bytes
    attachment_id: str

    @property
    def size_human(self) -> str:
        """Human-readable file size"""
        if self.size < 1024:
            return f"{self.size}B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f}KB"
        else:
            return f"{self.size / (1024 * 1024):.1f}MB"


class EmailSummary(BaseModel):
    """Concise email summary for list views - LLM optimized"""
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
        """LLM-friendly markdown format"""
        unread = "🔵 " if self.is_unread else ""
        attachment = "📎 " if self.has_attachments else ""
        return (
            f"{unread}{attachment}**{self.subject}**\n"
            f"From: {self.from_}\n"
            f"Date: {self.date.strftime('%Y-%m-%d %H:%M')}\n"
            f"ID: `{self.message_id}`\n"
            f"_{self.snippet}_"
        )


class EmailFull(BaseModel):
    """Complete email with body and attachments"""
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
        """LLM-friendly markdown format"""
        lines = [
            f"# {self.subject}",
            "",
            f"**From:** {self.from_}",
            f"**To:** {', '.join(str(addr) for addr in self.to)}",
        ]

        if self.cc:
            lines.append(f"**CC:** {', '.join(str(addr) for addr in self.cc)}")

        lines.append(f"**Date:** {self.date.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Message ID:** `{self.message_id}`")

        if self.labels:
            lines.append(f"**Labels:** {', '.join(self.labels)}")

        if self.attachments:
            lines.append(f"\n**Attachments:** ({len(self.attachments)} files)")
            for att in self.attachments:
                lines.append(f"  - {att.filename} ({att.size_human}, {att.mime_type})")

        lines.append("\n---\n")

        # Prefer plain text body
        body = self.body_plain if self.body_plain else self.body_html
        if body:
            # Truncate if too long (keep first 3000 chars for LLM context efficiency)
            if len(body) > 3000:
                lines.append(body[:3000])
                lines.append(f"\n\n_[Body truncated - {len(body)} total characters]_")
            else:
                lines.append(body)

        return "\n".join(lines)


class SearchResult(BaseModel):
    """Paginated search results"""
    emails: List[EmailSummary]
    total_count: int
    next_page_token: Optional[str] = None
    query: str

    def to_markdown(self) -> str:
        """LLM-friendly markdown format"""
        lines = [
            f"# Search Results: \"{self.query}\"",
            f"",
            f"Found {self.total_count} emails. Showing {len(self.emails)}.",
            "",
        ]

        for i, email in enumerate(self.emails, 1):
            lines.append(f"## {i}. {email.subject}")
            lines.append(f"From: {email.from_}")
            lines.append(f"Date: {email.date.strftime('%Y-%m-%d %H:%M')}")
            lines.append(f"ID: `{email.message_id}`")
            lines.append(f"_{email.snippet}_")
            lines.append("")

        if self.next_page_token:
            lines.append(f"_More results available. Use next_page_token: `{self.next_page_token}`_")

        return "\n".join(lines)


class Folder(BaseModel):
    """Gmail label/folder"""
    id: str
    name: str
    type: str  # system or user
    message_count: Optional[int] = None
    unread_count: Optional[int] = None

    def to_markdown(self) -> str:
        """LLM-friendly markdown format"""
        unread = f" ({self.unread_count} unread)" if self.unread_count else ""
        msg_count = f" [{self.message_count} messages]" if self.message_count else ""
        return f"- **{self.name}**{msg_count}{unread} (ID: `{self.id}`)"


class SendEmailRequest(BaseModel):
    """Request to send an email"""
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

    @field_validator('to', 'cc', 'bcc')
    @classmethod
    def validate_emails(cls, v):
        """Ensure email addresses are valid"""
        if v is None:
            return v
        # Basic email validation
        for email in v:
            if '@' not in email or '.' not in email.split('@')[1]:
                raise ValueError(f"Invalid email address: {email}")
        return v


class SendEmailResponse(BaseModel):
    """Response after sending an email"""
    message_id: str
    thread_id: str
    success: bool = True
    error: Optional[str] = None

    def to_markdown(self) -> str:
        """LLM-friendly markdown format"""
        if self.success:
            return (
                f"✅ Email sent successfully!\n"
                f"Message ID: `{self.message_id}`\n"
                f"Thread ID: `{self.thread_id}`"
            )
        else:
            return f"❌ Failed to send email: {self.error}"


class BatchOperationResult(BaseModel):
    """Result of batch operations"""
    successful: List[str] = Field(default_factory=list, description="Successfully processed message IDs")
    failed: Dict[str, str] = Field(default_factory=dict, description="Failed message IDs with error messages")
    total: int

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        return len(self.successful) / self.total if self.total > 0 else 0.0

    def to_markdown(self) -> str:
        """LLM-friendly markdown format"""
        success_pct = self.success_rate * 100
        lines = [
            f"# Batch Operation Results",
            "",
            f"✅ Successful: {len(self.successful)}/{self.total} ({success_pct:.1f}%)",
        ]

        if self.failed:
            lines.append(f"❌ Failed: {len(self.failed)}")
            lines.append("")
            lines.append("## Failed Operations")
            for msg_id, error in list(self.failed.items())[:10]:  # Limit to first 10
                lines.append(f"- `{msg_id}`: {error}")

            if len(self.failed) > 10:
                lines.append(f"_... and {len(self.failed) - 10} more failures_")

        return "\n".join(lines)
