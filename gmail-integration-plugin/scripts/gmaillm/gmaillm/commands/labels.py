"""Gmail labels management commands."""

import typer
from rich.console import Console

from gmaillm import GmailClient
from gmaillm.formatters import RichFormatter
from gmaillm.helpers.typer_utils import HelpfulGroup
from gmaillm.helpers.cli_utils import (
    show_operation_preview,
    confirm_or_force,
    handle_command_error
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
        from enum import Enum

        # Define OutputFormat enum locally to avoid circular import
        class OutputFormat(str, Enum):
            RICH = "rich"
            JSON = "json"

        client = GmailClient()
        folders = client.get_folders()

        # Parse output format
        try:
            format_enum = OutputFormat(output_format.lower())
        except ValueError:
            console.print(f"[red]✗ Invalid output format: {output_format}. Use 'rich' or 'json'[/red]")
            raise typer.Exit(code=1)

        if format_enum == OutputFormat.JSON:
            console.print_json(data=[f.model_dump(mode='json') for f in folders])
        else:  # RICH
            formatter.print_folder_list(folders, "Gmail Labels")

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
