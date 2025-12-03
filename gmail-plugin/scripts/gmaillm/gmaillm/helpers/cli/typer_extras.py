"""Typer customizations and utilities for CLI."""

import sys
from enum import Enum

import click
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


class HelpfulGroup(typer.core.TyperGroup):
    """Typer group that shows help when no subcommand is provided.

    When a group command is invoked without a subcommand (e.g., 'gmail styles'
    instead of 'gmail styles list'), this displays the full help message
    instead of Click's default "Missing command" error.

    Example:
        app = typer.Typer(cls=HelpfulGroup)

        @app.command()
        def list():
            # Running 'app' without 'list' will show help
            pass
    """

    def invoke(self, ctx):
        """Override to show help when no subcommand is provided."""
        # Check if this is a group invocation with no subcommand
        if ctx.protected_args + ctx.args == [] and ctx.invoked_subcommand is None:
            # Show help instead of "Missing command" error
            click.echo(ctx.get_help(), file=sys.stderr)
            ctx.exit(0)
        return super().invoke(ctx)
