"""Utility classes and functions for Typer CLI customization."""

import sys

import click
import typer


class HelpfulCommand(click.Command):
    """Command that shows help when invoked without required arguments.

    Overrides Click's exception formatting to show help text instead
    of the default error message when required parameters are missing.

    Usage:
        app = typer.Typer()
        app.command(cls=HelpfulCommand)(my_function)

        Or for a Typer group:
        app = typer.Typer(cls=HelpfulGroup)
    """

    def parse_args(self, ctx, args):
        """Override parse_args to intercept missing arguments."""
        try:
            return super().parse_args(ctx, args)
        except (click.MissingParameter, click.exceptions.UsageError) as e:
            # Show help instead of error
            click.echo(self.get_help(ctx), file=sys.stderr)
            ctx.exit(2)


class HelpfulGroup(typer.core.TyperGroup):
    """Typer group that uses HelpfulCommand for all commands.

    All commands in this group will show help when required arguments
    are missing, instead of showing Click's default error message.

    Also shows help when no subcommand is provided to a group.

    Example:
        app = typer.Typer(cls=HelpfulGroup)

        @app.command()
        def read(message_id: str):
            # Shows full help if message_id is missing
            pass
    """

    def invoke(self, ctx):
        """Override to show help when no subcommand is provided."""
        # Check if this is a group invocation with no subcommand
        if ctx.protected_args + ctx.args == [] and ctx.invoked_subcommand is None:
            # Show help instead of error
            click.echo(ctx.get_help(), file=sys.stderr)
            ctx.exit(0)
        return super().invoke(ctx)

    def command(self, *args, **kwargs):
        """Override to use HelpfulCommand as default command class."""
        kwargs.setdefault('cls', HelpfulCommand)
        return super().command(*args, **kwargs)

    def add_command(self, cmd: click.Command, name: str = None):
        """Override to convert existing commands to HelpfulCommand."""
        if isinstance(cmd, click.Command) and not isinstance(cmd, HelpfulCommand):
            # Convert the command to use HelpfulCommand's parse_args override
            original_parse_args = cmd.parse_args

            def new_parse_args(ctx, args):
                try:
                    return original_parse_args(ctx, args)
                except (click.MissingParameter, click.exceptions.UsageError) as e:
                    click.echo(cmd.get_help(ctx), file=sys.stderr)
                    ctx.exit(2)

            cmd.parse_args = new_parse_args

        return super().add_command(cmd, name)
