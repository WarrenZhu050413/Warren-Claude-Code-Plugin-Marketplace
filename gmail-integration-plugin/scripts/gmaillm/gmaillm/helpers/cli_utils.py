"""Shared utilities for CLI commands to reduce code duplication."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

import typer
from rich.console import Console

console = Console()


def show_operation_preview(
    title: str,
    details: Dict[str, Any],
    width: int = 60
) -> None:
    """Display a formatted preview box for operations.

    Args:
        title: Operation title (e.g., "Creating Email Group")
        details: Dictionary of field names to values to display
        width: Width of the separator line

    Example:
        show_operation_preview(
            "Creating Email Group",
            {
                "Name": "#team",
                "Members": 3,
                "Emails": ["user1@example.com", "user2@example.com"]
            }
        )
    """
    console.print("=" * width)
    console.print(title)
    console.print("=" * width)

    for key, value in details.items():
        if isinstance(value, list):
            console.print(f"{key}: {len(value)}")
            for item in value:
                console.print(f"  - {item}")
        else:
            console.print(f"{key}: {value}")

    console.print("=" * width)


def confirm_or_force(
    prompt: str,
    force: bool,
    force_message: Optional[str] = None
) -> bool:
    """Handle confirmation prompt with --force flag support.

    Args:
        prompt: Confirmation prompt to show user
        force: Whether --force flag is set
        force_message: Optional custom message when forcing (default: generic message)

    Returns:
        True if user confirmed or force=True, False if user cancelled

    Example:
        if not confirm_or_force("\\nCreate this group?", force):
            console.print("Cancelled.")
            return
    """
    if not force:
        response = typer.confirm(prompt)
        if not response:
            return False
    else:
        if force_message is None:
            force_message = "Proceeding without confirmation"
        console.print(f"\n[yellow]--force: {force_message}[/yellow]")

    return True


def handle_command_error(
    operation: str,
    exception: Exception,
    exit_code: int = 1
) -> None:
    """Display standardized error message and exit.

    Args:
        operation: Description of the operation that failed (e.g., "creating group")
        exception: The exception that was raised
        exit_code: Exit code to use (default: 1)

    Example:
        try:
            # ... operation ...
        except Exception as e:
            handle_command_error("creating group", e)
    """
    console.print(f"[red]✗ Error {operation}: {exception}[/red]")
    raise typer.Exit(code=exit_code)


def ensure_item_exists(
    item_name: str,
    collection: Dict[str, Any],
    item_type: str,
    list_command: str
) -> None:
    """Check if item exists in collection, show helpful error if not.

    Args:
        item_name: Name of the item to check
        collection: Dictionary/collection to check in
        item_type: Human-readable type name (e.g., "Group", "Label")
        list_command: Command to list available items (e.g., "gmail groups list")

    Raises:
        typer.Exit: If item doesn't exist

    Example:
        ensure_item_exists(
            group_name,
            groups,
            "Group",
            "gmail groups list"
        )
    """
    if item_name not in collection:
        console.print(f"[red]✗ {item_type} '{item_name}' not found[/red]")
        console.print(f"\nAvailable: [cyan]{list_command}[/cyan]")
        raise typer.Exit(code=1)


def create_backup_with_message(
    file_path: Path,
    backup_func: Callable[[Path], Path]
) -> None:
    """Create backup of file and display confirmation message.

    Args:
        file_path: Path to file to backup
        backup_func: Function that creates backup and returns backup path

    Example:
        from gmaillm.helpers.config import create_backup
        create_backup_with_message(groups_file, create_backup)
    """
    if file_path.exists():
        backup_path = backup_func(file_path)
        console.print(f"Backup created: {backup_path}")


def print_success(
    message: str,
    details: Optional[Dict[str, Any]] = None,
    next_steps: Optional[List[str]] = None
) -> None:
    """Display success message with optional details and next steps.

    Args:
        message: Main success message
        details: Optional dictionary of additional details to show
        next_steps: Optional list of suggested next steps

    Example:
        print_success(
            f"Group created: #{group_name}",
            {"Members": len(emails)},
            ["gmail send --to #{group_name} ..."]
        )
    """
    console.print(f"\n[green]✅ {message}[/green]")

    if details:
        for key, value in details.items():
            console.print(f"   {key}: {value}")

    if next_steps:
        console.print("\nNext steps:")
        for step in next_steps:
            console.print(f"  [cyan]{step}[/cyan]")
