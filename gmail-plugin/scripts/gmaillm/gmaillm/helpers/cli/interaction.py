"""User interaction helpers for CLI commands."""

from pathlib import Path
from typing import Any, Callable, Dict, Optional

import typer
from rich.console import Console

console = Console()


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
        from gmaillm.helpers.core.io import create_backup
        create_backup_with_message(groups_file, create_backup)
    """
    if file_path.exists():
        backup_path = backup_func(file_path)
        console.print(f"Backup created: {backup_path}")
