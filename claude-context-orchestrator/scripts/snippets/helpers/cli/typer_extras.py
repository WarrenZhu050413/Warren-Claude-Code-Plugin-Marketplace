"""Typer extensions and custom classes."""

import sys
from typing import Any

import click
import typer.core


class HelpfulGroup(typer.core.TyperGroup):
    """Typer group that shows help when no subcommand is provided.

    When a group command is invoked without a subcommand (e.g., 'snippets'
    instead of 'snippets list'), this displays the full help message
    instead of Click's default "Missing command" error.
    """

    def invoke(self, ctx: Any) -> Any:
        """Override to show help when no subcommand is provided."""
        # Check if this is a group invocation with no subcommand
        if ctx.protected_args + ctx.args == [] and ctx.invoked_subcommand is None:
            # Show help instead of "Missing command" error
            click.echo(ctx.get_help(), file=sys.stderr)
            ctx.exit(0)
        return super().invoke(ctx)
