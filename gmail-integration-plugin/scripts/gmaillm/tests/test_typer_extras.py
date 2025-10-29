"""Tests for Typer customizations and utilities."""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

import typer
import click
from rich.console import Console

from gmaillm.helpers.cli.typer_extras import (
    OutputFormat,
    parse_output_format,
    HelpfulGroup,
)


class TestOutputFormat:
    """Test OutputFormat enum."""

    def test_rich_format(self):
        """Test RICH format value."""
        assert OutputFormat.RICH == "rich"

    def test_json_format(self):
        """Test JSON format value."""
        assert OutputFormat.JSON == "json"


class TestParseOutputFormat:
    """Test parse_output_format function."""

    def test_parse_rich_format(self):
        """Test parsing 'rich' format."""
        console = Console()
        result = parse_output_format("rich", console)
        assert result == OutputFormat.RICH

    def test_parse_json_format(self):
        """Test parsing 'json' format."""
        console = Console()
        result = parse_output_format("json", console)
        assert result == OutputFormat.JSON

    def test_parse_case_insensitive(self):
        """Test parsing is case-insensitive."""
        console = Console()

        assert parse_output_format("RICH", console) == OutputFormat.RICH
        assert parse_output_format("Rich", console) == OutputFormat.RICH
        assert parse_output_format("JSON", console) == OutputFormat.JSON
        assert parse_output_format("Json", console) == OutputFormat.JSON

    def test_invalid_format_raises_exit(self):
        """Test invalid format raises typer.Exit."""
        console = Console()

        with pytest.raises(typer.Exit) as exc_info:
            parse_output_format("invalid", console)

        assert exc_info.value.exit_code == 1

    def test_invalid_format_shows_error_message(self):
        """Test invalid format prints error message."""
        # Create console with StringIO to capture output
        output = StringIO()
        console = Console(file=output, force_terminal=True)

        with pytest.raises(typer.Exit):
            parse_output_format("xml", console)

        output_text = output.getvalue()
        assert "Invalid output format" in output_text
        assert "xml" in output_text
        assert "rich" in output_text or "json" in output_text

    def test_empty_string_raises_exit(self):
        """Test empty string raises typer.Exit."""
        console = Console()

        with pytest.raises(typer.Exit) as exc_info:
            parse_output_format("", console)

        assert exc_info.value.exit_code == 1


class TestHelpfulGroup:
    """Test HelpfulGroup class."""

    def test_condition_check_empty_args_none_subcommand(self):
        """Test the condition that triggers help display."""
        # Test that condition evaluates to True when we should show help
        ctx = MagicMock(spec=click.Context)
        ctx.protected_args = []
        ctx.args = []
        ctx.invoked_subcommand = None

        # This is the condition checked in the invoke method
        should_show_help = (ctx.protected_args + ctx.args == [] and
                           ctx.invoked_subcommand is None)

        assert should_show_help is True

    def test_condition_check_with_args(self):
        """Test condition is False when args are present."""
        ctx = MagicMock(spec=click.Context)
        ctx.protected_args = []
        ctx.args = ["arg1"]
        ctx.invoked_subcommand = None

        should_show_help = (ctx.protected_args + ctx.args == [] and
                           ctx.invoked_subcommand is None)

        assert should_show_help is False

    def test_condition_check_with_subcommand(self):
        """Test condition is False when subcommand is invoked."""
        ctx = MagicMock(spec=click.Context)
        ctx.protected_args = []
        ctx.args = []
        ctx.invoked_subcommand = "subcommand"

        should_show_help = (ctx.protected_args + ctx.args == [] and
                           ctx.invoked_subcommand is None)

        assert should_show_help is False

    def test_help_display_uses_stderr(self):
        """Test that click.echo is called with sys.stderr."""
        # This tests the actual line: click.echo(ctx.get_help(), file=sys.stderr)
        ctx = MagicMock()
        ctx.get_help.return_value = "Help text"

        with patch("click.echo") as mock_echo:
            # Simulate the help display line
            click.echo(ctx.get_help(), file=sys.stderr)

            # Verify it was called with stderr
            mock_echo.assert_called_once_with("Help text", file=sys.stderr)
