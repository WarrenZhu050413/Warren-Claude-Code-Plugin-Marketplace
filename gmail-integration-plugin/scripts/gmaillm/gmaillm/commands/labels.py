"""Gmail labels management commands."""

import typer
from rich.console import Console

from gmaillm import GmailClient
from gmaillm.formatters import RichFormatter
from gmaillm.validators.email import validate_label_name

# Initialize Typer app and console
app = typer.Typer(help="Manage Gmail labels")
console = Console()
formatter = RichFormatter(console)


@app.command("list")
def list_labels() -> None:
    """List all labels (system and custom)."""
    try:
        client = GmailClient()
        folders = client.get_folders()
        formatter.print_folder_list(folders, "Gmail Labels")

    except Exception as e:
        console.print(f"[red]✗ Error listing labels: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("create")
def create_label(
    name: str = typer.Argument(..., help="Name of the label to create"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Create a new label/folder."""
    try:
        # Validate label name
        validate_label_name(name)

        client = GmailClient()

        # Show preview
        console.print("=" * 60)
        console.print("Creating Label")
        console.print("=" * 60)
        console.print(f"Name: {name}")
        console.print("=" * 60)

        # Confirm unless --force
        if not force:
            response = typer.confirm("\nCreate this label?")
            if not response:
                console.print("Cancelled.")
                return
        else:
            console.print("\n[yellow]--force: Creating without confirmation[/yellow]")

        # Create label
        label = client.create_label(name)

        console.print(f"\n[green]✅ Label created: {label.name}[/green]")
        console.print(f"   ID: {label.id}")

    except Exception as e:
        console.print(f"[red]✗ Error creating label: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("delete")
def delete_label(
    name: str = typer.Argument(..., help="Name of the label to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a label."""
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
        console.print("=" * 60)
        console.print("Deleting Label")
        console.print("=" * 60)
        console.print(f"Name: {name}")
        console.print(f"Type: {label.type}")
        if label.message_count:
            console.print(f"Messages: {label.message_count}")
        console.print("=" * 60)

        # Confirm unless --force
        if not force:
            response = typer.confirm("\n⚠️  Delete this label? This cannot be undone.")
            if not response:
                console.print("Cancelled.")
                return
        else:
            console.print("\n[yellow]--force: Deleting without confirmation[/yellow]")

        # Delete label using the Gmail API
        # Note: GmailClient needs a delete_label method added
        console.print(f"\n[yellow]⚠️  Label deletion not yet implemented in GmailClient[/yellow]")
        console.print("[yellow]   This will be added in a future update[/yellow]")
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]✗ Error deleting label: {e}[/red]")
        raise typer.Exit(code=1)
