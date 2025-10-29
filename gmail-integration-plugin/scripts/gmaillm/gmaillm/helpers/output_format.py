"""Shared output format utilities for CLI commands."""

from enum import Enum
import typer
from rich.console import Console


class OutputFormat(str, Enum):
    """Output format for CLI commands."""
    RICH = "rich"  # Rich terminal output (default)
    JSON = "json"  # Raw JSON output


def parse_output_format(format_str: str, console: Console) -> OutputFormat:
    """Parse and validate output format string.

    Args:
        format_str: The format string to parse (e.g., "rich" or "json")
        console: Rich console for error printing

    Returns:
        OutputFormat enum value

    Raises:
        typer.Exit: If format string is invalid
    """
    try:
        return OutputFormat(format_str.lower())
    except ValueError:
        console.print(f"[red]✗ Invalid output format: {format_str}. Use 'rich' or 'json'[/red]")
        raise typer.Exit(code=1)
