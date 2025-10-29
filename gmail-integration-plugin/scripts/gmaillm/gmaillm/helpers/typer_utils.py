"""Utility classes and functions for Typer CLI customization."""

import sys

import click
import typer


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
