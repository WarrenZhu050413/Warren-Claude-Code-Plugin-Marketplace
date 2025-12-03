"""Gmail labels management commands."""

import typer
from rich.console import Console

from gmaillm import GmailClient
from gmaillm.formatters import RichFormatter
from gmaillm.helpers.cli import (
    HelpfulGroup,
    OutputFormat,
    parse_output_format,
    show_operation_preview,
    confirm_or_force,
    handle_command_error,
    output_json_or_rich
)
from gmaillm.validators.email import validate_label_name

# Initialize Typer app and console
app = typer.Typer(
    help="Manage Gmail labels",
    cls=HelpfulGroup,  # Show help on missing required args
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()
formatter = RichFormatter(console)


@app.command("examples")
def show_examples() -> None:
    """Show example usage and workflows for Gmail labels."""
    console.print("\n[bold cyan]Gmail Labels - Example Usage[/bold cyan]\n")

    console.print("[bold]📋 LISTING LABELS[/bold]")
    console.print("  [dim]$ gmail labels list[/dim]")
    console.print("  [dim]$ gmail labels list --output-format json[/dim]")
    console.print()

    console.print("[bold]➕ CREATING LABELS[/bold]")
    console.print("  [dim]$ gmail labels create Projects/ClientA[/dim]")
    console.print("  [dim]$ gmail labels create Urgent --force  # Skip confirmation[/dim]")
    console.print()

    console.print("[bold]🗑️  DELETING LABELS[/bold]")
    console.print("  [dim]$ gmail labels delete Projects/ClientA[/dim]")
    console.print("  [dim]$ gmail labels delete Urgent --force[/dim]")
    console.print()

    console.print("[bold yellow]💡 WORKFLOWS[/bold yellow]")
    console.print("  [dim]1. Create project labels:[/dim]")
    console.print("     [dim]gmail labels create Projects/Alpha[/dim]")
    console.print("     [dim]gmail labels create Projects/Beta[/dim]")
    console.print()
    console.print("  [dim]2. Use labels for filtering:[/dim]")
    console.print("     [dim]gmail list --query \"label:Projects/Alpha\"[/dim]")
    console.print("     [dim]gmail search \"label:Urgent\" --max 20[/dim]")
    console.print()
    console.print("  [dim]3. Organize with nested labels:[/dim]")
    console.print("     [dim]gmail labels create Work/Meetings[/dim]")
    console.print("     [dim]gmail labels create Work/Tasks[/dim]")
    console.print()


@app.command("list")
def list_labels(
    output_format: str = typer.Option("rich", "--output-format", help="Output format (rich|json)"),
) -> None:
    """List all labels (system and custom).

    \b
    EXAMPLES:
      $ gmail labels list
      $ gmail labels list --output-format json
    """
    try:
        client = GmailClient()
        folders = client.get_folders()

        # Parse and handle output format
        format_enum = parse_output_format(output_format, console)
        output_json_or_rich(
            format_enum,
            json_data=[f.model_dump(mode='json') for f in folders],
            rich_func=lambda: formatter.print_folder_list(folders, "Gmail Labels")
        )

    except Exception as e:
        console.print(f"[red]✗ Error listing labels: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("create")
def create_label(
    name: str = typer.Argument(..., help="Name of the label to create"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Create a new label.

    \b
    EXAMPLES:
      $ gmail labels create "Work Projects"
      $ gmail labels create "Archive/2024" --force
    """
    try:
        # Validate label name
        validate_label_name(name)

        client = GmailClient()

        # Show preview
        show_operation_preview(
            "Creating Label",
            {"Name": name}
        )

        # Confirm unless --force
        if not confirm_or_force("\nCreate this label?", force, "Creating without confirmation"):
            console.print("Cancelled.")
            return

        # Create label
        label = client.create_label(name)

        console.print(f"\n[green]✅ Label created: {label.name}[/green]")
        console.print(f"   ID: {label.id}")

    except Exception as e:
        handle_command_error("creating label", e)


@app.command("delete")
def delete_label(
    name: str = typer.Argument(..., help="Name of the label to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a custom label.

    \b
    EXAMPLES:
      $ gmail labels delete "Old Project"
      $ gmail labels delete "Archive/2023" --force
    """
    try:
        client = GmailClient()

        # Get all folders to find the label
        folders = client.get_folders()
        label = next((f for f in folders if f.name == name), None)

        if not label:
            console.print(f"[red]✗ Label '{name}' not found[/red]")
            raise typer.Exit(code=1)

        # Prevent deletion of system labels
        if label.type == "system":
            console.print(f"[red]✗ Cannot delete system label '{name}'[/red]")
            raise typer.Exit(code=1)

        # Show preview
        details = {
            "Name": name,
            "Type": label.type
        }
        if label.message_count:
            details["Messages"] = label.message_count

        show_operation_preview("Deleting Label", details)

        # Confirm unless --force
        if not confirm_or_force("\n⚠️  Delete this label? This cannot be undone.", force, "Deleting without confirmation"):
            console.print("Cancelled.")
            return

        # Delete label using the Gmail API
        # Note: GmailClient needs a delete_label method added
        console.print(f"\n[yellow]⚠️  Label deletion not yet implemented in GmailClient[/yellow]")
        console.print("[yellow]   This will be added in a future update[/yellow]")
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]✗ Error deleting label: {e}[/red]")
        raise typer.Exit(code=1)
