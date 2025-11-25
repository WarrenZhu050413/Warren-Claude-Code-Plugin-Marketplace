"""CLI validation and confirmation utilities."""

import sys
from typing import Optional

from rich.console import Console

console = Console()


def confirm_or_force(
    prompt: str,
    force: bool,
    force_message: Optional[str] = None
) -> bool:
    """Confirm action with user or bypass if force flag is set.

    Args:
        prompt: Confirmation prompt to show user
        force: If True, bypass confirmation
        force_message: Optional message to show when forcing (default: "Forcing...")

    Returns:
        True if confirmed or forced, False otherwise
    """
    if force:
        if force_message:
            console.print(f"[yellow]{force_message}[/yellow]")
        return True

    response = console.input(f"{prompt} [dim](yes/no)[/dim]: ").strip().lower()
    return response in ("yes", "y")


def validate_pattern(pattern: str) -> bool:
    """Validate a regex pattern.

    Args:
        pattern: Regex pattern to validate

    Returns:
        True if valid, False otherwise
    """
    import re

    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def validate_snippet_name(name: str) -> bool:
    """Validate a snippet name.

    Snippet names should:
    - Not be empty
    - Not contain slashes or backslashes
    - Not start with a dot

    Args:
        name: Snippet name to validate

    Returns:
        True if valid, False otherwise
    """
    if not name:
        return False

    if "/" in name or "\\" in name:
        return False

    if name.startswith("."):
        return False

    return True


def prompt_for_input(
    prompt: str,
    default: Optional[str] = None,
    required: bool = True,
    validator: Optional[callable] = None
) -> str:
    """Prompt user for input with validation.

    Args:
        prompt: Prompt message
        default: Default value if user presses Enter
        required: Whether input is required
        validator: Optional validation function

    Returns:
        User input string

    Raises:
        SystemExit: If user cancels (Ctrl+C) or validation fails repeatedly
    """
    default_text = f" [dim](default: {default})[/dim]" if default else ""
    required_text = " [red]*[/red]" if required else ""

    while True:
        try:
            value = console.input(f"{prompt}{required_text}{default_text}: ").strip()

            # Handle default
            if not value and default:
                value = default

            # Check required
            if required and not value:
                console.print("[red]This field is required[/red]")
                continue

            # Validate
            if validator and value:
                if not validator(value):
                    console.print("[red]Invalid input[/red]")
                    continue

            return value

        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled[/yellow]")
            sys.exit(1)


def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """Prompt user for yes/no confirmation.

    Args:
        prompt: Confirmation prompt
        default: Default value if user presses Enter

    Returns:
        True for yes, False for no
    """
    default_text = " [dim](Y/n)[/dim]" if default else " [dim](y/N)[/dim]"

    while True:
        try:
            response = console.input(f"{prompt}{default_text}: ").strip().lower()

            if not response:
                return default

            if response in ("yes", "y"):
                return True
            elif response in ("no", "n"):
                return False
            else:
                console.print("[red]Please enter 'yes' or 'no'[/red]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled[/yellow]")
            sys.exit(1)
