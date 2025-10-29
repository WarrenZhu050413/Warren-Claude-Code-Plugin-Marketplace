"""Utility classes and functions for Typer CLI customization."""

import functools
from typing import Callable

import click
import typer


def help_on_missing_args(func: Callable) -> Callable:
    """Decorator that shows help when required arguments are missing.

    This wraps a Typer command function to catch MissingParameter exceptions
    and display the command's help text instead of showing an error.

    Args:
        func: The command function to wrap

    Returns:
        Wrapped function with help-on-missing-args behavior

    Example:
        @app.command()
        @help_on_missing_args
        def read(message_id: str):
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except click.MissingParameter as e:
            ctx = click.get_current_context()
            click.echo(ctx.get_help())
            ctx.exit(1)
    return wrapper


class HelpOnMissingArgsGroup(typer.core.TyperGroup):
    """Custom Typer group that shows help on missing arguments for all commands.

    This is a simpler alternative to the decorator approach. When used as the
    `cls` parameter for a Typer app, all commands in that app will automatically
    show help when required arguments are missing.

    Note: Due to Click's error handling, this approach has limitations. The decorator
    approach above may work better in some cases.
    """

    def add_command(self, cmd: click.Command, name: str = None):
        """Override add_command to wrap each command with help-on-missing-args."""
        if isinstance(cmd, click.Command):
            # Wrap the callback
            original_callback = cmd.callback
            if original_callback:
                @functools.wraps(original_callback)
                def new_callback(*args, **kwargs):
                    try:
                        return original_callback(*args, **kwargs)
                    except click.MissingParameter as e:
                        ctx = click.get_current_context()
                        click.echo(ctx.get_help())
                        ctx.exit(1)
                cmd.callback = new_callback
        return super().add_command(cmd, name)
