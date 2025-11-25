"""Email preview formatting for CLI display.

This module provides utilities for formatting email previews in the CLI,
ensuring consistent visual presentation across all email operations.

Key Features:
- Rich-formatted preview output
- Standardized preview layout
- Support for attachments and recipients
"""

from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel

console = Console()


def format_email_preview(
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None,
) -> str:
    """Format email preview as a display string.

    Creates a structured preview showing:
    - Recipients (To, CC, BCC)
    - Subject line
    - Body content
    - Attachments (if present)

    Args:
        to: List of recipient email addresses
        subject: Email subject line
        body: Email body content
        cc: Optional list of CC recipients
        bcc: Optional list of BCC recipients
        attachments: Optional list of attachment paths

    Returns:
        Formatted preview string ready for console display

    Example:
        preview = format_email_preview(
            to=["user@example.com"],
            subject="Hello",
            body="This is the message",
            cc=["boss@example.com"]
        )
        console.print(preview)
    """
    preview_lines = []

    # Recipients section
    preview_lines.append(f"[bold]To:[/bold] {', '.join(to)}")
    if cc:
        preview_lines.append(f"[bold]Cc:[/bold] {', '.join(cc)}")
    if bcc:
        preview_lines.append(f"[bold]Bcc:[/bold] {', '.join(bcc)}")

    # Subject section
    preview_lines.append(f"[bold]Subject:[/bold] {subject}")

    # Separator
    preview_lines.append("=" * 60)

    # Body
    preview_lines.append(body)

    # Attachments section (if present)
    if attachments:
        preview_lines.append("=" * 60)
        preview_lines.append(f"[bold]Attachments:[/bold] {len(attachments)} file(s)")
        for att in attachments:
            preview_lines.append(f"  - {att}")

    return "\n".join(preview_lines)


def show_email_preview(
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None,
    title: str = "📧 Email Preview",
) -> None:
    """Display formatted email preview to console.

    Shows a rich-formatted preview panel with all email details.
    This is the core preview functionality for the preview-first workflow.

    Args:
        to: List of recipient email addresses
        subject: Email subject line
        body: Email body content
        cc: Optional list of CC recipients
        bcc: Optional list of BCC recipients
        attachments: Optional list of attachment paths
        title: Panel title (default: "📧 Email Preview")

    Example:
        show_email_preview(
            to=["user@example.com"],
            subject="Hello",
            body="This is the message",
            title="📧 Email Preview"
        )
        response = typer.confirm("Send this email?")
    """
    preview_content = format_email_preview(
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        attachments=attachments,
    )

    console.print(
        Panel(
            preview_content,
            title=title,
            border_style="blue",
        )
    )


def show_operation_preview(title: str, details: Dict[str, str]) -> None:
    """Display operation preview as a formatted panel.

    This is a legacy function kept for compatibility with existing code.
    Shows operation details in a structured format.

    Args:
        title: Title of the operation (e.g., "Email Preview")
        details: Dictionary of field name -> value pairs

    Example:
        show_operation_preview("Reply Preview", {
            "To": "user@example.com",
            "Subject": "Re: Hello"
        })
    """
    details_lines = [f"[bold]{key}:[/bold] {value}" for key, value in details.items()]
    content = "\n".join(details_lines)

    console.print(
        Panel(
            content,
            title=title,
            border_style="blue",
        )
    )
