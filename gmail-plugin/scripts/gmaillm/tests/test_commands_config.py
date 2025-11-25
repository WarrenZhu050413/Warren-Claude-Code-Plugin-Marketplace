"""Tests for commands/config.py module."""

import pytest
from unittest.mock import patch, Mock
from pathlib import Path

from typer.testing import CliRunner

from gmaillm.commands.config import app


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner(env={"_TYPER_COMPLETE_TEST_DISABLE_SHELL_DETECTION": "1"})


class TestExamplesCommand:
    """Test 'config examples' command."""

    def test_examples_shows_usage(self, runner):
        """Test examples command shows usage information."""
        result = runner.invoke(app, ["examples"])

        assert result.exit_code == 0
        assert "Example Usage" in result.stdout
        assert "VIEWING CONFIGURATION" in result.stdout
        assert "COMMON TASKS" in result.stdout
        assert "gmail config show" in result.stdout


class TestShowCommand:
    """Test 'config show' command."""

    def test_show_command_exists(self, runner):
        """Test that show command exists and can be called."""
        # Just verify the command exists and doesn't crash on help
        result = runner.invoke(app, ["show", "--help"])
        assert result.exit_code == 0
        assert "Show configuration" in result.stdout or "configuration" in result.stdout.lower()

    def test_show_config_with_invalid_output_format(self, runner):
        """Test showing config with invalid output format."""
        result = runner.invoke(app, ["show", "--output-format", "xml"])

        assert result.exit_code == 1
        assert "Invalid output format" in result.stdout
