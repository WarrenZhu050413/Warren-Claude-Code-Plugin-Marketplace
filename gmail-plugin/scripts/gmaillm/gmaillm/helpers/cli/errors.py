"""Error handling utilities for CLI commands."""

import typer
from rich.console import Console

console = Console()


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
