"""Gmail workflow management commands."""

from enum import Enum
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from gmaillm import GmailClient
from gmaillm.formatters import RichFormatter
from gmaillm.workflow_config import WorkflowManager, WorkflowConfig
from gmaillm.helpers.cli_utils import (
    show_operation_preview,
    confirm_or_force,
    handle_command_error
)


# Output format enum (duplicated to avoid circular import)
class OutputFormat(str, Enum):
    """Output format for CLI commands."""
    RICH = "rich"  # Rich terminal output (default)
    JSON = "json"  # Raw JSON output

# Initialize Typer app and console
app = typer.Typer(help="Interactive email workflows")
console = Console()
formatter = RichFormatter(console)


@app.command("list")
def list_workflows() -> None:
    """List all configured workflows."""
    try:
        manager = WorkflowManager()
        workflows = manager.list_workflows()

        if not workflows:
            console.print("[yellow]No workflows configured[/yellow]")
            console.print("\nCreate a workflow: [cyan]gmail workflows create <id> --query \"...\"[/cyan]")
            return

        # Create table
        table = Table(title="Email Workflows")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Query", style="dim")
        table.add_column("Auto-Read", justify="center")

        for workflow_id, config in sorted(workflows.items()):
            auto_read = "✓" if config.auto_mark_read else "✗"
            table.add_row(
                workflow_id,
                config.name,
                config.query[:50] + "..." if len(config.query) > 50 else config.query,
                auto_read
            )

        console.print(table)
        console.print(f"\n[dim]Total: {len(workflows)} workflow(s)[/dim]")
        console.print(f"\nUsage: [cyan]gmail workflows run <id>[/cyan]")

    except Exception as e:
        console.print(f"[red]✗ Error listing workflows: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("show")
def show_workflow(
    workflow_id: str = typer.Argument(..., help="Workflow ID to show"),
) -> None:
    """Show detailed information about a workflow."""
    try:
        manager = WorkflowManager()
        config = manager.get_workflow(workflow_id)

        console.print("=" * 60)
        console.print(f"Workflow: {workflow_id}")
        console.print("=" * 60)
        console.print(f"Name: {config.name}")
        console.print(f"Query: {config.query}")
        console.print(f"Description: {config.description or '(none)'}")
        console.print(f"Auto-mark read on skip: {'Yes' if config.auto_mark_read else 'No'}")
        console.print()
        console.print(f"Usage: [cyan]gmail workflows run {workflow_id}[/cyan]")

    except KeyError as e:
        console.print(f"[red]✗ {e}[/red]")
        console.print("\nAvailable workflows: [cyan]gmail workflows list[/cyan]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error showing workflow: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("run")
def run_workflow(
    workflow_id: Optional[str] = typer.Argument(None, help="Workflow ID to run"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Ad-hoc query (instead of named workflow)"),
    max_results: int = typer.Option(100, "--max", "-n", help="Maximum emails to process"),
    format: OutputFormat = typer.Option(OutputFormat.RICH, "--format", help="Output format"),
) -> None:
    """Run a workflow (named or ad-hoc query).

    \b
    EXAMPLES:
      Run named workflow:
        $ gmail workflows run clear

      Ad-hoc query:
        $ gmail workflows run --query "from:boss@company.com is:unread"

      JSON output (programmatic):
        $ gmail workflows run clear --format json
    """
    try:
        client = GmailClient()

        # Determine query and settings
        if workflow_id:
            # Named workflow
            manager = WorkflowManager()
            config = manager.get_workflow(workflow_id)
            search_query = config.query
            auto_mark_read = config.auto_mark_read
            workflow_name = config.name
        elif query:
            # Ad-hoc query
            search_query = query
            auto_mark_read = True  # Default for ad-hoc
            workflow_name = "Ad-hoc Workflow"
        else:
            console.print("[red]✗ Either workflow ID or --query is required[/red]")
            console.print("\nUsage: [cyan]gmail workflows run <id>[/cyan]")
            console.print("   Or: [cyan]gmail workflows run --query \"is:unread\"[/cyan]")
            raise typer.Exit(code=1)

        # Execute search
        result = client.search_emails(query=search_query, folder="", max_results=max_results)

        # JSON output mode (programmatic)
        if format == OutputFormat.JSON:
            console.print_json(data=result.model_dump(mode='json'))
            return

        # Interactive mode
        if not result.emails:
            console.print(f"[yellow]No emails found for: {search_query}[/yellow]")
            return

        console.print(f"\n[bold]{workflow_name}[/bold]")
        console.print(f"Query: [dim]{search_query}[/dim]")
        console.print(f"Found: {len(result.emails)} email(s)\n")

        # Process each email interactively
        for i, email_summary in enumerate(result.emails, 1):
            console.print("=" * 60)
            console.print(f"Email {i} of {len(result.emails)}")
            console.print("=" * 60)

            # Fetch full email details
            email = client.read_email(email_summary.message_id, format="full")

            # Display email
            formatter.print_email_full(email)

            # Prompt for action
            console.print("\n[bold]Actions:[/bold]")
            console.print("  [cyan]r[/cyan] - Reply (then archive)")
            console.print("  [cyan]a[/cyan] - Archive")
            console.print("  [cyan]s[/cyan] - Skip" + (" (mark as read)" if auto_mark_read else ""))
            console.print("  [cyan]q[/cyan] - Quit workflow")

            action = console.input("\n[bold]Choose action:[/bold] ").lower().strip()

            if action == 'r':
                # Reply
                body = console.input("[bold]Reply body:[/bold] ")
                if body.strip():
                    client.reply_email(message_id=email.message_id, body=body)
                    console.print("[green]✅ Reply sent[/green]")

                    # Archive after replying
                    client.modify_labels(email.message_id, remove_labels=["INBOX", "UNREAD"])
                    console.print("[green]✅ Archived[/green]")
                else:
                    console.print("[yellow]Reply cancelled (empty body)[/yellow]")

            elif action == 'a':
                # Archive
                client.modify_labels(email.message_id, remove_labels=["INBOX", "UNREAD"])
                console.print("[green]✅ Archived[/green]")

            elif action == 's':
                # Skip
                if auto_mark_read:
                    client.modify_labels(email.message_id, remove_labels=["UNREAD"])
                    console.print("[yellow]Skipped (marked as read)[/yellow]")
                else:
                    console.print("[yellow]Skipped[/yellow]")

            elif action == 'q':
                # Quit
                console.print(f"\n[yellow]Exiting workflow (processed {i-1} of {len(result.emails)})[/yellow]")
                break

            else:
                console.print(f"[red]Invalid action: {action}[/red]")
                console.print("[yellow]Skipping this email[/yellow]")

        console.print(f"\n[green]✅ Workflow complete![/green]")

    except KeyError as e:
        console.print(f"[red]✗ {e}[/red]")
        console.print("\nAvailable workflows: [cyan]gmail workflows list[/cyan]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error running workflow: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("create")
def create_workflow(
    workflow_id: str = typer.Argument(..., help="Workflow ID (kebab-case)"),
    query: str = typer.Option(..., "--query", "-q", help="Gmail search query"),
    name: Optional[str] = typer.Option(None, "--name", help="Human-readable name"),
    description: str = typer.Option("", "--description", "-d", help="Workflow description"),
    auto_mark_read: bool = typer.Option(True, "--auto-mark-read/--no-auto-mark-read", help="Mark as read on skip"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite if exists"),
) -> None:
    """Create a new workflow.

    \b
    EXAMPLE:
      $ gmail workflows create urgent \\
          --query "is:important is:unread" \\
          --name "Process Urgent" \\
          --description "Handle urgent emails first"
    """
    try:
        manager = WorkflowManager()

        # Check if exists
        try:
            existing = manager.get_workflow(workflow_id)
            if not force:
                console.print(f"[red]✗ Workflow '{workflow_id}' already exists[/red]")
                console.print("\nUse --force to overwrite")
                raise typer.Exit(code=1)
            console.print(f"[yellow]--force: Overwriting existing workflow[/yellow]")
        except KeyError:
            pass  # Doesn't exist, OK to create

        # Create config
        config = WorkflowConfig(
            name=name or workflow_id.replace("-", " ").title(),
            query=query,
            description=description,
            auto_mark_read=auto_mark_read
        )

        # Save
        manager.save_workflow(workflow_id, config)

        console.print(f"\n[green]✅ Workflow created: {workflow_id}[/green]")
        console.print(f"   Name: {config.name}")
        console.print(f"   Query: {config.query}")
        console.print(f"\nUsage: [cyan]gmail workflows run {workflow_id}[/cyan]")

    except Exception as e:
        console.print(f"[red]✗ Error creating workflow: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("delete")
def delete_workflow(
    workflow_id: str = typer.Argument(..., help="Workflow ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a workflow."""
    try:
        manager = WorkflowManager()

        # Check if exists
        try:
            config = manager.get_workflow(workflow_id)
        except KeyError:
            console.print(f"[red]✗ Workflow '{workflow_id}' not found[/red]")
            console.print("\nAvailable workflows: [cyan]gmail workflows list[/cyan]")
            raise typer.Exit(code=1)

        # Show what will be deleted
        show_operation_preview(
            "Deleting Workflow",
            {
                "ID": workflow_id,
                "Name": config.name,
                "Query": config.query
            }
        )

        # Confirm unless --force
        if not confirm_or_force("\n⚠️  Delete this workflow?", force, "Deleting without confirmation"):
            console.print("Cancelled.")
            return

        # Delete
        manager.delete_workflow(workflow_id)

        console.print(f"\n[green]✅ Workflow deleted: {workflow_id}[/green]")

    except Exception as e:
        handle_command_error("deleting workflow", e)
