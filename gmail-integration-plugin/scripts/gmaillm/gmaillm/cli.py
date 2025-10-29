#!/usr/bin/env python3
"""Command-line interface for gmaillm using Typer."""

from enum import Enum
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from gmaillm import GmailClient, SendEmailRequest
from gmaillm.formatters import RichFormatter

# Import helper utilities
from gmaillm.helpers.config import (
    expand_email_groups,
    load_email_groups
)

# Import validators
from gmaillm.validators.email import (
    validate_email_list,
    validate_attachment_paths
)

# Import command modules
from gmaillm.commands import labels, styles, groups, config as config_commands

# Initialize Typer app and console
app = typer.Typer(
    name="gmaillm",
    help="Gmail CLI with LLM-friendly operations and progressive disclosure patterns",
    add_completion=True,
    no_args_is_help=True,
)
console = Console()
formatter = RichFormatter(console)

# Output format enum (kept for backward compatibility)
class OutputFormat(str, Enum):
    """Output format for CLI commands."""
    RICH = "rich"  # Rich terminal output (default)
    JSON = "json"  # Raw JSON output

# Preview lengths (kept for status command)
SNIPPET_PREVIEW_LENGTH = 80
MESSAGE_ID_DISPLAY_LENGTH = 8


# ============ HELPER FUNCTIONS ============

def _get_folder_by_name(folders, folder_name):
    """Get folder by name from list."""
    return next((f for f in folders if f.name == folder_name), None)


# ============ MAIN COMMANDS ============

@app.command()
def verify() -> None:
    """Verify authentication and setup."""
    try:
        client = GmailClient()
        result = client.verify_setup()

        console.print("=" * 60)
        console.print("gmaillm Setup Verification")
        console.print("=" * 60)

        if result["auth"]:
            console.print("[green]✓[/green] Authentication: Working")
            if result["email_address"]:
                console.print(f"[green]✓[/green] Authenticated as: {result['email_address']}")
        else:
            console.print("[red]✗[/red] Authentication: Failed")

        console.print(f"[green]✓[/green] Folders accessible: {result['folders']}")

        if result["inbox_accessible"]:
            console.print("[green]✓[/green] Inbox: Accessible")
        else:
            console.print("[red]✗[/red] Inbox: Not accessible")

        if result["errors"]:
            console.print("\n[red]Errors:[/red]")
            for error in result["errors"]:
                console.print(f"  - {error}")
        else:
            console.print("\n[green]✅ All checks passed![/green]")

    except Exception as e:
        console.print(f"[red]✗ Setup verification failed: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def setup_auth(
    oauth_keys: Optional[str] = typer.Option(
        None, "--oauth-keys", help="Path to OAuth2 client secrets (gcp-oauth.keys.json)"
    ),
    credentials: Optional[str] = typer.Option(
        None,
        "--credentials",
        help="Path to save credentials (default: ~/.gmail-mcp/credentials.json)",
    ),
    port: int = typer.Option(8080, "--port", help="Local server port for OAuth callback"),
) -> None:
    """Set up Gmail API authentication via OAuth2."""
    try:
        from gmaillm.setup_auth import setup_authentication

        console.print("=" * 70)
        console.print("  Gmail API Authentication Setup")
        console.print("=" * 70)
        console.print()

        result = setup_authentication(
            oauth_keys_file=oauth_keys,
            credentials_file=credentials,
            port=port,
        )

        if result is None:
            console.print(
                "\n[yellow]⚠️  Setup incomplete. Please address the issues above.[/yellow]"
            )
            raise typer.Exit(code=1)
        else:
            console.print("\n[green]✅ Setup complete![/green]")
            console.print("\nYou can now use the Gmail CLI and Python library.")
            console.print("\nVerify with: [cyan]gmail verify[/cyan]")

            console.print("\n" + "=" * 70)
            console.print("📊 Next Steps (Optional)")
            console.print("=" * 70)
            console.print("\n💡 Install shell completions for faster typing:")
            console.print("   [cyan]$ gmail --install-completion[/cyan]")
            console.print("\nThen restart your shell to enable tab-completion:")
            console.print("   [cyan]$ exec $SHELL[/cyan]\n")

    except Exception as e:
        console.print(f"\n[red]✗ Authentication failed: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def status() -> None:
    """Show current Gmail account status with beautiful formatting."""
    try:
        client = GmailClient()

        # Verify authentication
        result = client.verify_setup()

        if not result["auth"] or not result["email_address"]:
            console.print(
                Panel(
                    "[red]✗ Not authenticated[/red]\n\n"
                    + "\n".join(f"  - {error}" for error in result["errors"]),
                    title="Authentication Failed",
                    border_style="red",
                )
            )
            raise typer.Exit(code=1)

        # Account header
        console.print(
            Panel(
                f"[bold cyan]{result['email_address']}[/bold cyan]",
                title="📧 Gmail Account",
                border_style="cyan",
            )
        )

        # Get folder statistics and display
        folders = client.get_folders()
        stats_table = formatter.build_folder_stats_table(folders)
        console.print(Panel(stats_table, title="📊 Folder Statistics", border_style="blue"))

        # Get most recent email (the "current" email)
        try:
            recent_emails = client.list_emails(folder="INBOX", max_results=1)
            if recent_emails.emails:
                recent = recent_emails.emails[0]

                # Format recent email display
                from_display = f"{recent.from_.name or recent.from_.email}"
                date_display = recent.date.strftime("%Y-%m-%d %H:%M")

                recent_info = f"""[bold]From:[/bold] {from_display}
[bold]Subject:[/bold] {recent.subject}
[bold]Date:[/bold] {date_display}
[bold]Preview:[/bold] {recent.snippet[:SNIPPET_PREVIEW_LENGTH]}..."""

                if recent.is_unread:
                    recent_info = "🔵 [bold yellow]UNREAD[/bold yellow]\n\n" + recent_info

                console.print(
                    Panel(
                        recent_info,
                        title=f"📬 Most Recent Email (ID: {recent.message_id[:MESSAGE_ID_DISPLAY_LENGTH]}...)",
                        border_style="green",
                    )
                )
        except Exception as e:
            console.print(f"[dim]Could not fetch recent email: {e}[/dim]")

        # Quick stats summary
        total_labels = len(folders)
        user_labels = len([f for f in folders if f.type == "user"])
        system_labels = len([f for f in folders if f.type == "system"])

        summary_items = [
            f"[cyan]Total Labels:[/cyan] {total_labels}",
            f"[blue]Custom:[/blue] {user_labels}",
            f"[magenta]System:[/magenta] {system_labels}",
        ]

        console.print("\n" + " | ".join(summary_items))

        # Unread indicator
        inbox_folder = _get_folder_by_name(folders, "INBOX")
        if inbox_folder and inbox_folder.unread_count and inbox_folder.unread_count > 0:
            console.print(
                f"\n[bold yellow]⚠️  You have {inbox_folder.unread_count} unread message(s)[/bold yellow]"
            )
        else:
            console.print("\n[green]✓ All caught up![/green]")

    except Exception as e:
        console.print(f"[red]✗ Failed to get status: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def list(
    folder: str = typer.Option("INBOX", "--folder", help="Folder to list from"),
    max: int = typer.Option(10, "--max", "-n", help="Maximum results"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Optional search query"),
    format: OutputFormat = typer.Option(OutputFormat.RICH, "--format", help="Output format"),
) -> None:
    """List emails from a folder."""
    try:
        client = GmailClient()
        result = client.list_emails(folder=folder, max_results=max, query=query)

        if format == OutputFormat.JSON:
            console.print_json(data=result.model_dump(mode='json'))
        else:  # RICH
            formatter.print_email_list(result.emails, folder)
    except Exception as e:
        console.print(f"[red]Error listing emails: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def read(
    message_id: str = typer.Argument(..., help="Message ID to read"),
    full: bool = typer.Option(False, "--full", help="Show full email body"),
    format: OutputFormat = typer.Option(OutputFormat.RICH, "--format", help="Output format"),
) -> None:
    """Read a specific email."""
    try:
        client = GmailClient()
        format_type = "full" if full else "summary"
        email = client.read_email(message_id, format=format_type)

        if format == OutputFormat.JSON:
            console.print_json(data=email.model_dump(mode='json'))
        else:  # RICH
            formatter.print_email_full(email)
    except Exception as e:
        console.print(f"[red]Error reading email: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def thread(
    message_id: str = typer.Argument(..., help="Message ID in the thread"),
) -> None:
    """Show entire email thread."""
    try:
        client = GmailClient()
        thread = client.get_thread(message_id)
        formatter.print_thread(thread, message_id)

    except Exception as e:
        console.print(f"[red]Error getting thread: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Gmail search query"),
    folder: str = typer.Option("INBOX", "--folder", help="Folder to search in"),
    max: int = typer.Option(10, "--max", "-n", help="Maximum results"),
    format: OutputFormat = typer.Option(OutputFormat.RICH, "--format", help="Output format"),
) -> None:
    """Search emails."""
    try:
        client = GmailClient()
        result = client.search_emails(query=query, folder=folder, max_results=max)

        if format == OutputFormat.JSON:
            console.print_json(data=result.model_dump(mode='json'))
        else:  # RICH
            formatter.print_search_results(result)
    except Exception as e:
        console.print(f"[red]Error searching emails: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def reply(
    message_id: str = typer.Argument(..., help="Message ID to reply to"),
    body: str = typer.Option(..., "--body", help="Reply body text"),
    reply_all: bool = typer.Option(False, "--reply-all", help="Reply to all recipients"),
) -> None:
    """Reply to an email."""
    try:
        client = GmailClient()

        # Get original email for context
        original = client.read_email(message_id, format="summary")

        # Show preview
        console.print("=" * 60)
        console.print("Reply Preview")
        console.print("=" * 60)
        console.print(f"To: {original.from_.email}")
        console.print(f"Subject: Re: {original.subject}")
        console.print(f"\n{body}")
        console.print("=" * 60)

        # Confirm
        response = typer.confirm("\nSend this reply?")
        if not response:
            console.print("Cancelled.")
            return

        # Send reply
        result = client.reply_email(message_id=message_id, body=body, reply_all=reply_all)

        console.print(f"\n[green]✅ Reply sent! Message ID: {result.message_id}[/green]")

    except Exception as e:
        console.print(f"[red]Error sending reply: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def send(
    to: List[str] = typer.Option(..., "--to", "-t", help="Recipient email(s)"),
    subject: str = typer.Option(..., "--subject", "-s", help="Email subject"),
    body: str = typer.Option(..., "--body", "-b", help="Email body"),
    cc: Optional[List[str]] = typer.Option(None, "--cc", help="CC recipient(s)"),
    attachments: Optional[List[str]] = typer.Option(
        None, "--attachment", "-a", help="Attachment file path(s)"
    ),
    yolo: bool = typer.Option(False, "--yolo", help="Send without confirmation"),
) -> None:
    """Send a new email."""
    try:
        client = GmailClient()

        # Validate email addresses
        validate_email_list(to, "recipient")
        if cc:
            validate_email_list(cc, "CC")

        # Validate attachments
        validated_attachments = validate_attachment_paths(attachments)

        # Expand email groups (@groupname -> actual emails)
        to_list = expand_email_groups(to)
        cc_list = expand_email_groups(cc) if cc else None

        # Show preview
        console.print("=" * 60)
        console.print("Email Preview")
        console.print("=" * 60)
        console.print(f"To: {', '.join(to_list)}")
        if cc_list:
            console.print(f"Cc: {', '.join(cc_list)}")
        console.print(f"Subject: {subject}")
        console.print(f"\n{body}")
        if validated_attachments:
            console.print(f"\nAttachments: {len(validated_attachments)} file(s)")
            for att in validated_attachments:
                console.print(f"  - {att}")
        console.print("=" * 60)

        # Confirm unless yolo
        if not yolo:
            response = typer.confirm("\nSend this email?")
            if not response:
                console.print("Cancelled.")
                return
        else:
            console.print("\n[yellow]YOLO mode: Sending without confirmation...[/yellow]")

        # Send email
        request = SendEmailRequest(
            to=to_list, subject=subject, body=body, cc=cc_list, attachments=validated_attachments
        )
        result = client.send_email(request)

        console.print(f"\n[green]✅ Email sent! Message ID: {result.message_id}[/green]")

    except Exception as e:
        console.print(f"[red]Error sending email: {e}[/red]")
        raise typer.Exit(code=1)


# ============ SUBCOMMAND REGISTRATION ============

# Register command modules
app.add_typer(labels.app, name="labels")
app.add_typer(groups.app, name="groups")
app.add_typer(styles.app, name="styles")
app.add_typer(config_commands.app, name="config")


# ============ MAIN ENTRY POINT ============

def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
