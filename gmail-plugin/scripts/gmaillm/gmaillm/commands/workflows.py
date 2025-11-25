"""Gmail workflow management commands."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from gmaillm import GmailClient
from gmaillm.formatters import RichFormatter
from gmaillm.helpers.cli import (
    OutputFormat,
    confirm_or_force,
    handle_command_error,
    output_json_or_rich,
    parse_output_format,
    show_operation_preview,
)
from gmaillm.workflow_config import WorkflowConfig, WorkflowManager
from gmaillm.workflow_state import (
    WorkflowAction,
    WorkflowResponse,
    WorkflowStateManager,
)

# Initialize Typer app and console
app = typer.Typer(
    help="Interactive email workflows",
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()
formatter = RichFormatter(console)


@app.command("examples")
def show_examples() -> None:
    """Show example usage and workflows for email workflows."""
    console.print("\n[bold cyan]Email Workflows - Example Usage[/bold cyan]\n")

    console.print("[bold]📋 LISTING WORKFLOWS[/bold]")
    console.print("  [dim]$ gmail workflows list[/dim]")
    console.print("  [dim]$ gmail workflows list --output-format json[/dim]")
    console.print()

    console.print("[bold]👁️  VIEWING WORKFLOW DETAILS[/bold]")
    console.print("  [dim]$ gmail workflows show clear[/dim]")
    console.print()

    console.print("[bold]▶️  RUNNING WORKFLOWS (Interactive)[/bold]")
    console.print("  [dim]$ gmail workflows run clear           # Run named workflow[/dim]")
    console.print("  [dim]$ gmail workflows run \"is:unread\"     # Run ad-hoc query[/dim]")
    console.print()

    console.print("[bold]🤖 LLM-FRIENDLY WORKFLOWS (Programmatic)[/bold]")
    console.print("  [dim]$ gmail workflows start clear         # Start workflow, get token[/dim]")
    console.print("  [dim]$ gmail workflows continue <token> archive   # Archive current email[/dim]")
    console.print("  [dim]$ gmail workflows continue <token> skip      # Skip to next email[/dim]")
    console.print("  [dim]$ gmail workflows continue <token> reply -b \"Thanks!\"  # Reply and archive[/dim]")
    console.print()

    console.print("[bold]➕ CREATING WORKFLOWS[/bold]")
    console.print("  [dim]$ gmail workflows create daily --query \"is:unread in:inbox\" --auto-read[/dim]")
    console.print("  [dim]$ gmail workflows create review --query \"label:review\" --name \"Code Reviews\"[/dim]")
    console.print()

    console.print("[bold]🗑️  DELETING WORKFLOWS[/bold]")
    console.print("  [dim]$ gmail workflows delete daily[/dim]")
    console.print("  [dim]$ gmail workflows delete review --force[/dim]")
    console.print()

    console.print("[bold yellow]💡 WORKFLOWS[/bold yellow]")
    console.print("  [dim]1. Create a daily inbox clearing workflow:[/dim]")
    console.print("     [dim]gmail workflows create daily-clear --query \"is:unread in:inbox\" --auto-read[/dim]")
    console.print()
    console.print("  [dim]2. Run it every morning:[/dim]")
    console.print("     [dim]gmail workflows run daily-clear[/dim]")
    console.print()
    console.print("  [dim]3. Create project-specific workflows:[/dim]")
    console.print("     [dim]gmail workflows create proj-alpha --query \"label:Projects/Alpha is:unread\"[/dim]")
    console.print("     [dim]gmail workflows run proj-alpha[/dim]")
    console.print()


@app.command("list")
def list_workflows(
    output_format: str = typer.Option("rich", "--output-format", help="Output format (rich|json)"),
) -> None:
    """List all configured workflows."""
    try:
        manager = WorkflowManager()
        workflows = manager.list_workflows()

        # Parse output format
        format_enum = parse_output_format(output_format, console)

        # Prepare JSON data
        workflows_list = [
            {
                "id": workflow_id,
                "name": config.name,
                "query": config.query,
                "auto_mark_read": config.auto_mark_read,
                "description": config.description
            }
            for workflow_id, config in sorted(workflows.items())
        ]

        # Define rich output function
        def print_rich() -> None:
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
            console.print("\nUsage: [cyan]gmail workflows run <id>[/cyan]")

        # Output in appropriate format
        output_json_or_rich(format_enum, workflows_list, print_rich)

    except Exception as e:
        console.print(f"[red]✗ Error listing workflows: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("show")
def show_workflow(
    workflow_id: str = typer.Argument(..., help="Workflow ID to show"),
    output_format: str = typer.Option("rich", "--output-format", help="Output format (rich|json)"),
) -> None:
    """Show detailed information about a workflow."""
    try:
        manager = WorkflowManager()
        config = manager.get_workflow(workflow_id)

        # Parse output format
        format_enum = parse_output_format(output_format, console)

        # Prepare JSON data
        workflow_data = {
            "id": workflow_id,
            "name": config.name,
            "query": config.query,
            "description": config.description,
            "auto_mark_read": config.auto_mark_read
        }

        # Define rich output function
        def print_rich() -> None:
            console.print("=" * 60)
            console.print(f"Workflow: {workflow_id}")
            console.print("=" * 60)
            console.print(f"Name: {config.name}")
            console.print(f"Query: {config.query}")
            console.print(f"Description: {config.description or '(none)'}")
            console.print(f"Auto-mark read on skip: {'Yes' if config.auto_mark_read else 'No'}")
            console.print()
            console.print(f"Usage: [cyan]gmail workflows run {workflow_id}[/cyan]")

        # Output in appropriate format
        output_json_or_rich(format_enum, workflow_data, print_rich)

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
    output_format: OutputFormat = typer.Option(OutputFormat.RICH, "--output-format", help="Output format"),
) -> None:
    """Run a workflow (named or ad-hoc query).

    \b
    EXAMPLES:
      $ gmail workflows run clear
      $ gmail workflows run --query "from:boss@company.com is:unread"
      $ gmail workflows run clear --output-format json
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
        if output_format == OutputFormat.JSON:
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

            # Prompt for action (loop until valid action)
            while True:
                console.print("\n[bold]Actions:[/bold]")
                console.print("  [cyan]v[/cyan] - View full body")
                console.print("  [cyan]r[/cyan] - Reply (then archive)")
                console.print("  [cyan]a[/cyan] - Archive")
                console.print("  [cyan]s[/cyan] - Skip" + (" (mark as read)" if auto_mark_read else ""))
                console.print("  [cyan]q[/cyan] - Quit workflow")

                action = console.input("\n[bold]Choose action:[/bold] ").lower().strip()

                if action == 'v':
                    # View full body
                    body = email.body_plain or email.body_html or "[No body]"
                    console.print("\n" + "=" * 60)
                    console.print("[bold]Full Email Body:[/bold]")
                    console.print("=" * 60)
                    console.print(body)
                    console.print("=" * 60 + "\n")
                    # Continue loop to show actions again
                    continue

                # Break loop for other actions
                break

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

        console.print("\n[green]✅ Workflow complete![/green]")

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
      $ gmail workflows create urgent \
          --query "is:important is:unread" \
          --name "Process Urgent" \
          --description "Handle urgent emails first"
    """
    try:
        manager = WorkflowManager()

        # Check if exists
        try:
            manager.get_workflow(workflow_id)
            if not force:
                console.print(f"[red]✗ Workflow '{workflow_id}' already exists[/red]")
                console.print("\nUse --force to overwrite")
                raise typer.Exit(code=1)
            console.print("[yellow]--force: Overwriting existing workflow[/yellow]")
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


@app.command("start")
def start_workflow(
    workflow_id: Optional[str] = typer.Argument(None, help="Workflow ID to start"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Ad-hoc query (instead of named workflow)"),
    max_results: int = typer.Option(100, "--max", "-n", help="Maximum emails to process"),
) -> None:
    """Start workflow, returns JSON with first email + continuation token.

    Use the returned token with 'gmail workflows continue <token> <action>' to process emails.
    Token expires after 1 hour.

    \b
    EXAMPLES:
      gmail workflows start clear
      gmail workflows start --query "is:unread from:boss@example.com"

    \b
    RETURNS:
      {
        "success": true,
        "token": "abc123...",
        "email": { /* email data */ },
        "progress": {"total": 10, "processed": 0, "remaining": 10, "current": 1}
      }

    \b
    NEXT STEP:
      gmail workflows continue <token> archive
    """
    try:
        client = GmailClient()
        state_manager = WorkflowStateManager()

        # Determine query and settings
        if workflow_id:
            manager = WorkflowManager()
            config = manager.get_workflow(workflow_id)
            search_query = config.query
            auto_mark_read = config.auto_mark_read
            workflow_name = config.name
        elif query:
            search_query = query
            auto_mark_read = True
            workflow_id = "adhoc"
            workflow_name = "Ad-hoc Workflow"
        else:
            response = WorkflowResponse(
                success=False,
                message="Either workflow ID or --query is required",
                progress={"total": 0, "processed": 0, "remaining": 0}
            )
            console.print_json(data=response.model_dump(mode='json'))
            raise typer.Exit(code=1)

        # Execute search
        result = client.search_emails(query=search_query, folder="", max_results=max_results)

        if not result.emails:
            response = WorkflowResponse(
                success=True,
                message=f"No emails found for query: {search_query}",
                progress={"total": 0, "processed": 0, "remaining": 0},
                completed=True
            )
            console.print_json(data=response.model_dump(mode='json'))
            return

        # Create workflow state
        email_ids = [email.message_id for email in result.emails]
        state = state_manager.create_state(
            workflow_id=workflow_id,
            query=search_query,
            email_ids=email_ids,
            auto_mark_read=auto_mark_read
        )

        # Get first email
        first_email = client.read_email(state.current_email_id, format="full")

        # Build response
        response = WorkflowResponse(
            success=True,
            token=state.token,
            email=first_email.model_dump(mode='json'),
            message=f"Started workflow: {workflow_name}",
            progress={
                "total": len(email_ids),
                "processed": 0,
                "remaining": len(email_ids),
                "current": 1
            }
        )

        console.print_json(data=response.model_dump(mode='json'))

    except Exception as e:
        response = WorkflowResponse(
            success=False,
            message=f"Error starting workflow: {e}",
            progress={"total": 0, "processed": 0, "remaining": 0}
        )
        console.print_json(data=response.model_dump(mode='json'))
        raise typer.Exit(code=1)


@app.command("continue")
def continue_workflow(
    token: str = typer.Argument(..., help="Continuation token from 'start' command"),
    action: str = typer.Argument(..., help="Action: view, reply, archive, skip, quit"),
    reply_body: Optional[str] = typer.Option(None, "--reply-body", "-b", help="Reply body (for 'reply' action)"),
) -> None:
    """Process current email with action, returns JSON with next email + token.

    \b
    ACTIONS:
      view     - Return full email body (no state change)
      archive  - Archive email and advance to next
      skip     - Skip email (mark as read if configured) and advance
      reply    - Send reply (requires --reply-body) and archive
      quit     - End workflow session

    \b
    EXAMPLES:
      gmail workflows continue abc123 archive
      gmail workflows continue abc123 skip
      gmail workflows continue abc123 reply --reply-body "Thanks!"
      gmail workflows continue abc123 view
      gmail workflows continue abc123 quit

    \b
    RETURNS:
      {
        "success": true,
        "token": "abc123...",
        "email": { /* next email */ },
        "message": "Archived",
        "progress": {"total": 10, "processed": 1, "remaining": 9, "current": 2},
        "completed": false
      }
    """
    try:
        client = GmailClient()
        state_manager = WorkflowStateManager()

        # Load state
        try:
            state = state_manager.load_state(token)
        except ValueError as e:
            response = WorkflowResponse(
                success=False,
                message=str(e),
                progress={"total": 0, "processed": 0, "remaining": 0}
            )
            console.print_json(data=response.model_dump(mode='json'))
            raise typer.Exit(code=1)

        # Get current email
        current_email = client.read_email(state.current_email_id, format="full")

        # Process action
        action = action.lower().strip()

        if action == "view":
            # Return email with full body
            response = WorkflowResponse(
                success=True,
                token=state.token,  # Same token, no state change
                email=current_email.model_dump(mode='json'),
                message="Email body returned",
                progress={
                    "total": len(state.email_ids),
                    "processed": state.processed,
                    "remaining": len(state.email_ids) - state.current_index,
                    "current": state.current_index + 1
                }
            )
            console.print_json(data=response.model_dump(mode='json'))
            return

        elif action == "reply":
            if not reply_body or not reply_body.strip():
                response = WorkflowResponse(
                    success=False,
                    token=state.token,
                    message="--reply-body is required for 'reply' action",
                    progress={
                        "total": len(state.email_ids),
                        "processed": state.processed,
                        "remaining": len(state.email_ids) - state.current_index,
                        "current": state.current_index + 1
                    }
                )
                console.print_json(data=response.model_dump(mode='json'))
                raise typer.Exit(code=1)

            # Send reply
            client.reply_email(message_id=state.current_email_id, body=reply_body)

            # Archive
            client.modify_labels(state.current_email_id, remove_labels=["INBOX", "UNREAD"])

            # Advance state
            state.advance()
            action_message = "Reply sent and archived"

        elif action == "archive":
            # Archive
            client.modify_labels(state.current_email_id, remove_labels=["INBOX", "UNREAD"])

            # Advance state
            state.advance()
            action_message = "Archived"

        elif action == "skip":
            # Mark as read if configured
            if state.auto_mark_read:
                client.modify_labels(state.current_email_id, remove_labels=["UNREAD"])
                action_message = "Skipped (marked as read)"
            else:
                action_message = "Skipped"

            # Advance state
            state.advance()

        elif action == "quit":
            # Delete state and exit
            state_manager.delete_state(token)
            response = WorkflowResponse(
                success=True,
                message=f"Workflow ended (processed {state.processed} of {len(state.email_ids)})",
                progress={
                    "total": len(state.email_ids),
                    "processed": state.processed,
                    "remaining": len(state.email_ids) - state.processed,
                },
                completed=True
            )
            console.print_json(data=response.model_dump(mode='json'))
            return

        else:
            response = WorkflowResponse(
                success=False,
                token=state.token,
                message=f"Invalid action: {action}. Use: view, reply, archive, skip, quit",
                progress={
                    "total": len(state.email_ids),
                    "processed": state.processed,
                    "remaining": len(state.email_ids) - state.current_index,
                    "current": state.current_index + 1
                }
            )
            console.print_json(data=response.model_dump(mode='json'))
            raise typer.Exit(code=1)

        # Check if workflow is complete
        if not state.has_more:
            state_manager.delete_state(token)
            response = WorkflowResponse(
                success=True,
                message=f"{action_message}. Workflow complete! Processed {state.processed} emails.",
                progress={
                    "total": len(state.email_ids),
                    "processed": state.processed,
                    "remaining": 0
                },
                completed=True
            )
            console.print_json(data=response.model_dump(mode='json'))
            return

        # Save updated state
        state_manager.save_state(state)

        # Get next email
        next_email = client.read_email(state.current_email_id, format="full")

        # Build response
        response = WorkflowResponse(
            success=True,
            token=state.token,
            email=next_email.model_dump(mode='json'),
            message=action_message,
            progress={
                "total": len(state.email_ids),
                "processed": state.processed,
                "remaining": len(state.email_ids) - state.current_index,
                "current": state.current_index + 1
            }
        )

        console.print_json(data=response.model_dump(mode='json'))

    except Exception as e:
        response = WorkflowResponse(
            success=False,
            message=f"Error continuing workflow: {e}",
            progress={"total": 0, "processed": 0, "remaining": 0}
        )
        console.print_json(data=response.model_dump(mode='json'))
        raise typer.Exit(code=1)


@app.command("cleanup")
def cleanup_states() -> None:
    """Remove expired workflow state files (older than 1 hour)."""
    try:
        state_manager = WorkflowStateManager()
        deleted = state_manager.cleanup_expired()

        console.print(f"[green]✅ Cleaned up {deleted} expired workflow state(s)[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error cleaning up states: {e}[/red]")
        raise typer.Exit(code=1)
