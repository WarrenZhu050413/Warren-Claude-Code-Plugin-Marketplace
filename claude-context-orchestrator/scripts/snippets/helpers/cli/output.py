"""Output formatting utilities for CLI."""

from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()


def show_operation_preview(title: str, details: Dict[str, str]) -> None:
    """Show a preview of an operation before execution.

    Args:
        title: Title of the operation
        details: Dictionary of key-value pairs to display
    """
    console.print("=" * 60)
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.print("=" * 60)

    for key, value in details.items():
        console.print(f"[bold]{key}:[/bold] {value}")


def display_schema_and_exit(
    schema_getter: Any,
    title: str,
    description: str,
    usage_example: str
) -> None:
    """Display JSON schema and exit.

    Args:
        schema_getter: Function that returns schema string
        title: Title for the schema display
        description: Description of schema usage
        usage_example: Example command showing usage
    """
    schema_str = schema_getter()

    console.print()
    console.print(Panel(
        f"[cyan]{description}[/cyan]",
        title=f"📋 {title}",
        border_style="cyan"
    ))

    console.print("\n[bold]Schema:[/bold]")
    console.print(schema_str)

    console.print("\n[bold]Usage:[/bold]")
    console.print(f"  [cyan]{usage_example}[/cyan]")
    console.print()


def format_table(
    headers: List[str],
    rows: List[List[str]],
    title: str = None
) -> Table:
    """Format data as a Rich table.

    Args:
        headers: List of column headers
        rows: List of row data
        title: Optional table title

    Returns:
        Rich Table object
    """
    table = Table(title=title, show_header=True, header_style="bold cyan")

    for header in headers:
        table.add_column(header)

    for row in rows:
        table.add_row(*row)

    return table


def print_success(message: str) -> None:
    """Print success message with formatting.

    Args:
        message: Success message to print
    """
    console.print(f"[green]✅ {message}[/green]")


def print_error(message: str) -> None:
    """Print error message with formatting.

    Args:
        message: Error message to print
    """
    console.print(f"[red]✗ {message}[/red]")


def print_warning(message: str) -> None:
    """Print warning message with formatting.

    Args:
        message: Warning message to print
    """
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def print_info(message: str) -> None:
    """Print info message with formatting.

    Args:
        message: Info message to print
    """
    console.print(f"[cyan]ℹ  {message}[/cyan]")
