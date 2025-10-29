"""Utility classes and functions for Typer CLI customization."""

import sys

import click
import typer


class HelpfulCommand(click.Command):
    """Command that shows help when invoked without required arguments.

    Overrides Click's exception formatting to show help text instead
    of the default error message when required parameters are missing.

    This uses Click's built-in show_default mechanism which is called
    before sys.exit(), making it the most reliable approach.

    Usage:
        app = typer.Typer()
        app.command(cls=HelpfulCommand)(my_function)

        Or for a Typer group:
        app = typer.Typer(cls=HelpfulGroup)
    """

    def make_context(self, info_name, args, parent=None, **extra):
        """Override to customize error handling during context creation.

        Args:
            info_name: Command name
            args: Arguments list
            parent: Parent context
            **extra: Extra context parameters

        Returns:
            Click context with custom error handling
        """
        try:
            return super().make_context(info_name, args, parent, **extra)
        except click.MissingParameter as e:
            # Create a temporary context just to get help
            ctx = click.Context(self, info_name=info_name, parent=parent)
            click.echo(self.get_help(ctx), file=sys.stderr)
            # Re-raise to maintain normal exit behavior
            sys.exit(2)


class HelpfulGroup(typer.core.TyperGroup):
    """Typer group that uses HelpfulCommand for all commands.

    All commands in this group will show help when required arguments
    are missing, instead of showing Click's default error message.

    Example:
        app = typer.Typer(cls=HelpfulGroup)

        @app.command()
        def read(message_id: str):
            # Shows full help if message_id is missing
            pass
    """

    def command(self, *args, **kwargs):
        """Override to use HelpfulCommand as default command class."""
        kwargs.setdefault('cls', HelpfulCommand)
        return super().command(*args, **kwargs)

    def add_command(self, cmd: click.Command, name: str = None):
        """Override to convert existing commands to HelpfulCommand."""
        if isinstance(cmd, click.Command) and not isinstance(cmd, HelpfulCommand):
            # Convert the command to use HelpfulCommand's make_context
            original_make_context = cmd.make_context

            def new_make_context(info_name, args, parent=None, **extra):
                try:
                    return original_make_context(info_name, args, parent, **extra)
                except click.MissingParameter as e:
                    ctx = click.Context(cmd, info_name=info_name, parent=parent)
                    click.echo(cmd.get_help(ctx), file=sys.stderr)
                    sys.exit(2)

            cmd.make_context = new_make_context

        return super().add_command(cmd, name)
