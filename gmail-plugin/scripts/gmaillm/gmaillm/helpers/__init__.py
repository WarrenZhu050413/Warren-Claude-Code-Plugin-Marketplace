"""Helper utilities for gmaillm CLI.

Organized into three layers:
- core: Low-level infrastructure (paths, I/O)
- domain: Business logic (groups, styles)
- cli: CLI-specific utilities (UI, interaction, validation)
"""

# Convenience re-exports of commonly used helpers
from gmaillm.helpers.cli import (
    HelpfulGroup,
    confirm_or_force,
    print_success,
    show_operation_preview,
)
from gmaillm.helpers.domain import expand_email_groups, load_email_groups

__all__ = [
    # Most commonly used helpers (for backward compatibility)
    "show_operation_preview",
    "print_success",
    "confirm_or_force",
    "HelpfulGroup",
    "load_email_groups",
    "expand_email_groups",
]
