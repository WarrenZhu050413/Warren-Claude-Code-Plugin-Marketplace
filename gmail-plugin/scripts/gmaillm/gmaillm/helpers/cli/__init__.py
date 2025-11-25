"""CLI-specific utilities for gmaillm."""

from gmaillm.helpers.cli.errors import handle_command_error
from gmaillm.helpers.cli.interaction import (
    confirm_or_force,
    create_backup_with_message,
    ensure_item_exists,
)
from gmaillm.helpers.cli.typer_extras import (
    HelpfulGroup,
    OutputFormat,
    parse_output_format,
)
from gmaillm.helpers.cli.ui import print_success, show_operation_preview, output_json_or_rich
from gmaillm.helpers.cli.validation import display_schema_and_exit, load_and_validate_json

__all__ = [
    # UI
    "show_operation_preview",
    "print_success",
    "output_json_or_rich",
    # Interaction
    "confirm_or_force",
    "ensure_item_exists",
    "create_backup_with_message",
    # Error handling
    "handle_command_error",
    # Validation
    "load_and_validate_json",
    "display_schema_and_exit",
    # Typer extras
    "HelpfulGroup",
    "OutputFormat",
    "parse_output_format",
]
