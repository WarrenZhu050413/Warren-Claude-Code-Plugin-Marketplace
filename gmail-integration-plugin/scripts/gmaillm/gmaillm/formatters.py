"""Rich-based formatters for terminal output.

This module centralizes all terminal formatting logic, separating presentation
from data models. All CLI commands should use RichFormatter for consistent,
beautiful terminal output.
"""

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .models import (
    Attachment,
    EmailFull,
    EmailSummary,
    Folder,
    SearchResult,
    SendEmailResponse,
)

# Constants for formatting
SNIPPET_PREVIEW_LENGTH = 80
MESSAGE_ID_DISPLAY_LENGTH = 12


class RichFormatter:
    """Centralized formatter for Rich terminal output."""

    def __init__(self, console: Console):
        """Initialize formatter with Rich console.

        Args:
            console: Rich Console instance for output
        """
        self.console = console

    # ============ FOLDER FORMATTING ============

    def format_folder(self, folder: Folder) -> str:
        """Format a single folder for terminal display.

        Args:
            folder: Folder object to format

        Returns:
            Formatted string with Rich markup
        """
        name = f"[bold cyan]{folder.name}[/bold cyan]"

        parts = []
        if folder.message_count is not None:
            parts.append(f"{folder.message_count} messages")
        if folder.unread_count:
            parts.append(f"[yellow]{folder.unread_count} unread[/yellow]")
        parts.append(f"ID: [dim]{folder.id}[/dim]")

        details = f" ({', '.join(parts)})" if parts else ""
        return f"  {name}{details}"

    def print_folder_list(
        self, folders: List[Folder], title: str = "Folders"
    ) -> None:
        """Format and print a list of folders.

        Args:
            folders: List of Folder objects
            title: Title for the list
        """
        # Separate system and user folders
        system = [f for f in folders if f.type == "system"]
        user = [f for f in folders if f.type == "user"]

        self.console.print("=" * 60)
        self.console.print(f"{title} ({len(folders)})")
        self.console.print("=" * 60)

        if system:
            self.console.print("\n[bold]📋 System Labels:[/bold]")
            for folder in system:
                self.console.print(self.format_folder(folder))

        if user:
            self.console.print("\n[bold]🏷️  Custom Labels:[/bold]")
            for folder in user:
                self.console.print(self.format_folder(folder))

        self.console.print(
            f"\n[dim]Total: {len(system)} system, {len(user)} custom[/dim]"
        )

    # ============ EMAIL FORMATTING ============

    def format_email_summary(self, email: EmailSummary) -> str:
        """Format email summary for lists.

        Args:
            email: EmailSummary object to format

        Returns:
            Formatted string with Rich markup
        """
        # Status indicators
        status = []
        if email.is_unread:
            status.append("[yellow]●[/yellow]")  # Unread dot
        if email.has_attachments:
            status.append("📎")

        status_str = " ".join(status) + " " if status else ""

        # Format parts
        subject = f"[bold]{email.subject}[/bold]"
        from_display = f"[cyan]{email.from_.name or email.from_.email}[/cyan]"
        date = f"[dim]{email.date.strftime('%Y-%m-%d %H:%M')}[/dim]"
        msg_id = f"[dim]ID: {email.message_id[:MESSAGE_ID_DISPLAY_LENGTH]}...[/dim]"

        return (
            f"{status_str}{subject}\n"
            f"  From: {from_display}  {date}  {msg_id}\n"
            f"  {email.snippet[:SNIPPET_PREVIEW_LENGTH]}...\n"
        )

    def print_email_list(
        self, emails: List[EmailSummary], folder: str = "INBOX"
    ) -> None:
        """Print a list of email summaries.

        Args:
            emails: List of EmailSummary objects
            folder: Folder name for title
        """
        self.console.print(f"\n[bold]📬 {folder}[/bold] ({len(emails)} emails)\n")

        for i, email in enumerate(emails, 1):
            self.console.print(f"[bold cyan]{i}.[/bold cyan] ", end="")
            self.console.print(self.format_email_summary(email))
            if i < len(emails):
                self.console.print("[dim]" + "─" * 60 + "[/dim]")

    def print_email_full(self, email: EmailFull) -> None:
        """Print full email in a panel.

        Args:
            email: EmailFull object to display
        """
        # Build header
        lines = [
            f"[bold]From:[/bold] {email.from_}",
            f"[bold]To:[/bold] {', '.join(str(addr) for addr in email.to)}",
        ]

        if email.cc:
            lines.append(
                f"[bold]Cc:[/bold] {', '.join(str(addr) for addr in email.cc)}"
            )

        lines.append(
            f"[bold]Date:[/bold] {email.date.strftime('%Y-%m-%d %H:%M')}"
        )
        lines.append(f"[bold]Subject:[/bold] {email.subject}")

        if email.labels:
            labels = ", ".join(f"[cyan]{label}[/cyan]" for label in email.labels)
            lines.append(f"[bold]Labels:[/bold] {labels}")

        if email.attachments:
            lines.append(
                f"\n[bold]Attachments ({len(email.attachments)}):[/bold]"
            )
            for att in email.attachments:
                lines.append(
                    f"  📎 {att.filename} [dim]({att.size_human}, {att.mime_type})[/dim]"
                )

        lines.append("\n" + "─" * 80 + "\n")

        # Body
        body = email.body_plain or email.body_html or "[No body]"

        # Truncate if too long
        if len(body) > 3000:
            body = body[:3000]
            lines.append(body)
            lines.append(
                f"\n[yellow][Body truncated — {len(email.body_plain or email.body_html or '')} total characters][/yellow]"
            )
        else:
            lines.append(body)

        content = "\n".join(lines)

        self.console.print(
            Panel(
                content,
                title=f"📧 Email: {email.message_id[:MESSAGE_ID_DISPLAY_LENGTH]}...",
                border_style="cyan",
            )
        )

    # ============ SEARCH RESULTS ============

    def print_search_results(self, result: SearchResult) -> None:
        """Print search results.

        Args:
            result: SearchResult object to display
        """
        self.console.print(f"\n[bold]🔍 Search:[/bold] \"{result.query}\"")
        self.console.print(
            f"[dim]Found {result.total_count} emails. Showing {len(result.emails)}.[/dim]\n"
        )

        for i, email in enumerate(result.emails, 1):
            self.console.print(
                f"[bold cyan]{i}.[/bold cyan] {self.format_email_summary(email)}"
            )
            if i < len(result.emails):
                self.console.print("[dim]" + "─" * 60 + "[/dim]")

        if result.next_page_token:
            self.console.print(
                f"\n[yellow]More results available (token: {result.next_page_token})[/yellow]"
            )

    # ============ THREAD FORMATTING ============

    def print_thread(self, thread: List[EmailFull], message_id: str) -> None:
        """Print email thread.

        Args:
            thread: List of EmailFull objects in the thread
            message_id: Original message ID for title
        """
        self.console.print("=" * 60)
        self.console.print(f"📧 Thread: {len(thread)} message(s)")
        self.console.print(f"[dim]Starting from: {message_id[:MESSAGE_ID_DISPLAY_LENGTH]}...[/dim]")
        self.console.print("=" * 60)

        for i, email in enumerate(thread, 1):
            from_str = f"[cyan]{email.from_.email}[/cyan]"
            to_str = (
                f"[cyan]{email.to[0].email}[/cyan]"
                if email.to and len(email.to) > 0
                else "[dim]unknown[/dim]"
            )

            self.console.print(f"\n[bold][{i}][/bold] {from_str} → {to_str}")
            self.console.print(
                f"[bold]Date:[/bold] {email.date.strftime('%Y-%m-%d %H:%M')}"
            )
            self.console.print(f"[bold]Subject:[/bold] {email.subject}")
            self.console.print(f"[dim]Snippet:[/dim] {email.snippet[:100]}...")

            if i < len(thread):
                self.console.print("[dim]" + "─" * 60 + "[/dim]")

    # ============ SEND/REPLY RESULTS ============

    def print_send_result(self, result: SendEmailResponse) -> None:
        """Print result of sending an email.

        Args:
            result: SendEmailResponse object
        """
        if result.success:
            self.console.print(
                f"\n[green]✅ Email sent successfully![/green]"
            )
            self.console.print(
                f"[dim]Message ID: {result.message_id[:MESSAGE_ID_DISPLAY_LENGTH]}...[/dim]"
            )
        else:
            self.console.print(f"\n[red]❌ Failed to send email[/red]")
            if result.error:
                self.console.print(f"[red]Error: {result.error}[/red]")

    # ============ FOLDER STATISTICS ============

    def build_folder_stats_table(self, folders: List[Folder]) -> Table:
        """Build statistics table from folder data.

        Args:
            folders: List of Folder objects

        Returns:
            Rich Table with folder statistics
        """
        stats_table = Table(
            show_header=True, header_style="bold magenta", box=None
        )
        stats_table.add_column("Folder", style="cyan", width=15)
        stats_table.add_column("Total", justify="right", style="white")
        stats_table.add_column("Unread", justify="right", style="yellow")

        # Folder display config (name, emoji+display, show_unread)
        FOLDER_DISPLAY_CONFIG = [
            ("INBOX", "📥 Inbox", True),
            ("SENT", "📤 Sent", False),
            ("DRAFT", "📝 Drafts", False),
            ("SPAM", "🗑️  Spam", True),
        ]

        # Build table rows
        for folder_name, display_name, show_unread in FOLDER_DISPLAY_CONFIG:
            folder = next((f for f in folders if f.name == folder_name), None)
            if folder:
                total = folder.message_count or 0
                unread = folder.unread_count or 0

                unread_display = (
                    (f"[bold yellow]{unread}[/bold yellow]" if unread > 0 else "0")
                    if show_unread
                    else "-"
                )

                stats_table.add_row(display_name, str(total), unread_display)

        return stats_table
