"""CLI utilities for snippets management."""

from .colors import Colors
from .output import (
    console,
    display_schema_and_exit,
    format_table,
    print_error,
    print_info,
    print_success,
    print_warning,
    show_operation_preview,
)
from .typer_extras import HelpfulGroup
from .validation import (
    confirm_or_force,
    prompt_for_input,
    prompt_yes_no,
    validate_pattern,
    validate_snippet_name,
)

__all__ = [
    # Colors
    "Colors",
    # Output
    "console",
    "display_schema_and_exit",
    "format_table",
    "print_error",
    "print_info",
    "print_success",
    "print_warning",
    "show_operation_preview",
    # Typer extras
    "HelpfulGroup",
    # Validation
    "confirm_or_force",
    "prompt_for_input",
    "prompt_yes_no",
    "validate_pattern",
    "validate_snippet_name",
]
